#!/usr/bin/env python3
"""Build manifest.json for prep.py from the repo's own files.

Sources:
  datasets      curated subsets from docs/dataset-cards/README.md (core + optional lists);
                every URL / id must appear in its card (checked here, see EVIDENCE)
  pip           samples/*/requirements.txt, plus `pip install` names from integration-card Install rows
  docker        FROM lines of sample Dockerfiles, image: lines of compose files,
                `docker pull|run` images in integration cards, buildable sample images
  repos         integration cards ranked by inbound graph links in index/records.jsonl
  js            templates/demo-dashboard/fetch-vendor.sh
  tools/tiles   go-pmtiles release named in docs/integration-cards/protomaps__pmtiles.md

Stdlib only, no network. Run: python3 templates/offline-kit/build_manifest.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json")
CARDS = os.path.join(ROOT, "docs", "dataset-cards")
ICARDS = os.path.join(ROOT, "docs", "integration-cards")

TIERS = ("minimal", "standard", "full")
REPOS_MINIMAL = 10
REPOS_STANDARD = 40
GB = 10**9
MB = 10**6

# Default map area: the project-repo compose default ORIGIN (59.0,10.0), about 55 x 33 km.
DEFAULT_BBOX = "9.75,58.85,10.25,59.15"
DEFAULT_MAXZOOM = 14
PROTOMAPS_BUILD = "https://build.protomaps.com/{date}.pmtiles"

# Each dataset entry: card, tier, license (from the card / README table), files.
# File keys: method, url | id | record | bucket+prefix, dest, size (bytes or None), size_note,
# evidence (strings that must all appear in the card; they carry the URL or its parts).
DATASETS = [
    dict(id="euroc-vicon-room1", card="euroc-mav.md", tier="standard",
         license="personal non-commercial (ETH Research Collection deposit terms)",
         note="Host rate-limits (HTTP 429); prep.py fetches it alone with backoff.",
         files=[dict(method="http", dest="vicon_room1.zip", size=int(6.04 * GB), size_note="DSpace sizeBytes, rounded in card",
                     url="https://www.research-collection.ethz.ch/server/api/core/bitstreams/02ecda9a-298f-498b-970c-b7c44334d880/content",
                     evidence=["bitstreams/02ecda9a-298f-498b-970c-b7c44334d880/content"])]),
    dict(id="tumvi-room1-512", card="tum-vi.md", tier="standard", license="CC BY 4.0",
         files=[dict(method="http", dest="dataset-room1_512_16.tar", size=1707110400, size_note="HEAD",
                     url="https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/dataset-room1_512_16.tar",
                     md5_url="https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/dataset-room1_512_16.tar.md5",
                     evidence=["https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/dataset-room1_512_16.tar.md5"])]),
    dict(id="uzhfpv-indoor-forward-3", card="uzh-fpv.md", tier="minimal", license="CC BY-NC-SA 3.0",
         files=[dict(method="http", dest="indoor_forward_3_snapdragon_with_gt.zip", size=int(0.84 * GB), size_note="HEAD, rounded in card",
                     url="https://download.ifi.uzh.ch/rpg/web/datasets/uzh-fpv-newer-versions/v3/indoor_forward_3_snapdragon_with_gt.zip",
                     evidence=["B=https://download.ifi.uzh.ch/rpg/web/datasets/uzh-fpv-newer-versions/v3", "$B/indoor_forward_3_snapdragon_with_gt.zip"])]),
    dict(id="ntuviral-eee03", card="ntu-viral.md", tier="standard", license="CC BY-NC-SA 4.0",
         files=[dict(method="http", dest="eee_03.zip", size=1995367404, size_note="HEAD",
                     url="https://huggingface.co/datasets/Yuan-Shenghai/NTU-VIRAL-DATASET/resolve/main/sequences/eee_03.zip?download=true",
                     evidence=["HF=https://huggingface.co/datasets/Yuan-Shenghai/NTU-VIRAL-DATASET/resolve/main", "$HF/sequences/eee_03.zip?download=true"])]),
    dict(id="kitti-raw-0001", card="kitti.md", tier="standard", license="CC BY-NC-SA 3.0",
         files=[dict(method="http", dest=d, size=s, size_note=n, url="https://s3.eu-central-1.amazonaws.com/avg-kitti/" + p,
                     evidence=["B=https://s3.eu-central-1.amazonaws.com/avg-kitti", "$B/" + p])
                for p, d, s, n in [
                    ("data_odometry_poses.zip", "data_odometry_poses.zip", int(1.3 * MB), "HEAD"),
                    ("data_odometry_calib.zip", "data_odometry_calib.zip", int(0.6 * MB), "HEAD"),
                    ("raw_data/2011_09_26_calib.zip", "2011_09_26_calib.zip", None, "not stated"),
                    ("raw_data/2011_09_26_drive_0001/2011_09_26_drive_0001_sync.zip", "2011_09_26_drive_0001_sync.zip", 459 * MB, "HEAD"),
                    ("raw_data/2011_09_26_drive_0001/2011_09_26_drive_0001_extract.zip", "2011_09_26_drive_0001_extract.zip", 697 * MB, "HEAD"),
                ]]),
    dict(id="urbannav-tokyo-medium-urban1", card="urbannav.md", tier="standard", license="MIT (covers the data, per README)",
         files=[dict(method="http", dest="Tokyo_Data.zip", size=int(4.45 * GB), size_note="HEAD",
                     url="https://www.dropbox.com/s/isu1bugpgr8dpas/Tokyo_Data.zip?dl=1",
                     evidence=["https://www.dropbox.com/s/isu1bugpgr8dpas/Tokyo_Data.zip?dl=1"]),
                dict(method="http", dest="UrbanNav_TST_GT_raw.txt", size=140 * 10**3, size_note="HEAD",
                     url="https://www.dropbox.com/s/twsvwftucoytfpc/UrbanNav_TST_GT_raw.txt?dl=1",
                     evidence=["https://www.dropbox.com/s/twsvwftucoytfpc/UrbanNav_TST_GT_raw.txt?dl=1"]),
                dict(method="http", dest="xsense_imu_medium_urban1.csv", size=110 * MB, size_note="HEAD",
                     url="https://www.dropbox.com/s/2rh1rs15ihpf63u/xsense_imu_medium_urban1.csv?dl=1",
                     evidence=["https://www.dropbox.com/s/2rh1rs15ihpf63u/xsense_imu_medium_urban1.csv?dl=1"])]),
    dict(id="boreas-radar-gt-calib", card="boreas.md", tier="standard", license="CC BY 4.0",
         files=[dict(method="s3prefix", endpoint="https://boreas.s3.amazonaws.com", prefix="boreas-2020-11-26-13-58/",
                     include=["radar/", "applanix/", "calib/"], dest="boreas-2020-11-26-13-58",
                     size=int(3.04 * GB), size_note="sum of S3 listing folder sizes in card (radar 2.75 + applanix 0.29 GB)",
                     evidence=["S=boreas-2020-11-26-13-58", "https://boreas.s3.amazonaws.com/$S", '--include "radar/*"'])]),
    dict(id="nclt-2012-01-08", card="nclt.md", tier="minimal", license="ODbL + DbCL",
         files=[dict(method="http", dest=p.split("/")[-1], size=s, size_note=n,
                     url="https://s3.us-east-2.amazonaws.com/nclt.perl.engin.umich.edu/" + p,
                     evidence=["B=https://s3.us-east-2.amazonaws.com/nclt.perl.engin.umich.edu", "D=2012-01-08", ev])
                for p, s, n, ev in [
                    ("sensor_data/2012-01-08_sen.tar.gz", 119 * MB, "HEAD", "$B/sensor_data/${D}_sen.tar.gz"),
                    ("ground_truth/groundtruth_2012-01-08.csv", 116 * MB, "HEAD", "$B/ground_truth/groundtruth_${D}.csv"),
                    ("covariance/cov_2012-01-08.csv", None, "not stated", "$B/covariance/cov_${D}.csv"),
                ]]),
    dict(id="gsdc-taroz-2023", card="gsdc.md", tier="standard", license="Kaggle competition rules",
         files=[dict(method="http", dest="dataset_2023.zip", size=2761355999, size_note="HEAD",
                     url="http://www.taroz.net/data/dataset_2023.zip", evidence=["http://www.taroz.net/data/dataset_2023.zip"])]),
    dict(id="texbat-cleanstatic80-ds3proc", card="texbat.md", tier="standard",
         license="UT research use; do not redistribute (share inside the team only after reading the terms)",
         files=[dict(method="http", dest="cleanStatic80.bin", size=8016392192, size_note="HEAD",
                     url="https://rnl-data.ae.utexas.edu/datastore/texbat/cleanStatic80.bin",
                     evidence=["B=https://rnl-data.ae.utexas.edu/datastore/texbat", "cleanStatic80.bin = 8,016,392,192 bytes"]),
                dict(method="httpdir", url="https://rnl-data.ae.utexas.edu/datastore/texbat/processed/ds3/", dest="processed/ds3",
                     size=int(0.8 * GB), size_note="directory listing, approximate",
                     evidence=["$B/processed/ds3/"])]),
    dict(id="jammertest-vaara", card="jammertest-data.md", tier="standard", license="none stated (no LICENSE in repo)",
         files=[dict(method="git", url="https://github.com/UniVaasaDigiEco/VAARA", dest="VAARA", size=int(1.57 * GB),
                     size_note="git tree blob sizes, uncompressed", evidence=["https://github.com/UniVaasaDigiEco/VAARA"])]),
    dict(id="jammertest-fraunhofer-chunk", card="jammertest-data.md", tier="standard", license="CC BY-NC-SA 4.0",
         note="Git LFS bandwidth quota on GitHub can block pulls; fetch early.",
         files=[dict(method="lfs", repo="FelixOtt94/FraunhoferIIS_Jammertest2025", ref="master",
                     path="dataset/Sample_Area1_0000000_0024999.h5.part-" + s, dest="Sample_Area1_0000000_0024999.h5.part-" + s,
                     size=1992294400 if s == "aa" else None, size_note="HEAD" if s == "aa" else "from LFS pointer at fetch time",
                     evidence=["https://github.com/FelixOtt94/FraunhoferIIS_Jammertest2025", 'dataset/Sample_Area1_0000000_0024999.h5.part-*'])
                for s in ("aa", "ab")]),
    dict(id="jammertest-npra-plan", card="jammertest-data.md", tier="full", license="MIT",
         files=[dict(method="git", url="https://github.com/NPRA/jammertest-plan", dest="jammertest-plan", size=None,
                     size_note="Testcatalog.pdf 92 MB + small JSON; repo total not stated", evidence=["https://github.com/NPRA/jammertest-plan"])]),
    dict(id="s7am1na-sample", card="gnss-spoofing-s7am1na.md", tier="minimal", license="MIT",
         note="Format sample only, not a labelled attack (card).",
         files=[dict(method="http", dest="gnss_log_2025_07_30_10_15_12.txt", size=23678435, size_note="HEAD",
                     url="https://raw.githubusercontent.com/S7AM1NA/GNSS-Spoofing-Dataset/main/sample/gnss_log_2025_07_30_10_15_12.txt",
                     evidence=["https://raw.githubusercontent.com/S7AM1NA/GNSS-Spoofing-Dataset/main/sample/gnss_log_2025_07_30_10_15_12.txt"])]),
    dict(id="magnav-zenodo-12723700", card="magnav-challenge-data.md", tier="standard",
         license="public domain per LICENSE.md, plus an Air Force use agreement (non-profit research/education/government, no redistribution)",
         files=[dict(method="zenodo", record="12723700", dest=".", size=int(1.16 * GB), size_note="Zenodo API",
                     evidence=["Z=https://zenodo.org/api/records/12723700/files"])]),
    dict(id="magnav-ottawa-maps", card="magnav-challenge-data.md", tier="standard", license="as MagNav.jl artifacts",
         files=[dict(method="manual", dest="ottawa_area_maps_v3.tar.gz", size=int(710.5 * MB), size_note="Dropbox HEAD per card",
                     instructions="URL is in MagNav.jl Artifacts.toml, not in this repo. Easiest: run samples/magnav-quickstart once online "
                                  "(julia:1.11 image) and keep ~/.julia/artifacts.",
                     evidence=["ottawa_area_maps_v3.tar.gz"])]),
    dict(id="afit-magnav-example", card="afit-magnav-example-data.md", tier="minimal", license="none stated; sources carry their own terms",
         files=[dict(method="http", dest=p.split("/")[-1], size=s, size_note=n,
                     url="https://github.com/AFIT-EENG-MagNav/example-data/raw/refs/heads/main/" + p,
                     evidence=["R=https://github.com/AFIT-EENG-MagNav/example-data/raw/refs/heads/main", "$R/" + p])
                for p, s, n in [("mit-aia/aia-maps.zip", 98562784, "HEAD"),
                                ("mit-aia/flight1002/10Hz_Mag_INS_Aux_Flt1002.xyz.zip", int(72.2 * MB), "git tree"),
                                ("namad/USMAG_origmrg.gxf.zip", int(41.8 * MB), "git tree"),
                                ("geodesy/geoids/egm2008-2_5.pgm.zip", int(64.2 * MB), "git tree")]]),
    dict(id="util-uwb-tdoa", card="util-uwb-tdoa.md", tier="standard", license="not stated",
         files=[dict(method="http", dest="dataset.7z", size=1861803968, size_note="GitHub releases API",
                     url="https://github.com/utiasDSL/util-uwb-dataset/releases/download/dataset-v1.0/dataset.7z",
                     evidence=["https://github.com/utiasDSL/util-uwb-dataset/releases/download/dataset-v1.0/dataset.7z"])]),
    dict(id="miluv-default-3-random-0", card="miluv.md", tier="standard", license="CC BY 4.0 (data), MIT (devkit)",
         files=[dict(method="http", dest="default_3_random_0.zip", size=int(3.2 * GB), size_note="figshare API, rounded in card",
                     url="https://ndownloader.figshare.com/files/52291625", evidence=["https://ndownloader.figshare.com/files/52291625"])]),
    dict(id="uav-visloc-example", card="uav-visloc.md", tier="standard", license="not stated; ask before redistribution",
         files=[dict(method="gdrive", id="16tY7tPZiNIoyAhknvyXnp0jAfccIcHtL", dest="UAV_VisLoc_example.zip", size=int(2.04 * GB),
                     size_note="README", evidence=["16tY7tPZiNIoyAhknvyXnp0jAfccIcHtL"])]),
    dict(id="vpair-sample", card="vpair.md", tier="standard", license="academic use only (README; stricter than the Zenodo CC BY tag)",
         files=[dict(method="http", dest="vpair_sample.zip", size=861249439, size_note="Zenodo API",
                     url="https://zenodo.org/records/6473989/files/vpair_sample.zip?download=1",
                     evidence=["https://zenodo.org/records/6473989/files/vpair_sample.zip?download=1"])]),
    dict(id="pohang00-navigation", card="maritime-datasets.md", tier="minimal", license="CC BY-NC 4.0",
         files=[dict(method="http", dest="navigation.zip", size=21 * MB, size_note="S3 listing, approximate",
                     url="https://pohang-canal-dataset.s3.amazonaws.com/pohang00/navigation.zip",
                     evidence=["https://pohang-canal-dataset.s3.amazonaws.com/pohang00/navigation.zip"])]),
    dict(id="pohang00-radar", card="maritime-datasets.md", tier="standard", license="CC BY-NC 4.0",
         files=[dict(method="http", dest="radar.zip", size=int(0.2 * GB), size_note="S3 listing, approximate",
                     url="https://pohang-canal-dataset.s3.amazonaws.com/pohang00/radar.zip",
                     evidence=["s3://pohang-canal-dataset/pohang00/radar.zip", "https://pohang-canal-dataset.s3.amazonaws.com/pohang00/"])]),
    dict(id="massmind", card="maritime-datasets.md", tier="standard", license="CC BY-NC-SA 4.0",
         files=[dict(method="gdrive", id=i, dest=d, size=s, size_note="Drive page", evidence=[i])
                for i, d, s in [("1T572f0oqy5JmuTvVEwkSUeXLWOSHl4hL", "MassMIND_Images.zip", 414 * MB),
                                ("1pHp480_Q-s72RoDf1nD7ERzsv9yZTDE1", "Segmentation_Masks.zip", 7 * MB),
                                ("16rPWhV8OEocyLLpT1-LSCALt757P_h0N", "InstanceSegmentation_Masks.zip", 7 * MB)]]),
    dict(id="anti-uav300", card="anti-uav.md", tier="standard", license="data terms not stated",
         files=[dict(method="gdrive", id="1NPYaop35ocVTYWHOYQQHn8YHsM9jmLGr", dest="Anti-UAV-RGBT.zip", size=int(5.6 * GB),
                     size_note="card", evidence=["1NPYaop35ocVTYWHOYQQHn8YHsM9jmLGr"])]),
    dict(id="dronerf", card="drone-rf-datasets.md", tier="standard", license="CC BY 4.0",
         files=[dict(method="mendeley", dataset="f4c2b4n755", dest=".", size=int(4.03 * GB), size_note="Mendeley API",
                     evidence=["https://data.mendeley.com/public-api/datasets/f4c2b4n755"])]),
    dict(id="remote-id-captures", card="remote-id-droneid-captures.md", tier="minimal",
         license="DroneSecurity AGPL-3.0; opendroneid wireshark-dissector Apache-2.0",
         files=[dict(method="git", url="https://github.com/RUB-SysSec/DroneSecurity", dest="DroneSecurity", size=None,
                     size_note="samples 7.6 MB; repo total not stated", evidence=["https://github.com/RUB-SysSec/DroneSecurity"]),
                dict(method="git", url="https://github.com/opendroneid/wireshark-dissector", dest="wireshark-dissector", size=None,
                     size_note="pcaps under 0.1 MB; repo total not stated", evidence=["https://github.com/opendroneid/wireshark-dissector"])]),
    # optional list
    dict(id="gvins-complex-environment", card="gvins.md", tier="full", license="CC BY-NC-SA 4.0",
         files=[dict(method="http", dest="complex_environment.bag", size=int(17.3 * GB), size_note="HF API",
                     url="https://huggingface.co/datasets/Shawn202606/GVINS-Dataset/resolve/main/complex_environment.bag",
                     evidence=["B=https://huggingface.co/datasets/Shawn202606/GVINS-Dataset/resolve/main", "$B/complex_environment.bag"]),
                dict(method="http", dest="checksum.txt", size=None, size_note="not stated",
                     url="https://huggingface.co/datasets/Shawn202606/GVINS-Dataset/resolve/main/checksum.txt",
                     evidence=["$B/checksum.txt"])]),
    dict(id="denseuav", card="denseuav.md", tier="full", license="repo Apache-2.0 / HF card MIT; imagery terms unscoped",
         files=[dict(method="http", dest="DenseUAV.zip", size=int(16.7 * GB), size_note="card",
                     url="https://huggingface.co/datasets/Dmmm997/DenseUAV/resolve/main/DenseUAV.zip",
                     evidence=["https://huggingface.co/datasets/Dmmm997/DenseUAV/resolve/main/DenseUAV.zip"])]),
    dict(id="hilti22-exp14", card="hilti-slam.md", tier="full", license="CC BY-NC-SA 3.0",
         files=[dict(method="http", dest=p.split("/")[-1], size=s, size_note=n,
                     url="https://huggingface.co/datasets/Hilti-Research/hilti-slam-challenge-2022/resolve/main/" + p,
                     evidence=["HF=https://huggingface.co/datasets/Hilti-Research/hilti-slam-challenge-2022/resolve/main", "$HF/" + p])
                for p, s, n in [("rosbags/exp14_basement_2.bag", int(6.26 * GB), "card"),
                                ("ground_truth/exp14_basement_2_imu.txt", None, "not stated")]]),
    dict(id="sues-200", card="sues-200.md", tier="full", license="academic research only (README)",
         files=[dict(method="gdrive", id="1UyVyFJ_pRaJHIr_eBY2HL7gkS5y9UxqI", dest="SUES-200-512x512-V2.zip", size=int(5.3 * GB),
                     size_note="card", evidence=["1UyVyFJ_pRaJHIr_eBY2HL7gkS5y9UxqI"])]),
    dict(id="subpipe-mini2", card="underwater-datasets.md", tier="full", license="CC BY 4.0",
         files=[dict(method="http", dest="SubPipeMini2.zip", size=int(4.9 * GB), size_note="card",
                     url="https://zenodo.org/records/12666132/files/SubPipeMini2.zip?download=1",
                     evidence=["https://zenodo.org/records/12666132/files/SubPipeMini2.zip?download=1"])]),
    dict(id="newer-college-math-easy", card="newer-college.md", tier="full", license="CC BY-NC-SA 4.0",
         files=[dict(method="http", dest="2021-04-07-13-52-31_1-math-easy.bag", size=int(1.84 * GB), size_note="card",
                     url="https://huggingface.co/datasets/ori-drs/newer_college_dataset/resolve/main/2021-ouster-os0-128-alphasense/"
                         "collection%203%20-%20maths%20institute/2021-04-07-13-52-31_1-math-easy.bag",
                     evidence=["HF=https://huggingface.co/datasets/ori-drs/newer_college_dataset/resolve/main",
                               "$HF/2021-ouster-os0-128-alphasense/collection%203%20-%20maths%20institute/2021-04-07-13-52-31_1-math-easy.bag"])]),
    dict(id="tartanair-one-env", card="tartanair.md", tier="full", license="CC BY 4.0 (site) vs BSD-3 (HF), unresolved",
         files=[dict(method="manual", dest="tartanair", size=int(1.06 * GB), size_note="card",
                     instructions="Script-driven: git clone https://github.com/castacks/tartanair_tools and run download_training.py "
                                  "with --rgb --only-left after filtering download_training_zipfiles.txt to one env (see card).",
                     evidence=["https://github.com/castacks/tartanair_tools"])]),
]

# Sample data fetched by a sample's own script (run from the repo checkout).
SCRIPTS = [
    dict(id="gnss-rinex-processing-data", tier="minimal", path="samples/gnss-rinex-processing/fetch_data.sh",
         size=int(3.6 * MB), size_note="stated in script header", license="NOAA NGS CORS public data",
         outputs="samples/gnss-rinex-processing/data/"),
]


def tier_index(t):
    return TIERS.index(t)


def card_text(name):
    with open(os.path.join(CARDS, name), encoding="utf-8") as f:
        return f.read()


def check_evidence(ds):
    text = card_text(ds["card"])
    missing = [e for f in ds["files"] for e in f["evidence"] if e not in text]
    return missing


def parse_requirements(path):
    """Return (binary-capable lines, vcs lines). Comments and blanks dropped."""
    reqs, vcs = [], []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.split(" #")[0].strip()
            if not line or line.startswith("#"):
                continue
            (vcs if "git+" in line or line.startswith(("http://", "https://")) else reqs).append(line)
    return reqs, vcs


PIP_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(\[[A-Za-z0-9_,.-]+\])?([=<>!~]=?[A-Za-z0-9.*]+)?$")


def parse_card_pip(text):
    """Plain PyPI requirement tokens from `pip install ...` in a card's Install row."""
    out = []
    for row in re.findall(r"^\| Install \|(.*)$", text, re.M):
        for cmd in re.findall(r"pip install ([^`|;&]+)", row):
            toks, i = cmd.split(), 0
            while i < len(toks):
                tok = toks[i].strip("\"'")
                i += 1
                if tok in ("-r", "-e", "--editable", "-c", "--index-url", "--extra-index-url"):
                    break
                if tok.startswith("-"):
                    continue
                if "/" in tok or "$" in tok or tok == "." or tok.endswith((".txt", ".whl")):
                    break
                if PIP_TOKEN.match(tok) and tok not in out:
                    out.append(tok)
    return out


IMAGE_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._/-]*(:[A-Za-z0-9._-]+)?$")


def parse_dockerfile_from(path):
    images, stages = [], set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?", line, re.I)
            if m:
                img = m.group(1)
                if img not in stages and "$" not in img:
                    images.append(img)
                if m.group(2):
                    stages.add(m.group(2))
    return images


def parse_compose_images(path):
    with open(path, encoding="utf-8") as f:
        return [m for m in re.findall(r"^\s*image:\s*(\S+)", f.read(), re.M) if "$" not in m]


FLAGS_WITH_VALUE = {"-p", "-v", "-w", "-e", "--name", "--platform", "--network", "--entrypoint", "-u"}


def parse_card_docker(text):
    """Image named by each `docker pull|run` command (first non-flag token)."""
    out = []
    for m in re.finditer(r"docker (?:pull|run)\s+([^`\n|&]+)", text):
        toks, i = m.group(1).split(), 0
        while i < len(toks):
            tok = toks[i]
            if tok.startswith("-"):
                i += 2 if tok in FLAGS_WITH_VALUE else 1
                continue
            if IMAGE_TOKEN.match(tok) and ("/" in tok or ":" in tok) and tok not in out:
                out.append(tok)
            break
    return out


def parse_fetch_vendor(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    base = re.search(r'curl[^"]*"(https://[^"$]+)\$1"', text).group(1)
    return [(base + src, dst) for src, dst in re.findall(r'"([^"\s]+@[^"\s]+) ([^"\s]+)"', text)]


def load_records():
    with open(os.path.join(ROOT, "index", "records.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def rank_repos(records):
    """Integration-card repos, ordered by (high fit, inbound graph links, stars)."""
    inbound = {}
    for r in records:
        for rel in r.get("related") or []:
            inbound[rel["id"]] = inbound.get(rel["id"], 0) + 1
    by_id = {r["id"].lower(): r for r in records if r["kind"] == "repo"}
    rows = []
    for card in sorted(glob.glob(os.path.join(ICARDS, "*__*.md"))):
        owner, name = os.path.basename(card)[:-3].split("__", 1)
        rec = by_id.get(f"repo:{owner}/{name}")
        if not rec:
            continue
        gh = rec.get("github") or {}
        rows.append(((rec.get("hackathon_fit") == "high", inbound.get(rec["id"], 0), gh.get("stargazers_count") or 0), rec))
    rows.sort(key=lambda r: r[0], reverse=True)
    return [r for _, r in rows]


def build():
    rel = lambda p: os.path.relpath(p, ROOT)
    items = []

    for ds in DATASETS:
        missing = check_evidence(ds)
        if missing:
            sys.exit(f"{ds['id']}: evidence not found in {ds['card']}: {missing}")
        files = [dict(f) for f in ds["files"]]
        known = [f["size"] for f in files if f.get("size") is not None]
        items.append(dict(id="dataset:" + ds["id"], type="dataset", tier=ds["tier"], license=ds["license"],
                          source=f"docs/dataset-cards/{ds['card']}", note=ds.get("note", ""), files=files,
                          size=sum(known) if known else None, size_complete=len(known) == len(files)))
    for s in SCRIPTS:
        items.append(dict(id="script:" + s["id"], type="script", tier=s["tier"], license=s["license"], source=s["path"],
                          path=s["path"], outputs=s["outputs"], size=s["size"], size_complete=True, note=s["size_note"]))

    minimal_reqs = {"mavlink-to-tak-cot", "gnss-ins-ekf-outage", "gnss-interference-monitor"}
    for req in sorted(glob.glob(os.path.join(ROOT, "samples", "*", "requirements*.txt"))):
        sample = os.path.basename(os.path.dirname(req))
        reqs, vcs = parse_requirements(req)
        if not reqs and not vcs:
            continue
        items.append(dict(id="pip:" + sample, type="pip", tier="minimal" if sample in minimal_reqs else "standard",
                          license="per package (see PyPI metadata)", source=rel(req), requirements=reqs, vcs=vcs,
                          size=None, size_complete=False))
    card_pip, card_pip_src = [], []
    for card in sorted(glob.glob(os.path.join(ICARDS, "*__*.md"))):
        with open(card, encoding="utf-8") as f:
            toks = parse_card_pip(f.read())
        for t in toks:
            if t not in card_pip:
                card_pip.append(t)
        if toks:
            card_pip_src.append(rel(card))
    items.append(dict(id="pip:integration-cards", type="pip", tier="full", license="per package",
                      source=f"Install rows of {len(card_pip_src)} integration cards", requirements=card_pip, vcs=[],
                      size=None, size_complete=False, each=True,
                      note="unpinned names, fetched one by one; resolve against your Python before the event"))

    images = {}

    def add_image(img, src, tier):
        cur = images.get(img)
        if cur is None or tier_index(tier) < tier_index(cur["tier"]):
            images[img] = dict(tier=tier, sources=(cur or {}).get("sources", []) + [src])
        elif src not in cur["sources"]:
            cur["sources"].append(src)

    builds = []
    for df in sorted(glob.glob(os.path.join(ROOT, "samples", "**", "Dockerfile*"), recursive=True)):
        for img in parse_dockerfile_from(df):
            add_image(img, rel(df), "minimal" if img.startswith("python:") else "standard")
    for cf in sorted(glob.glob(os.path.join(ROOT, "templates", "*", "docker-compose.yml")) +
                     glob.glob(os.path.join(ROOT, "samples", "*", "compose.yaml"))):
        text = open(cf, encoding="utf-8").read()
        for svc in re.finditer(r"^  (\w[\w-]*):\n((?:    .*\n|\n)+)", text, re.M):
            body = svc.group(2)
            img = re.search(r"^\s*image:\s*(\S+)", body, re.M)
            if not img or "$" in img.group(1):
                continue
            if "build:" in body:
                dockerfile = re.search(r"dockerfile:\s*(\S+)", body)
                builds.append(dict(image=img.group(1), context=rel(os.path.dirname(cf)),
                                   dockerfile=dockerfile.group(1) if dockerfile else "Dockerfile", source=rel(cf)))
            else:
                add_image(img.group(1), rel(cf), "minimal")
    for script in sorted(glob.glob(os.path.join(ROOT, "samples", "*", "*.sh"))):
        text = open(script, encoding="utf-8").read()
        m = re.search(r"^IMAGE=(\S+)", text, re.M)
        if m and re.search(r'docker build -t "\$IMAGE" (\S+)', text):
            ctx = re.search(r'docker build -t "\$IMAGE" (\S+)', text).group(1)
            builds.append(dict(image=m.group(1), context=rel(os.path.join(os.path.dirname(script), ctx)),
                               dockerfile="Dockerfile", source=rel(script)))
    for card in sorted(glob.glob(os.path.join(ICARDS, "*__*.md"))):
        for img in parse_card_docker(open(card, encoding="utf-8").read()):
            add_image(img, rel(card), "full")
    for img, meta in sorted(images.items()):
        items.append(dict(id="docker:" + img, type="docker", tier=meta["tier"], image=img, platforms=["linux/amd64", "linux/arm64"],
                          license="per image", source=", ".join(meta["sources"]), size=None, size_complete=False,
                          note="unpinned tag; pin a digest you tested" if img.endswith((":latest",)) or ":" not in img else ""))
    seen_builds = set()
    for b in builds:
        # Several samples reuse one image by tag; the first parsed build (sorted order) owns its context.
        if b["image"] in seen_builds or '"' in b["context"] or "$" in b["context"]:
            continue
        seen_builds.add(b["image"])
        items.append(dict(id="docker-build:" + b["image"], type="docker-build", tier="standard", image=b["image"],
                          context=b["context"], dockerfile=b["dockerfile"], license="per Dockerfile contents", source=b["source"],
                          size=None, size_complete=False, note="needs network at build time; build and save the week before"))

    for i, rec in enumerate(rank_repos(load_records())):
        tier = "minimal" if i < REPOS_MINIMAL else "standard" if i < REPOS_STANDARD else "full"
        gh = rec.get("github") or {}
        items.append(dict(id="git:" + rec["id"][5:], type="git", tier=tier, url=rec["url"], rank=i + 1,
                          license=gh.get("license") or "not stated", source=f"docs/integration-cards/{rec['id'][5:].replace('/', '__')}.md",
                          size=None, size_complete=False))

    fv = os.path.join(ROOT, "templates", "demo-dashboard", "fetch-vendor.sh")
    for url, dst in parse_fetch_vendor(fv):
        lic = {"maplibre": "BSD-3-Clause", "milsymbol": "MIT", "pmtiles": "BSD-3-Clause"}
        items.append(dict(id="js:" + dst, type="js", tier="minimal", url=url, dest=dst,
                          license=next((v for k, v in lic.items() if k in url), "not stated"),
                          source=rel(fv), size=None, size_complete=False,
                          note="copy into templates/demo-dashboard/vendor/"))

    pm_card = open(os.path.join(ICARDS, "protomaps__pmtiles.md"), encoding="utf-8").read()
    version = re.search(r"latest (v\d+\.\d+\.\d+)", pm_card).group(1)
    items.append(dict(id="tool:pmtiles", type="tool", tier="minimal", repo="protomaps/go-pmtiles", tag=version,
                      assets={"darwin-arm64": "Darwin_arm64", "linux-amd64": "Linux_x86_64", "linux-arm64": "Linux_arm64",
                              "darwin-amd64": "Darwin_x86_64"},
                      license="BSD-3-Clause", source="docs/integration-cards/protomaps__pmtiles.md", size=None, size_complete=False))
    items.append(dict(id="tiles:basemap", type="tiles", tier="standard", source_url=PROTOMAPS_BUILD, bbox=DEFAULT_BBOX,
                      maxzoom=DEFAULT_MAXZOOM, dest="basemap.pmtiles",
                      license="Protomaps basemap: ODbL (OpenStreetMap data), attribution required",
                      source="templates/demo-dashboard/README.md (Offline), docs/integration-cards/protomaps__pmtiles.md",
                      size=None, size_complete=False,
                      note="override --bbox for the venue; size from `pmtiles extract --dry-run` (prep.py --probe)"))

    return dict(version=1, generated_by="templates/offline-kit/build_manifest.py", tiers=list(TIERS),
                pip_platforms={"linux-amd64": ["manylinux_2_28_x86_64", "manylinux2014_x86_64"],
                               "linux-arm64": ["manylinux_2_28_aarch64", "manylinux2014_aarch64"],
                               "macos-arm64": ["macosx_14_0_arm64"]},
                python_version="3.12", items=items)


def main():
    manifest = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
        f.write("\n")
    counts = {}
    for it in manifest["items"]:
        counts[it["type"]] = counts.get(it["type"], 0) + 1
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(manifest['items'])} items {counts}")


if __name__ == "__main__":
    main()
