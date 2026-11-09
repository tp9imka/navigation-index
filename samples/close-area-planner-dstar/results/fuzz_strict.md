`python compare.py fuzz --trials 300 --strict` (strict textbook key test; synthetic random 20 x 20 grids, 30 incremental plans per trial, path cost D* Lite vs A* from scratch, tolerance 1e-6 relative)

| start moves | cells flip blocked | costs change | trials | failing trials |
|---|---|---|---|---|
| False | False | True | 300 | 50 |
| False | True | False | 300 | 43 |
| False | True | True | 300 | 62 |
| True | False | True | 300 | 1 |
| True | True | False | 300 | 11 |
| True | True | True | 300 | 9 |
