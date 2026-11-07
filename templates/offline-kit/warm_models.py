#!/usr/bin/env python3
"""Online warm-up for exactly the vision bundle's models; uses TORCH_HOME from bundle.py."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.repo) / 'samples' / 'vpr-large-area'))
    from lightglue import ALIKED, LightGlue
    import torch
    from vpr import DINOV2_REPO, Dinov2Describer

    Dinov2Describer(device='cpu')
    ALIKED(max_num_keypoints=2048).eval()
    LightGlue(features='aliked').eval()
    print(json.dumps(dict(dinov2_source=DINOV2_REPO, torch_home=str(Path(torch.hub.get_dir()).parent),
                          models=['dinov2_vits14', 'aliked-n16', 'aliked_lightglue'])))


if __name__ == '__main__':
    main()
