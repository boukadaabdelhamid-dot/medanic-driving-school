"""
keygen_tool.py  —  أداة توليد مفاتيح الترخيص (للمطوّر فقط)
=============================================================
هذا الملف مخصص لك أنت فقط — لا تُرسله للمستخدمين.

الاستخدام:
1. شغّل هذا الملف:  python keygen_tool.py
2. أدخل HWID الذي أرسله لك المستخدم من نافذة التفعيل.
3. انسخ المفتاح الناتج وأرسله للمستخدم.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from license_guard import generate_key, _get_hwid


class KeygenWindow(tk.Tk):

    FONT_TITLE = ("Arial", 16, "bold")
    FONT_BODY  = ("Arial", 10)
    FONT_MONO  = ("Courier New", 13, "bold")
    COLOR_BG   = "#0f172a"
    COLOR_CARD = "#1e293b"
    COLOR_PRI  = "#3b82f6"
    COLOR_GRN  = "#22c55e"
    COLOR_TXT  = "#f1f5f9"
    COLOR_MUTED= "#94a3b8"

    def __init__(self):
        super().__init__()
        self.title("مولّد مفاتيح الترخيص — ميدانيك  [للمطوّر فقط]")
        self.geometry("560x460")
        self.resizable(False, False)
        self.configure(bg=self.COLOR_BG)
        self._build()

    def _build(self):
        # ── رأس ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=self.COLOR_PRI, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔑  مولّد مفاتيح الترخيص",
                 font=self.FONT_TITLE, bg=self.COLOR_PRI, fg="white").pack()
        tk.Label(hdr, text="هذه الأداة للمطوّر فقط — لا تُوزَّع مع البرنامج",
                 font=("Arial", 9), bg=self.COLOR_PRI, fg="#bfdbfe").pack()

        body = tk.Frame(self, bg=self.COLOR_BG, padx=35, pady=25)
        body.pack(fill="both", expand=True)

        # ── HWID الجهاز الحالي ───────────────────────────────────────────
        tk.Label(body, text="HWID جهازك الحالي (للاختبار):",
                 font=self.FONT_BODY, bg=self.COLOR_BG, fg=self.COLOR_MUTED).pack(anchor="w")

        my_hwid = _get_hwid()
        my_fr = tk.Frame(body, bg=self.COLOR_CARD, pady=6, padx=10)
        my_fr.pack(fill="x", pady=(4, 20))
        tk.Label(my_fr, text=my_hwid, font=self.FONT_MONO,
                 bg=self.COLOR_CARD, fg=self.COLOR_PRI).pack(side="left")
        tk.Button(my_fr, text="📋", font=("Arial", 9),
                  bg=self.COLOR_CARD, fg=self.COLOR_MUTED,
                  relief="flat", cursor="hand2", bd=0,
                  command=lambda: self._copy(my_hwid)).pack(side="right")

        # ── إدخال HWID المستخدم ──────────────────────────────────────────
        tk.Label(body, text="أدخل HWID المستخدم:",
                 font=("Arial", 10, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TXT).pack(anchor="w")

        inp_fr = tk.Frame(body, bg=self.COLOR_CARD, pady=6, padx=10)
        inp_fr.pack(fill="x", pady=(4, 16))
        self._hwid_var = tk.StringVar()
        tk.Entry(inp_fr, textvariable=self._hwid_var,
                 font=self.FONT_MONO, bg=self.COLOR_CARD, fg=self.COLOR_TXT,
                 insertbackground=self.COLOR_TXT,
                 relief="flat", bd=0).pack(fill="x")

        tk.Button(body, text="⚡  توليد المفتاح",
                  font=("Arial", 11, "bold"),
                  bg=self.COLOR_PRI, fg="white",
                  activebackground="#2563eb",
                  relief="flat", cursor="hand2", bd=0, padx=20, pady=10,
                  command=self._generate).pack(fill="x", pady=(0, 20))

        # ── المفتاح الناتج ───────────────────────────────────────────────
        tk.Label(body, text="المفتاح الناتج — أرسله للمستخدم:",
                 font=("Arial", 10, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TXT).pack(anchor="w")

        res_fr = tk.Frame(body, bg=self.COLOR_CARD, pady=12, padx=10,
                          highlightthickness=2, highlightbackground=self.COLOR_GRN)
        res_fr.pack(fill="x", pady=(4, 12))
        self._key_var = tk.StringVar(value="—")
        tk.Label(res_fr, textvariable=self._key_var,
                 font=("Courier New", 15, "bold"),
                 bg=self.COLOR_CARD, fg=self.COLOR_GRN).pack(side="left")

        tk.Button(body, text="📋  نسخ المفتاح",
                  font=self.FONT_BODY,
                  bg=self.COLOR_CARD, fg=self.COLOR_GRN,
                  relief="flat", cursor="hand2", bd=0, padx=10, pady=6,
                  command=lambda: self._copy(self._key_var.get())).pack(anchor="e")

        # تنبيه
        tk.Label(body,
                 text="⚠  لا تُعطِ هذا الملف للمستخدمين — احتفظ به لنفسك.",
                 font=("Arial", 8), bg=self.COLOR_BG, fg="#f59e0b").pack(side="bottom")

    def _generate(self):
        hwid = self._hwid_var.get().strip().upper()
        if len(hwid) != 16 or not hwid.isalnum():
            messagebox.showerror("خطأ", "HWID يجب أن يكون 16 حرفاً أحرف وأرقام فقط.", parent=self)
            return
        key = generate_key(hwid)
        self._key_var.set(key)

    def _copy(self, text: str):
        if text in ("", "—"):
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("تم النسخ", "تم نسخ النص إلى الحافظة.", parent=self)


if __name__ == "__main__":
    KeygenWindow().mainloop()
