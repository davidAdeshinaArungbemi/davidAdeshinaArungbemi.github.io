"""Three design directions for the site, each as a working homepage, a topic page and an article.

Run from the repo root:
  python3 _directions/build.py            build every direction that exists, then the chooser page
  python3 _directions/build.py b          build only direction B (letters a, b, c, d, or "chooser")
Then serve the repo root and open /_directions/. The folder name starts with "_", so GitHub Pages
would not publish it even if it were merged.
"""
import importlib, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import kit                                             # noqa: E402

if __name__ == "__main__":
    want = sys.argv[1:] or ["a", "b", "c", "d", "chooser"]
    data = kit.gather()
    for name in want:
        module = "chooser" if name == "chooser" else f"dir_{name}"
        if not (HERE / f"{module}.py").exists():
            print(f"skipped {name}: there is no {module}.py yet")
            continue
        importlib.import_module(module).build(data)
        print(f"built {name}")
