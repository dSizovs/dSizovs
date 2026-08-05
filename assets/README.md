`about.yml` is the play. `render_run.py` draws it as an animated SVG of that
play executing — SMIL timing, so it plays inside a README via a plain `<img>`.

```bash
python3 render_run.py
```

Two knobs at the top of `render_run.py`:

- `THESIS_DUE` — the countdown target, printed as Ansible's retry line
- `ECTS_DONE` / `ECTS_TOTAL` — bump to 90/90 once the credits are in

`.github/workflows/refresh.yml` re-renders daily so the countdown stays honest.
