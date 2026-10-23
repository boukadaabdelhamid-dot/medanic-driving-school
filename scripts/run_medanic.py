"""Launch the unchanged desktop app with Replit's Nix Tk extension available."""

import glob
from pathlib import Path
import runpy
import sys


def main():
    try:
        import _tkinter  # noqa: F401
    except ModuleNotFoundError:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        candidates = glob.glob(
            f"/nix/store/*-python{version}-tkinter-*/lib/"
            f"python{version}/site-packages"
        )
        if not candidates:
            raise SystemExit(
                "Tkinter is missing. Install the matching python Tkinter "
                "system dependency in Replit before starting Medanic."
            )
        sys.path[:0] = sorted(candidates)
        import _tkinter  # noqa: F401

    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    runpy.run_path(str(root / "driving_school_single.py"), run_name="__main__")


if __name__ == "__main__":
    main()
