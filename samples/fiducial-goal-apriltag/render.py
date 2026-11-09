"""Synthetic pinhole camera images of a tag36h11 AprilTag on a textured wall, at known poses.

Camera model (no lens distortion): 640 x 480 px, fx = fy = 500 px, cx = 319.5, cy = 239.5
=> horizontal FOV 65.2 deg, vertical FOV 51.3 deg.

Frames follow the AprilTag pose convention used by pupil-apriltags:
- tag frame: origin at the tag centre, x right, y down (as printed), z into the wall;
  the outward normal (towards a viewer) is -z.
- camera frame: x right, y down, z along the optical axis.
- a pose (R, t) maps tag points into the camera frame: X_cam = R @ X_tag + t.

tag_size is the edge of the black border square (8 of the 10 cells), as the detector expects.
"""
import math

import cv2
import numpy as np

W, H = 640, 480
FX = FY = 500.0
CX, CY = (W - 1) / 2.0, (H - 1) / 2.0
K = np.array([[FX, 0, CX], [0, FY, CY], [0, 0, 1.0]])
TAG_SIZE = 0.16          # m, black border edge (fits on an A4 sheet)
TAG_ID = 7
BLACK, WHITE = 25.0, 220.0   # rendered intensities of ink and paper (8-bit)

HFOV_DEG = math.degrees(2 * math.atan(W / 2 / FX))
VFOV_DEG = math.degrees(2 * math.atan(H / 2 / FY))


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def look_at_pose(cam_pos_tag, target_tag=(0.0, 0.0, 0.0)):
    """Level camera (its y axis = tag y = down) at cam_pos_tag looking at target_tag.
    Returns (R, t) mapping tag points into the camera frame."""
    c = np.asarray(cam_pos_tag, float)
    z = np.asarray(target_tag, float) - c
    z /= np.linalg.norm(z)
    down = np.array([0.0, 1.0, 0.0])
    x = np.cross(down, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R_tc = np.column_stack([x, y, z])      # camera axes expressed in the tag frame
    R = R_tc.T
    return R, -R @ c


def heading_of(R):
    """Yaw of the tag's outward normal seen from the camera, rad, about the camera y (down) axis.
    0 = the camera looks straight at the tag face. This is the tag-relative heading a
    wall-tag approach uses (for a floor pad with a down camera it is the same quantity
    after the fixed mount rotation)."""
    n = R @ np.array([0.0, 0.0, -1.0])
    return math.atan2(n[0], -n[2])


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def _tag_texture(tag_id, px_per_cell=64):
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    code = cv2.aruco.generateImageMarker(d, tag_id, 8 * px_per_cell, borderBits=1)
    tex = np.full((12 * px_per_cell, 12 * px_per_cell), 255, np.uint8)   # 2-cell white margin
    tex[2 * px_per_cell:10 * px_per_cell, 2 * px_per_cell:10 * px_per_cell] = code
    return tex


def _wall_texture(rng, n=2048):
    """Mid-grey wall with smooth blotches and some random dark and light rectangles (clutter edges)."""
    low = rng.uniform(0, 1, (48, 48)).astype(np.float32)
    tex = cv2.resize(low, (n, n), interpolation=cv2.INTER_CUBIC)
    tex = 90 + 70 * (tex - tex.min()) / (np.ptp(tex) + 1e-9)
    for _ in range(60):
        x0, y0 = rng.integers(0, n - 50, 2)
        w, h = rng.integers(20, 200, 2)
        tex[y0:y0 + h, x0:x0 + w] = rng.uniform(40, 200)
    tex += rng.normal(0, 6, tex.shape)
    return np.clip(tex, 0, 255).astype(np.float32)


class Renderer:
    def __init__(self, tag_id=TAG_ID, tag_size=TAG_SIZE, supersample=3, wall_seed=12345,
                 wall_extent_m=12.0):
        self.tag_id, self.tag_size, self.ss = tag_id, tag_size, supersample
        self.tag_tex = _tag_texture(tag_id).astype(np.float32) / 255.0
        self.tag_tex = BLACK + (WHITE - BLACK) * self.tag_tex
        self.tag_mask = np.ones_like(self.tag_tex)
        self.wall_tex = _wall_texture(np.random.default_rng(wall_seed))
        # texture pixel => tag-plane metres
        n_tag = self.tag_tex.shape[0]
        m_tag = 1.5 * tag_size / n_tag                     # 12 cells span 1.5 * tag_size
        self.A_tag = np.array([[m_tag, 0, -0.75 * tag_size + m_tag / 2],
                               [0, m_tag, -0.75 * tag_size + m_tag / 2], [0, 0, 1]])
        n_wall = self.wall_tex.shape[0]
        m_wall = wall_extent_m / n_wall
        self.A_wall = np.array([[m_wall, 0, -wall_extent_m / 2], [0, m_wall, -wall_extent_m / 2], [0, 0, 1]])
        s = self.ss
        self.K_ss = np.array([[FX * s, 0, (CX + 0.5) * s - 0.5], [0, FY * s, (CY + 0.5) * s - 0.5], [0, 0, 1]])
        u, v = np.meshgrid(np.arange(W * s, dtype=np.float32), np.arange(H * s, dtype=np.float32))
        self._uv1 = np.stack([u, v, np.ones_like(u)], -1)

    def render(self, R, t, rng=None, blur_px=0.0, noise_dn=0.0):
        """8-bit grey image of the tag at pose (R, t). blur_px: Gaussian blur sigma in output
        pixels (defocus / motion stand-in). noise_dn: Gaussian read noise sigma in 8-bit DN."""
        s = self.ss
        Hp = self.K_ss @ np.column_stack([R[:, 0], R[:, 1], t])   # tag plane (x, y, 1) => image
        size = (W * s, H * s)
        wall = cv2.warpPerspective(self.wall_tex, Hp @ self.A_wall, size, flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_REFLECT)
        tag = cv2.warpPerspective(self.tag_tex, Hp @ self.A_tag, size, flags=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        mask = cv2.warpPerspective(self.tag_mask, Hp @ self.A_tag, size, flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # pixels whose ray misses the wall (above the horizon, or behind) see a flat far background
        n = R[:, 2]                                   # wall normal in the camera frame
        nd = self._uv1 @ (np.linalg.inv(self.K_ss).T @ n)   # n . ray direction, per pixel
        hits = nd * float(n @ t) > 0                  # ray parameter (n.t)/(n.d) is positive
        img = np.where(hits, mask * tag + (1 - mask) * wall, 150.0).astype(np.float32)
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        if blur_px > 0:
            img = cv2.GaussianBlur(img, (0, 0), blur_px)
        if noise_dn > 0:
            rng = rng if rng is not None else np.random.default_rng()
            img = img + rng.normal(0, noise_dn, img.shape)
        return np.clip(np.rint(img), 0, 255).astype(np.uint8)


def project(R, t, pts_tag):
    pc = (R @ np.asarray(pts_tag, float).T).T + t
    uv = (K @ pc.T).T
    return uv[:, :2] / uv[:, 2:3], pc[:, 2]


def tag_corners(tag_size=TAG_SIZE):
    h = tag_size / 2
    return np.array([[-h, -h, 0], [h, -h, 0], [h, h, 0], [-h, h, 0]])
