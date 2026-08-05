`about.yml` is the source. `render.py` regenerates the SVGs from it:

```bash
python3 render.py
```

The PNGs are 2x screenshots of those SVGs, taken with headless Chrome so the
card doesn't depend on the viewer having SF Mono or Menlo installed:

```bash
chrome --headless=new --force-device-scale-factor=2 --window-size=669,986 \
  --default-background-color=00000000 \
  --screenshot=about-dark.png file://$PWD/about-dark.svg
```
