# Ghidra-ReAGS Quick Start

A beginner-friendly tutorial for Windows users: extract Adventure Game Studio (AGS) game scripts with [AGSUnpacker](https://github.com/adm244/AGSUnpacker), open them in [Ghidra 10.4](https://ghidra-sre.org/) with the [ReAGS](https://github.com/adm244/Ghidra-ReAGS) extension, and export pseudo-C decompilation output.

**Live site:** [selloa.github.io/ghidra-reags-quickstart](https://selloa.github.io/ghidra-reags-quickstart/)

Community tutorial — not affiliated with the NSA Ghidra team or the ReAGS/AGSUnpacker author.

## Repository layout

| Path | Purpose |
|------|---------|
| `tutorial.md` | Source of truth — edit this |
| `build.py` | Builds `index.html` from `tutorial.md` |
| `index.html` | Published tutorial page |
| `assets/tutorial.css` | Page styling (MarkView-derived) |
| `media/` | Tutorial screenshots (`step-NN-*.png`) |

## Build locally

Requires Python 3:

```powershell
pip install -r requirements.txt
python build.py
```

Open `index.html` in a browser to preview.

After editing `tutorial.md`, bump `version` and `date` in the YAML front matter, run `python build.py`, then commit both `tutorial.md` and `index.html`.

## GitHub Pages

This site is deployed from the **`main`** branch at the repo root (`index.html` + `assets/` + `media/`).

No build step runs on GitHub — regenerate `index.html` locally before pushing content changes.

## Status

Early draft (tutorial v0.1.0). ReAGS is an unfinished plugin; the guide paraphrases the official project README for known issues.

## License

Tutorial text and screenshots: specify a license when you are ready to publish. Third-party tools (Ghidra, AGSUnpacker, ReAGS) remain under their respective licenses.
