`about.yml` is the play. `render_run.py` draws it as an animated SVG of that
play executing — SMIL timing, so it plays inside a README via a plain `<img>`.

```bash
python3 render_run.py
```

Two knobs at the top of `render_run.py`:

- `THESIS_DUE` — the countdown target, printed as Ansible's retry line
- `ECTS_DONE` / `ECTS_TOTAL` — bump to 90/90 once the credits are in

Nothing re-renders on its own — run the script again whenever the countdown has
drifted far enough to bother you, and commit the two SVGs.
