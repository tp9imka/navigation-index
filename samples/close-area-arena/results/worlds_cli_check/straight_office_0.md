`python run.py --planner straight --layouts 2 --family office --out results/worlds_cli_check` (synthetic), wall 0.2 s

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m |
|---|---|---|---|---|---|---|---|---|
| straight | office | 2 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.325 |

| run | obstacles | outcome | time to goal s | min clearance m | path m |
|---|---|---|---|---|---|
| 0 | 28 | stuck | - | 0.3729 | 0.856 |
| 1 | 18 | stuck | - | 0.2777 | 2.929 |
