Narrow_gap reach check (synthetic), run 2026-11-09 after kill_e_narrow_gap, output to stdout only.

Why: every arm in `kill_e_narrow_gap_summary_1.md` reached 0 of 50 layouts in every case. This
checks whether the range barrier F2 (eps = 0.7 m, shared by F3, F4, F5) closes the gap itself.

```sh
.venv/bin/python -c "
import run_kill as k, collections
c=collections.Counter(k.run_one('F0','truth',True,i,1,family='narrow_gap')['outcome'] for i in range(10)); print('F0 truth narrow_gap 10:',c)
c=collections.Counter(k.run_one('F2','truth',True,i,1,family='narrow_gap')['outcome'] for i in range(10)); print('F2 truth narrow_gap 10:',c)
"
```

Output (layouts 0-9, seed 1, unsensed on, truth pose):

```
F0 truth narrow_gap 10: Counter({'reached': 10})
F2 truth narrow_gap 10: Counter({'stuck': 10})
```

So with a perfect pose, no filter reaches 10 of 10 and F2 alone reaches 0 of 10. The arena gap is
0.5-0.9 m wide (world.py `narrow_gap`), below the about 1.4 m that F2's 0.7 m range barrier leaves
open for a 0.15 m radius vehicle. Reach on this family measures F2's parameters, not the map
margins.
