---
name: Desktop setup constraints
description: Scope decision and Replit-specific Tkinter packaging behavior.
---

Keep the imported Medanic app as a Python desktop application unless the user
explicitly requests a conversion.

**Why:** The user chose to get the imported project running on Replit, not to
rebuild it as a website.

**How to apply:** Use a VNC workflow and preserve the original licensing and
SQLite storage behavior.

Installing the Nix Tkinter package alone may not expose its compiled extension
to the Python environment created by Replit's dependency installer.

**Why:** The interpreter could find the standard-library tkinter module but
failed to import `_tkinter` even after the matching system dependency was installed.

**How to apply:** Check the compiled extension's importability, not just whether
`find_spec("tkinter")` succeeds. Expose the matching Nix site-packages path through
any launcher or headless wrapper that imports the desktop module; do not modify the
product's source or bypass Tk.
