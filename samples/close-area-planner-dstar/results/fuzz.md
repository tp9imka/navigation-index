`python compare.py fuzz --trials 300` (KEY_EPS 1e-9 tie tolerance; synthetic random 20 x 20 grids, 30 incremental plans per trial, path cost D* Lite vs A* from scratch, tolerance 1e-6 relative)

| start moves | cells flip blocked | costs change | trials | failing trials |
|---|---|---|---|---|
| False | False | True | 300 | 0 |
| False | True | False | 300 | 0 |
| False | True | True | 300 | 0 |
| True | False | True | 300 | 0 |
| True | True | False | 300 | 0 |
| True | True | True | 300 | 0 |
