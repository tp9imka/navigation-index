"""SGM (STGL, Xiao et al. IROS 2023) thermal => satellite retrieval as a coarse localizer.

Rebuilds the network the demo branch of arplaboratory/satellite-thermal-geo-localization
instantiates (ResNet-50 up to conv4 + L2 + GeM + FC 4096 + L2) with torchvision, and loads
xjh19972/SGM model.safetensors from Hugging Face. Code is MIT; the weights card states no
license and the model was trained on the Boson-nighttime set, which is gated "non-commercial
research only". Treat the weights as research-only.

Retrieval: the query (north-up, centre square) is compared against satellite squares of the
same ground size on a grid around the prior; the best L2 match gives the position.
"""
import math
import time

import cv2
import numpy as np
import torch
import torchvision
from torch import nn

from geom import haversine_m

HF_REPO = "xjh19972/SGM"
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
QUERY_CONTRAST = 3.0
BATCH = 32
DISTINCT_EXCLUSION_M = 40.0


class GeM(nn.Module):
    def __init__(self, p=3.0, eps=1e-6):
        super().__init__()
        self.p = nn.Parameter(torch.ones(1) * p)
        self.eps = eps

    def forward(self, x):
        return nn.functional.avg_pool2d(x.clamp(min=self.eps).pow(self.p), (x.size(-2), x.size(-1))).pow(1.0 / self.p)


class L2Norm(nn.Module):
    def forward(self, x):
        return nn.functional.normalize(x, p=2, dim=1)


class SGM(nn.Module):
    def __init__(self):
        super().__init__()
        r = torchvision.models.resnet50(weights=None)
        self.backbone = nn.Sequential(*list(r.children())[:-3])
        self.aggregation = nn.Sequential(nn.Sequential(L2Norm(), GeM(), nn.Flatten()),
                                         nn.Linear(1024, 4096), L2Norm())

    def forward(self, x):
        return self.aggregation(self.backbone(x))


def load_sgm(device="cpu"):
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file
    path = hf_hub_download(HF_REPO, "model.safetensors")
    sd = load_file(path)
    sd = {k.replace("module.", ""): v for k, v in sd.items()}
    model = SGM()
    model.load_state_dict(sd)
    return model.eval().to(device)


def adjust_contrast(gray, factor):
    """torchvision adjust_contrast on a grayscale image: blend with its mean."""
    mean = gray.astype(np.float32).mean()
    return np.clip((gray.astype(np.float32) - mean) * factor + mean, 0, 255).astype(np.uint8)


def to_batch(grays, size, device):
    arr = np.stack([cv2.resize(g, (size, size), interpolation=cv2.INTER_AREA) for g in grays])
    t = torch.from_numpy(arr).float().div(255.0)[:, None].repeat(1, 3, 1, 1)
    return ((t - MEAN) / STD).to(device)


class SGMLocalizer:
    def __init__(self, device="cpu", input_px=512, square_m=110.0, stride_m=15.0):
        self.device = torch.device(device)
        self.model = load_sgm(self.device)
        self.input_px = input_px
        self.square_m = square_m
        self.stride_m = stride_m

    @torch.inference_mode()
    def embed(self, grays):
        out = []
        for i in range(0, len(grays), BATCH):
            out.append(self.model(to_batch(grays[i:i + BATCH], self.input_px, self.device)).cpu())
        return torch.cat(out)

    def localize(self, thermal_gray, frame_gsd, heading_deg, ortho, prior_lonlat, search_radius_m,
                 truth_latlon=None):
        from thermal_geoloc import north_up
        t0 = time.perf_counter()
        gsd = ortho.gsd
        q, _, qc = north_up(thermal_gray, frame_gsd, heading_deg, gsd)
        side = int(round(self.square_m / gsd))
        cx, cy = int(round(qc[0])), int(round(qc[1]))
        q = q[cy - side // 2: cy - side // 2 + side, cx - side // 2: cx - side // 2 + side]
        q = adjust_contrast(q, QUERY_CONTRAST)

        half = search_radius_m + self.square_m / 2
        ref, c0, r0, k = ortho.window(*prior_lonlat, half, gsd)
        step = max(1, int(round(self.stride_m / gsd)))
        centres, patches = [], []
        for y in range(side // 2, ref.shape[0] - side // 2, step):
            for x in range(side // 2, ref.shape[1] - side // 2, step):
                patches.append(ref[y - side // 2: y - side // 2 + side, x - side // 2: x - side // 2 + side])
                centres.append((x, y))
        qf = self.embed([q])
        df = self.embed(patches)
        d = torch.cdist(qf, df).squeeze(0).numpy()
        best = int(d.argmin())
        x, y = centres[best]
        lon, lat = ortho.world_to_lonlat(*(ortho.transform * (c0 + (x + 0.5) / k, r0 + (y + 0.5) / k)))
        far = [d[i] for i, (xx, yy) in enumerate(centres)
               if math.hypot(xx - x, yy - y) * gsd > DISTINCT_EXCLUSION_M]
        margin = (min(far) / d[best]) if far else float("inf")
        # no geometric verification exists for a retrieval hit: every top-1 counts as a fix
        res = {"features": "sgm", "preproc": f"sgm{self.input_px}", "accepted": True, "reasons": [], "fix": (lat, lon), "dist": float(d[best]),
               "margin": float(margin), "n_db": len(patches), "err_m": None,
               "t_total_s": round(time.perf_counter() - t0, 3)}
        if truth_latlon is not None:
            res["err_m"] = haversine_m(truth_latlon[0], truth_latlon[1], lat, lon)
        return res
