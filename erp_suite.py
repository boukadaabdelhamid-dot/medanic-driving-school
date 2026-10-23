"""Additive finance and HR modules for Medanic.

All ERP records live in their own prefixed SQLite tables. Nothing in this
module alters the legacy app's records, reports, or administrative documents.
"""

from datetime import date
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


COLORS = {
    "bg": "#F8FAFC",
    "card": "#FFFFFF",
    "text": "#1E293B",
    "muted": "#64748B",
    "border": "#E2E8F0",
    "primary": "#4F46E5",
    "green": "#059669",
    "red": "#DC2626",
}

TRANSLATIONS = {
    "title": {"ar": "الموارد المالية والبشرية", "fr": "Finance & ressources humaines"},
    "subtitle": {
        "ar": "وحدات إضافية مستقلة — بيانات المدرسة الحالية ووثائقها لم تتغير.",
        "fr": "Modules complémentaires — données et documents existants inchangés.",
    },
    "journal": {"ar": "المحاسبة", "fr": "Comptabilité"},
    "accounts": {"ar": "دليل الحسابات", "fr": "Plan comptable"},
    "employees": {"ar": "الموظفون", "fr": "Employés"},
    "payroll": {"ar": "الرواتب", "fr": "Paie"},
    "income": {"ar": "إيراد", "fr": "Recette"},
    "expense": {"ar": "مصروف", "fr": "Dépense"},
    "date": {"ar": "التاريخ", "fr": "Date"},
    "btn_save": {"ar": "حفظ", "fr": "Enregistrer"},
    "btn_cancel": {"ar": "إلغاء", "fr": "Annuler"},
    "kind": {"ar": "النوع", "fr": "Type"},
    "settlement": {"ar": "الصندوق / البنك", "fr": "Caisse / Banque"},
    "category": {"ar": "حساب الإيراد / المصروف", "fr": "Compte produit / charge"},
    "amount": {"ar": "المبلغ (دج)", "fr": "Montant (DA)"},
    "reference": {"ar": "المرجع", "fr": "Référence"},
    "description": {"ar": "البيان", "fr": "Description"},
    "add_entry": {"ar": "تسجيل قيد", "fr": "Ajouter une écriture"},
    "reverse": {"ar": "عكس القيد المحدد", "fr": "Contrepasser l'écriture"},
    "confirm_reverse": {
        "ar": "سيُنشأ قيد عكسي جديد مع الاحتفاظ بالقيد الأصلي. متابعة؟",
        "fr": "Une écriture inverse sera créée sans supprimer l'original. Continuer ?",
    },
    "code": {"ar": "الرمز", "fr": "Code"},
    "name": {"ar": "اسم الحساب", "fr": "Nom du compte"},
    "account_type": {"ar": "تصنيف الحساب", "fr": "Type de compte"},
    "new_account": {"ar": "إضافة حساب", "fr": "Ajouter un compte"},
    "name_required": {"ar": "الاسم مطلوب.", "fr": "Le nom est obligatoire."},
    "code_required": {"ar": "رمز الحساب مطلوب.", "fr": "Le code du compte est obligatoire."},
    "account_invalid": {"ar": "اختر حسابًا مناسبًا للتصنيف المحدد.", "fr": "Choisissez un compte compatible avec le type."},
    "no_selection": {"ar": "حدد سجلًا أولًا.", "fr": "Sélectionnez d'abord une ligne."},
    "saved": {"ar": "تم الحفظ بنجاح.", "fr": "Enregistré."},
    "invalid_amount": {"ar": "أدخل مبلغًا أكبر من صفر.", "fr": "Saisissez un montant supérieur à zéro."},
    "ledger_header": {"ar": "دفتر القيود المحاسبية", "fr": "Journal comptable"},
    "income_total": {"ar": "إجمالي الإيرادات", "fr": "Total des recettes"},
    "expense_total": {"ar": "إجمالي المصروفات", "fr": "Total des dépenses"},
    "net_total": {"ar": "الصافي (حسب القيود)", "fr": "Solde (selon le journal)"},
    "employees_header": {"ar": "سجل الموظفين", "fr": "Registre des employés"},
    "add_employee": {"ar": "إضافة موظف", "fr": "Ajouter un employé"},
    "edit_employee": {"ar": "تعديل بيانات الموظف", "fr": "Modifier l'employé"},
    "employee_no": {"ar": "رقم الموظف", "fr": "Matricule"},
    "full_name": {"ar": "الاسم الكامل", "fr": "Nom complet"},
    "job_title": {"ar": "الوظيفة", "fr": "Poste"},
    "phone": {"ar": "الهاتف", "fr": "Téléphone"},
    "hire_date": {"ar": "تاريخ التوظيف", "fr": "Date d'embauche"},
    "base_salary": {"ar": "الأجر الأساسي (دج)", "fr": "Salaire de base (DA)"},
    "status": {"ar": "الحالة", "fr": "Statut"},
    "active": {"ar": "نشط", "fr": "Actif"},
    "inactive": {"ar": "غير نشط", "fr": "Inactif"},
    "deactivate": {"ar": "إيقاف الموظف", "fr": "Désactiver"},
    "reactivate": {"ar": "إعادة تفعيل", "fr": "Réactiver"},
    "period": {"ar": "الشهر (YYYY-MM)", "fr": "Mois (AAAA-MM)"},
    "allowances": {"ar": "المنح (دج)", "fr": "Primes (DA)"},
    "deductions": {"ar": "الاقتطاعات (دج)", "fr": "Retenues (DA)"},
    "net_salary": {"ar": "الصافي (دج)", "fr": "Net à payer (DA)"},
    "note": {"ar": "ملاحظة", "fr": "Note"},
    "add_payroll": {"ar": "إعداد راتب", "fr": "Préparer une paie"},
    "mark_paid": {"ar": "تسجيل الدفع", "fr": "Marquer payé"},
    "confirm_paid": {
        "ar": "هل تؤكد تسجيل هذا الراتب مدفوعًا؟ سيُسجل أيضًا كمصروف في دفتر المحاسبة.",
        "fr": "Confirmer le paiement ? Une charge sera aussi inscrite au journal comptable.",
    },
    "paid": {"ar": "مدفوع", "fr": "Payé"},
    "pending": {"ar": "مستحق", "fr": "À payer"},
    "payroll_header": {"ar": "مسيرات الرواتب الشهرية", "fr": "Paies mensuelles"},
    "invalid_period": {"ar": "أدخل الشهر بالصيغة YYYY-MM.", "fr": "Format de mois attendu : AAAA-MM."},
    "invalid_name": {"ar": "الاسم والوظيفة مطلوبان.", "fr": "Nom et poste obligatoires."},
    "negative_values": {"ar": "لا تقبل الأجور والمنح والاقتطاعات قيمًا سالبة.", "fr": "Les montants ne peuvent pas être négatifs."},
    "net_negative": {"ar": "يجب ألا يتجاوز الاقتطاع الأساسي والمنح.", "fr": "Les retenues dépassent le salaire et les primes."},
    "employee_required": {"ar": "اختر موظفًا نشطًا.", "fr": "Choisissez un employé actif."},
    "duplicate_payroll": {"ar": "يوجد راتب مسجل لهذا الموظف في هذا الشهر.", "fr": "Cette paie existe déjà pour ce mois."},
    "no_payroll": {"ar": "لا توجد رواتب مستحقة لهذا الشهر.", "fr": "Aucune paie à enregistrer pour ce mois."},
    "employee_has_payroll": {
        "ar": "لا يمكن إيقاف الموظف وله راتب غير مدفوع. سجّل الدفع أولًا.",
        "fr": "Un employé avec une paie impayée ne peut pas être désactivé.",
    },
}


def tr(key, language="ar"):
    return TRANSLATIONS.get(key, {}).get(language, TRANSLATIONS.get(key, {}).get("ar", key))


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema(db_path):
    """Create only ERP-prefixed tables; do not touch any legacy table."""
    conn = connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS erp_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name_ar TEXT NOT NULL,
                name_fr TEXT NOT NULL DEFAULT '',
                account_type TEXT NOT NULL
                    CHECK (account_type IN ('asset','income','expense')),
                active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS erp_journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date TEXT NOT NULL,
                entry_type TEXT NOT NULL CHECK (entry_type IN ('income','expense')),
                amount REAL NOT NULL CHECK (amount > 0),
                settlement_account_id INTEGER NOT NULL REFERENCES erp_accounts(id),
                category_account_id INTEGER NOT NULL REFERENCES erp_accounts(id),
                memo TEXT NOT NULL DEFAULT '',
                reference TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS erp_journal_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL REFERENCES erp_journal_entries(id),
                account_id INTEGER NOT NULL REFERENCES erp_accounts(id),
                debit REAL NOT NULL DEFAULT 0 CHECK (debit >= 0),
                credit REAL NOT NULL DEFAULT 0 CHECK (credit >= 0),
                CHECK ((debit = 0 AND credit > 0) OR (credit = 0 AND debit > 0))
            );
            CREATE INDEX IF NOT EXISTS erp_journal_date_idx
                ON erp_journal_entries(entry_date, id);
            CREATE TABLE IF NOT EXISTS erp_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_no TEXT UNIQUE,
                full_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                phone TEXT NOT NULL DEFAULT '',
                hire_date TEXT NOT NULL DEFAULT '',
                base_salary REAL NOT NULL DEFAULT 0 CHECK (base_salary >= 0),
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','inactive')),
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS erp_payroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL CHECK (
                    length(period) = 7 AND substr(period, 5, 1) = '-'
                ),
                employee_id INTEGER NOT NULL REFERENCES erp_employees(id),
                base_salary REAL NOT NULL CHECK (base_salary >= 0),
                allowances REAL NOT NULL DEFAULT 0 CHECK (allowances >= 0),
                deductions REAL NOT NULL DEFAULT 0 CHECK (deductions >= 0),
                net_amount REAL NOT NULL CHECK (net_amount >= 0),
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','paid')),
                paid_date TEXT,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(period, employee_id)
            );
            CREATE INDEX IF NOT EXISTS erp_payroll_period_idx
                ON erp_payroll(period, employee_id);
            """
        )
        defaults = [
            ("1000", "الصندوق", "Caisse", "asset"),
            ("1010", "البنك", "Banque", "asset"),
            ("4000", "إيرادات التكوين", "Produits de formation", "income"),
            ("4100", "إيرادات أخرى", "Autres produits", "income"),
            ("6000", "مصاريف التشغيل", "Charges d'exploitation", "expense"),
            ("6100", "أجور ورواتب", "Salaires", "expense"),
        ]
        conn.executemany(
            """INSERT OR IGNORE INTO erp_accounts(code,name_ar,name_fr,account_type)
               VALUES(?,?,?,?)""",
            defaults,
        )
        conn.commit()
    finally:
        conn.close()


def create_journal_entry(db_path, entry_date, entry_type, amount,
                         settlement_account_id, category_account_id,
                         memo="", reference=""):
    amount = float(amount)
    try:
        date.fromisoformat(entry_date)
    except (TypeError, ValueError):
        raise ValueError("entry date must be valid ISO date")
    if amount <= 0 or entry_type not in ("income", "expense"):
        raise ValueError("amount must be positive and type must be income or expense")
    conn = connect(db_path)
    try:
        allowed_type = "income" if entry_type == "income" else "expense"
        rows = conn.execute(
            "SELECT id,account_type FROM erp_accounts WHERE id IN (?,?) AND active=1",
            (settlement_account_id, category_account_id),
        ).fetchall()
        types = {row["id"]: row["account_type"] for row in rows}
        if types.get(settlement_account_id) != "asset" or types.get(category_account_id) != allowed_type:
            raise ValueError("account types do not match the transaction")
        with conn:
            cur = conn.execute(
                """INSERT INTO erp_journal_entries
                   (entry_date,entry_type,amount,settlement_account_id,
                    category_account_id,memo,reference)
                   VALUES(?,?,?,?,?,?,?)""",
                (entry_date, entry_type, amount, settlement_account_id,
                 category_account_id, memo.strip(), reference.strip()),
            )
            entry_id = cur.lastrowid
            if entry_type == "income":
                lines = [
                    (entry_id, settlement_account_id, amount, 0),
                    (entry_id, category_account_id, 0, amount),
                ]
            else:
                lines = [
                    (entry_id, category_account_id, amount, 0),
                    (entry_id, settlement_account_id, 0, amount),
                ]
            conn.executemany(
                """INSERT INTO erp_journal_lines(entry_id,account_id,debit,credit)
                   VALUES(?,?,?,?)""",
                lines,
            )
        return entry_id
    finally:
        conn.close()


def reverse_journal_entry(db_path, entry_id):
    """Post an auditable opposite transaction; never delete the source entry."""
    conn = connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM erp_journal_entries WHERE id=?", (entry_id,)
        ).fetchone()
        if not row:
            raise ValueError("journal entry does not exist")
        with conn:
            cur = conn.execute(
                """INSERT INTO erp_journal_entries
                   (entry_date,entry_type,amount,settlement_account_id,
                    category_account_id,memo,reference)
                   VALUES(?,?,?,?,?,?,?)""",
                (date.today().isoformat(),
                 "expense" if row["entry_type"] == "income" else "income",
                 row["amount"], row["settlement_account_id"],
                 row["category_account_id"], f"عكس القيد #{entry_id}",
                 f"REV-{entry_id}"),
            )
            reversal_id = cur.lastrowid
            original_lines = conn.execute(
                "SELECT account_id,debit,credit FROM erp_journal_lines WHERE entry_id=?",
                (entry_id,),
            ).fetchall()
            if len(original_lines) != 2:
                raise ValueError("source journal entry is incomplete")
            conn.executemany(
                """INSERT INTO erp_journal_lines(entry_id,account_id,debit,credit)
                   VALUES(?,?,?,?)""",
                [(reversal_id, line["account_id"], line["credit"], line["debit"])
                 for line in original_lines],
            )
        return reversal_id
    finally:
        conn.close()


def save_employee(db_path, data, employee_id=None):
    if not data.get("full_name", "").strip() or not data.get("job_title", "").strip():
        raise ValueError("name and job title are required")
    salary = float(data.get("base_salary") or 0)
    if salary < 0:
        raise ValueError("salary cannot be negative")
    conn = connect(db_path)
    try:
        values = (
            data.get("employee_no", "").strip() or None,
            data["full_name"].strip(),
            data["job_title"].strip(),
            data.get("phone", "").strip(),
            data.get("hire_date", "").strip(),
            salary,
            data.get("notes", "").strip(),
        )
        with conn:
            if employee_id:
                conn.execute(
                    """UPDATE erp_employees SET employee_no=?,full_name=?,job_title=?,
                       phone=?,hire_date=?,base_salary=?,notes=? WHERE id=?""",
                    (*values, employee_id),
                )
            else:
                conn.execute(
                    """INSERT INTO erp_employees
                       (employee_no,full_name,job_title,phone,hire_date,base_salary,notes)
                       VALUES(?,?,?,?,?,?,?)""",
                    values,
                )
    finally:
        conn.close()


def add_payroll(db_path, period, employee_id, allowances=0, deductions=0, note=""):
    try:
        parsed_period = date(int(period[:4]), int(period[5:7]), 1)
    except (ValueError, IndexError):
        raise ValueError("period must be a valid YYYY-MM month")
    if parsed_period.strftime("%Y-%m") != period:
        raise ValueError("period must be a valid YYYY-MM month")
    allowances, deductions = float(allowances), float(deductions)
    if allowances < 0 or deductions < 0:
        raise ValueError("payroll additions and deductions cannot be negative")
    conn = connect(db_path)
    try:
        with conn:
            employee = conn.execute(
                "SELECT base_salary,status FROM erp_employees WHERE id=?",
                (employee_id,),
            ).fetchone()
            if not employee or employee["status"] != "active":
                raise ValueError("employee is missing or inactive")
            net = employee["base_salary"] + allowances - deductions
            if net < 0:
                raise ValueError("payroll deductions cannot exceed gross pay")
            cur = conn.execute(
                """INSERT INTO erp_payroll
                   (period,employee_id,base_salary,allowances,deductions,net_amount,note)
                   VALUES(?,?,?,?,?,?,?)""",
                (period, employee_id, employee["base_salary"],
                 allowances, deductions, net, note.strip()),
            )
            return cur.lastrowid
    finally:
        conn.close()


def mark_payroll_paid(db_path, payroll_id):
    conn = connect(db_path)
    try:
        payroll = conn.execute(
            """SELECT p.*,e.full_name FROM erp_payroll p
               JOIN erp_employees e ON e.id=p.employee_id
               WHERE p.id=? AND p.status='pending'""",
            (payroll_id,),
        ).fetchone()
        if not payroll:
            raise ValueError("payroll item does not exist or is already paid")
        accounts = conn.execute(
            """SELECT id,account_type FROM erp_accounts
               WHERE code IN ('1000','6100') AND active=1"""
        ).fetchall()
        account_ids = {row["account_type"]: row["id"] for row in accounts}
        settlement_id = next(
            (row["id"] for row in accounts
             if row["account_type"] == "asset"
             and conn.execute("SELECT code FROM erp_accounts WHERE id=?", (row["id"],)).fetchone()["code"] == "1000"),
            None,
        )
        salary_id = next(
            (row["id"] for row in accounts
             if row["account_type"] == "expense"
             and conn.execute("SELECT code FROM erp_accounts WHERE id=?", (row["id"],)).fetchone()["code"] == "6100"),
            None,
        )
        if not settlement_id or not salary_id:
            raise ValueError("salary journal accounts are unavailable")
        with conn:
            cur = conn.execute(
                """UPDATE erp_payroll SET status='paid',paid_date=?
                   WHERE id=? AND status='pending'""",
                (date.today().isoformat(), payroll_id),
            )
            if cur.rowcount != 1:
                raise ValueError("payroll item does not exist or is already paid")
            memo = f'راتب {payroll["full_name"]} — {payroll["period"]}'
            reference = f'PAY-{payroll["period"]}-{payroll_id}'
            journal = conn.execute(
                """INSERT INTO erp_journal_entries
                   (entry_date,entry_type,amount,settlement_account_id,
                    category_account_id,memo,reference)
                   VALUES(?,'expense',?,?,?,?,?)""",
                (date.today().isoformat(), payroll["net_amount"], settlement_id,
                 salary_id, memo, reference),
            )
            conn.executemany(
                """INSERT INTO erp_journal_lines(entry_id,account_id,debit,credit)
                   VALUES(?,?,?,?)""",
                [
                    (journal.lastrowid, salary_id, payroll["net_amount"], 0),
                    (journal.lastrowid, settlement_id, 0, payroll["net_amount"]),
                ],
            )
    finally:
        conn.close()


class ERPSuiteFrame(tk.Frame):
    """Localized admin workspace for accounting, HR, and monthly payroll."""

    def __init__(self, parent, db_path, language_fn):
        super().__init__(parent, bg=COLORS["bg"])
        self.db_path = db_path
        self.language_fn = language_fn
        ensure_schema(db_path)
        self._build()
        self.refresh_all()

    def _t(self, key):
        return tr(key, self.language_fn())

    def _label(self, parent, key, **kwargs):
        return tk.Label(
            parent, text=self._t(key), bg=kwargs.pop("bg", COLORS["card"]),
            fg=kwargs.pop("fg", COLORS["text"]), **kwargs
        )

    def _button(self, parent, key, command, primary=False):
        return tk.Button(
            parent, text=self._t(key), command=command,
            bg=COLORS["primary"] if primary else COLORS["card"],
            fg="white" if primary else COLORS["text"],
            activebackground=COLORS["primary"],
            activeforeground="white", relief="flat",
            padx=12, pady=7, cursor="hand2",
            font=("Tahoma", 10, "bold"),
        )

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=20, pady=(18, 10))
        self._label(header, "title", bg=COLORS["bg"],
                    font=("Tahoma", 18, "bold")).pack(anchor="e" if self.language_fn() == "ar" else "w")
        self._label(header, "subtitle", bg=COLORS["bg"],
                    fg=COLORS["muted"], font=("Tahoma", 10)).pack(
                        anchor="e" if self.language_fn() == "ar" else "w", pady=(5, 0)
                    )

        self.summary = tk.Frame(self, bg=COLORS["bg"])
        self.summary.pack(fill="x", padx=20, pady=(0, 12))
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.journal_tab = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.accounts_tab = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.employees_tab = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.payroll_tab = tk.Frame(self.notebook, bg=COLORS["bg"])
        for tab, key in (
            (self.journal_tab, "journal"),
            (self.accounts_tab, "accounts"),
            (self.employees_tab, "employees"),
            (self.payroll_tab, "payroll"),
        ):
            self.notebook.add(tab, text=self._t(key))
        self._build_journal()
        self._build_accounts()
        self._build_employees()
        self._build_payroll()

    def _tree(self, parent, columns, headings, widths):
        wrapper = tk.Frame(parent, bg=COLORS["card"])
        wrapper.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        tree = ttk.Treeview(
            wrapper, columns=columns, show="headings",
            style="Treeview", height=12,
        )
        for column, heading, width in zip(columns, headings, widths):
            tree.heading(column, text=self._t(heading) if heading in TRANSLATIONS else heading)
            tree.column(column, width=width, anchor="center", stretch=True)
        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _build_journal(self):
        controls = tk.Frame(self.journal_tab, bg=COLORS["bg"])
        controls.pack(fill="x", padx=12, pady=10)
        self._button(controls, "add_entry", self._entry_dialog, True).pack(side="right")
        self._button(controls, "reverse", self._reverse_selected).pack(side="right", padx=8)
        self.journal_tree = self._tree(
            self.journal_tab,
            ("id", "date", "type", "amount", "settlement", "category", "reference", "memo"),
            ("#", "date", "kind", "amount", "settlement", "category", "reference", "description"),
            (55, 105, 75, 110, 135, 165, 100, 220),
        )

    def _build_accounts(self):
        controls = tk.Frame(self.accounts_tab, bg=COLORS["bg"])
        controls.pack(fill="x", padx=12, pady=10)
        self._button(controls, "new_account", self._account_dialog, True).pack(side="right")
        self.accounts_tree = self._tree(
            self.accounts_tab, ("code", "name", "type", "active"),
            ("code", "name", "account_type", "status"), (130, 310, 180, 100),
        )

    def _build_employees(self):
        controls = tk.Frame(self.employees_tab, bg=COLORS["bg"])
        controls.pack(fill="x", padx=12, pady=10)
        self._button(controls, "add_employee", self._employee_dialog, True).pack(side="right")
        self._button(controls, "edit_employee", self._edit_employee).pack(side="right", padx=8)
        self.toggle_employee_button = self._button(
            controls, "deactivate", self._toggle_employee
        )
        self.toggle_employee_button.pack(side="right")
        self.employees_tree = self._tree(
            self.employees_tab,
            ("id", "number", "name", "job", "phone", "hire", "salary", "status"),
            ("#", "employee_no", "full_name", "job_title", "phone", "hire_date", "base_salary", "status"),
            (55, 100, 180, 145, 120, 110, 125, 90),
        )
        self.employees_tree.bind("<<TreeviewSelect>>", self._update_toggle_label)

    def _build_payroll(self):
        controls = tk.Frame(self.payroll_tab, bg=COLORS["bg"])
        controls.pack(fill="x", padx=12, pady=10)
        self._button(controls, "add_payroll", self._payroll_dialog, True).pack(side="right")
        self._button(controls, "mark_paid", self._mark_paid).pack(side="right", padx=8)
        self.payroll_tree = self._tree(
            self.payroll_tab,
            ("id", "period", "employee", "base", "allowances", "deductions", "net", "status", "paid_date"),
            ("#", "period", "full_name", "base_salary", "allowances", "deductions", "net_salary", "status", "date"),
            (55, 100, 180, 120, 120, 120, 125, 95, 110),
        )

    def _summary_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["border"],
                        highlightthickness=1, padx=16, pady=12)
        card.pack(side="right", fill="x", expand=True, padx=(0, 8))
        self._label(card, title, fg=COLORS["muted"], font=("Tahoma", 10)).pack(anchor="e")
        tk.Label(card, text=value, bg=COLORS["card"], fg=color,
                 font=("Tahoma", 15, "bold")).pack(anchor="e", pady=(4, 0))

    def refresh_all(self):
        if not self.winfo_exists():
            return
        conn = connect(self.db_path)
        try:
            totals = conn.execute(
                """SELECT
                     COALESCE(SUM(CASE WHEN entry_type='income' THEN amount END),0) income,
                     COALESCE(SUM(CASE WHEN entry_type='expense' THEN amount END),0) expense
                   FROM erp_journal_entries"""
            ).fetchone()
            employee_count = conn.execute(
                "SELECT COUNT(*) FROM erp_employees WHERE status='active'"
            ).fetchone()[0]
        finally:
            conn.close()
        for child in self.summary.winfo_children():
            child.destroy()
        income, expense = totals["income"], totals["expense"]
        self._summary_card(self.summary, "income_total", f"{income:,.2f} دج", COLORS["green"])
        self._summary_card(self.summary, "expense_total", f"{expense:,.2f} دج", COLORS["red"])
        self._summary_card(self.summary, "net_total", f"{income-expense:,.2f} دج", COLORS["primary"])
        self._summary_card(self.summary, "employees_header", str(employee_count), COLORS["text"])
        self._refresh_journal()
        self._refresh_accounts()
        self._refresh_employees()
        self._refresh_payroll()

    @staticmethod
    def _clear(tree):
        tree.delete(*tree.get_children())

    def _refresh_journal(self):
        self._clear(self.journal_tree)
        conn = connect(self.db_path)
        try:
            rows = conn.execute(
                """SELECT j.*, s.code settlement_code, s.name_ar settlement_ar,
                          s.name_fr settlement_fr, c.code category_code,
                          c.name_ar category_ar,c.name_fr category_fr
                   FROM erp_journal_entries j
                   JOIN erp_accounts s ON s.id=j.settlement_account_id
                   JOIN erp_accounts c ON c.id=j.category_account_id
                   ORDER BY j.entry_date DESC,j.id DESC"""
            ).fetchall()
            for row in rows:
                direction = self._t(row["entry_type"])
                settlement = f'{row["settlement_code"]} {row["settlement_ar"] if self.language_fn()=="ar" else row["settlement_fr"]}'
                category = f'{row["category_code"]} {row["category_ar"] if self.language_fn()=="ar" else row["category_fr"]}'
                self.journal_tree.insert(
                    "", "end", iid=str(row["id"]),
                    values=(row["id"], row["entry_date"], direction,
                            f'{row["amount"]:,.2f}', settlement, category,
                            row["reference"], row["memo"]),
                )
        finally:
            conn.close()

    def _refresh_accounts(self):
        self._clear(self.accounts_tree)
        conn = connect(self.db_path)
        try:
            for row in conn.execute("SELECT * FROM erp_accounts ORDER BY code"):
                name = row["name_ar"] if self.language_fn() == "ar" else row["name_fr"]
                self.accounts_tree.insert(
                    "", "end", iid=str(row["id"]),
                    values=(row["code"], name, row["account_type"],
                            self._t("active") if row["active"] else self._t("inactive")),
                )
        finally:
            conn.close()

    def _refresh_employees(self):
        self._clear(self.employees_tree)
        conn = connect(self.db_path)
        try:
            for row in conn.execute("SELECT * FROM erp_employees ORDER BY full_name"):
                self.employees_tree.insert(
                    "", "end", iid=str(row["id"]),
                    values=(row["id"], row["employee_no"] or "", row["full_name"],
                            row["job_title"], row["phone"], row["hire_date"],
                            f'{row["base_salary"]:,.2f}',
                            self._t(row["status"])),
                )
        finally:
            conn.close()

    def _refresh_payroll(self):
        self._clear(self.payroll_tree)
        conn = connect(self.db_path)
        try:
            rows = conn.execute(
                """SELECT p.*,e.full_name FROM erp_payroll p
                   JOIN erp_employees e ON e.id=p.employee_id
                   ORDER BY p.period DESC,e.full_name"""
            )
            for row in rows:
                self.payroll_tree.insert(
                    "", "end", iid=str(row["id"]),
                    values=(row["id"], row["period"], row["full_name"],
                            f'{row["base_salary"]:,.2f}', f'{row["allowances"]:,.2f}',
                            f'{row["deductions"]:,.2f}', f'{row["net_amount"]:,.2f}',
                            self._t(row["status"]), row["paid_date"] or ""),
                )
        finally:
            conn.close()

    def _dialog(self, title, fields, save):
        window = tk.Toplevel(self)
        window.title(title)
        window.configure(bg=COLORS["card"])
        window.resizable(False, False)
        window.transient(self.winfo_toplevel())
        window.grab_set()
        body = tk.Frame(window, bg=COLORS["card"], padx=20, pady=16)
        body.pack(fill="both", expand=True)
        widgets = {}
        for row_index, (key, widget_type, choices) in enumerate(fields):
            label = self._label(body, key, font=("Tahoma", 10))
            label.grid(row=row_index, column=1, sticky="e", padx=(12, 0), pady=6)
            if widget_type == "combo":
                widget = ttk.Combobox(body, state="readonly", width=31, values=choices)
                if choices:
                    widget.current(0)
            elif widget_type == "text":
                widget = tk.Text(body, width=33, height=3, font=("Tahoma", 10))
            else:
                widget = ttk.Entry(body, width=34)
            widget.grid(row=row_index, column=0, sticky="ew", pady=6)
            widgets[key] = widget

        def submit():
            values = {}
            for key, widget in widgets.items():
                values[key] = (widget.get("1.0", "end-1c") if isinstance(widget, tk.Text)
                               else widget.get().strip())
            try:
                save(values)
                window.destroy()
                self.refresh_all()
            except sqlite3.IntegrityError as exc:
                messagebox.showerror(self._t("title"), self._integrity_message(exc), parent=window)
            except (ValueError, TypeError) as exc:
                messagebox.showwarning(self._t("title"), self._friendly_error(exc), parent=window)

        actions = tk.Frame(body, bg=COLORS["card"])
        actions.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self._button(actions, "btn_save", submit, True).pack(side="right")
        self._button(actions, "btn_cancel", window.destroy).pack(side="right", padx=8)
        window.update_idletasks()
        window.geometry(f"+{max(0, (window.winfo_screenwidth()-window.winfo_width())//2)}+"
                        f"{max(0, (window.winfo_screenheight()-window.winfo_height())//2)}")
        return widgets

    def _friendly_error(self, error):
        message = str(error)
        mapping = {
            "name and job title are required": "invalid_name",
            "salary cannot be negative": "negative_values",
            "period must be a valid YYYY-MM month": "invalid_period",
            "entry date must be valid ISO date": "date",
            "account code is required": "code_required",
            "account name is required": "name_required",
            "salary journal accounts are unavailable": "account_invalid",
            "payroll additions and deductions cannot be negative": "negative_values",
            "payroll deductions cannot exceed gross pay": "net_negative",
            "employee is missing or inactive": "employee_required",
            "amount must be positive and type must be income or expense": "invalid_amount",
            "account types do not match the transaction": "account_invalid",
            "payroll item does not exist or is already paid": "no_payroll",
        }
        return self._t(mapping.get(message, "invalid_amount"))

    def _integrity_message(self, error):
        text = str(error).lower()
        if "erp_payroll" in text:
            return self._t("duplicate_payroll")
        if "erp_accounts" in text:
            return self._t("code_required")
        if "employee" in text:
            return self._t("employee_required")
        return str(error)

    def _entry_dialog(self):
        accounts = self._account_options()
        settlement_ids = [a for a in accounts if a["account_type"] == "asset"]
        income_ids = [a for a in accounts if a["account_type"] == "income"]
        expense_ids = [a for a in accounts if a["account_type"] == "expense"]
        if not settlement_ids or not income_ids or not expense_ids:
            messagebox.showerror(self._t("title"), self._t("account_invalid"), parent=self)
            return
        fields = [
            ("kind", "combo", [self._t("income"), self._t("expense")]),
            ("date", "entry", None),
            ("settlement", "combo", [a["label"] for a in settlement_ids]),
            ("category", "combo", [a["label"] for a in income_ids]),
            ("amount", "entry", None),
            ("reference", "entry", None),
            ("description", "entry", None),
        ]

        def save(values):
            if not values["amount"]:
                raise ValueError("amount must be positive and type must be income or expense")
            entry_type = "income" if values["kind"] == self._t("income") else "expense"
            candidates = income_ids if entry_type == "income" else expense_ids
            label = values["category"]
            category = next((a for a in candidates if a["label"] == label), None)
            settlement = next((a for a in settlement_ids if a["label"] == values["settlement"]), None)
            if not category or not settlement:
                raise ValueError("account types do not match the transaction")
            create_journal_entry(
                self.db_path, values["date"], entry_type, values["amount"],
                settlement["id"], category["id"],
                values["description"], values["reference"],
            )

        widgets = self._dialog(self._t("add_entry"), fields, save)
        widgets["date"].insert(0, date.today().isoformat())
        type_widget, category_widget = widgets["kind"], widgets["category"]

        def update_categories(_event=None):
            options = income_ids if type_widget.get() == self._t("income") else expense_ids
            category_widget.configure(values=[a["label"] for a in options])
            if options:
                category_widget.current(0)
        type_widget.bind("<<ComboboxSelected>>", update_categories)
        update_categories()

    def _account_options(self):
        conn = connect(self.db_path)
        try:
            rows = conn.execute("SELECT * FROM erp_accounts WHERE active=1 ORDER BY code").fetchall()
            return [
                {"id": row["id"], "code": row["code"], "account_type": row["account_type"],
                 "label": f'{row["code"]} {row["name_ar"] if self.language_fn()=="ar" else row["name_fr"]}'}
                for row in rows
            ]
        finally:
            conn.close()

    def _reverse_selected(self):
        selected = self.journal_tree.selection()
        if not selected:
            messagebox.showinfo(self._t("title"), self._t("no_selection"), parent=self)
            return
        if not messagebox.askyesno(self._t("reverse"), self._t("confirm_reverse"), parent=self):
            return
        try:
            reverse_journal_entry(self.db_path, int(selected[0]))
            self.refresh_all()
        except (ValueError, sqlite3.Error) as exc:
            messagebox.showerror(self._t("title"), str(exc), parent=self)

    def _account_dialog(self):
        type_options = ["asset", "income", "expense"]

        def save(values):
            if not values["code"]:
                raise ValueError("account code is required")
            if not values["name"]:
                raise ValueError("account name is required")
            conn = connect(self.db_path)
            try:
                with conn:
                    conn.execute(
                        """INSERT INTO erp_accounts(code,name_ar,name_fr,account_type)
                           VALUES(?,?,?,?)""",
                        (values["code"], values["name"], values["name"], values["account_type"]),
                    )
            finally:
                conn.close()
        self._dialog(
            self._t("new_account"),
            [("code", "entry", None), ("name", "entry", None),
             ("account_type", "combo", type_options)],
            save,
        )

    def _selected_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showinfo(self._t("title"), self._t("no_selection"), parent=self)
            return None
        conn = connect(self.db_path)
        try:
            return conn.execute(
                "SELECT * FROM erp_employees WHERE id=?", (int(selected[0]),)
            ).fetchone()
        finally:
            conn.close()

    def _update_toggle_label(self, _event=None):
        selected = self.employees_tree.selection()
        if not selected:
            return
        values = self.employees_tree.item(selected[0], "values")
        is_active = values[-1] == self._t("active")
        self.toggle_employee_button.configure(
            text=self._t("deactivate" if is_active else "reactivate")
        )

    def _employee_dialog(self, employee=None):
        fields = [
            ("employee_no", "entry", None), ("full_name", "entry", None),
            ("job_title", "entry", None), ("phone", "entry", None),
            ("hire_date", "entry", None), ("base_salary", "entry", None),
            ("note", "text", None),
        ]
        def save(values):
            save_employee(self.db_path, values, employee["id"] if employee else None)
        widgets = self._dialog(self._t("edit_employee" if employee else "add_employee"), fields, save)
        if employee:
            for key, value in (
                ("employee_no", employee["employee_no"] or ""),
                ("full_name", employee["full_name"]),
                ("job_title", employee["job_title"]),
                ("phone", employee["phone"]),
                ("hire_date", employee["hire_date"]),
                ("base_salary", employee["base_salary"]),
            ):
                widgets[key].insert(0, str(value))
            widgets["note"].insert("1.0", employee["notes"])
        else:
            widgets["hire_date"].insert(0, date.today().isoformat())
            widgets["base_salary"].insert(0, "0")

    def _edit_employee(self):
        row = self._selected_employee()
        if row:
            self._employee_dialog(row)

    def _toggle_employee(self):
        row = self._selected_employee()
        if not row:
            return
        next_status = "inactive" if row["status"] == "active" else "active"
        if next_status == "inactive":
            conn = connect(self.db_path)
            try:
                pending = conn.execute(
                    """SELECT 1 FROM erp_payroll
                       WHERE employee_id=? AND status='pending' LIMIT 1""",
                    (row["id"],),
                ).fetchone()
            finally:
                conn.close()
            if pending:
                messagebox.showwarning(self._t("title"), self._t("employee_has_payroll"), parent=self)
                return
        conn = connect(self.db_path)
        try:
            with conn:
                conn.execute(
                    "UPDATE erp_employees SET status=? WHERE id=?",
                    (next_status, row["id"]),
                )
        finally:
            conn.close()
        self._refresh_employees()
        self.toggle_employee_button.configure(
            text=self._t("deactivate" if next_status == "active" else "reactivate")
        )

    def _payroll_dialog(self):
        conn = connect(self.db_path)
        try:
            employees = conn.execute(
                "SELECT id,full_name,base_salary FROM erp_employees WHERE status='active' ORDER BY full_name"
            ).fetchall()
        finally:
            conn.close()
        if not employees:
            messagebox.showinfo(self._t("title"), self._t("employee_required"), parent=self)
            return
        by_label = {f'{row["full_name"]} — {row["base_salary"]:,.2f} دج': row for row in employees}

        def save(values):
            employee = by_label.get(values["full_name"])
            if not employee:
                raise ValueError("employee is missing or inactive")
            add_payroll(
                self.db_path, values["period"], employee["id"],
                values["allowances"] or 0, values["deductions"] or 0, values["note"],
            )
        widgets = self._dialog(
            self._t("add_payroll"),
            [("period", "entry", None),
             ("full_name", "combo", list(by_label)),
             ("allowances", "entry", None),
             ("deductions", "entry", None),
             ("note", "text", None)],
            save,
        )
        widgets["period"].insert(0, date.today().strftime("%Y-%m"))
        widgets["allowances"].insert(0, "0")
        widgets["deductions"].insert(0, "0")

    def _mark_paid(self):
        selected = self.payroll_tree.selection()
        if not selected:
            messagebox.showinfo(self._t("title"), self._t("no_selection"), parent=self)
            return
        if not messagebox.askyesno(self._t("mark_paid"), self._t("confirm_paid"), parent=self):
            return
        try:
            mark_payroll_paid(self.db_path, int(selected[0]))
            self.refresh_all()
        except (ValueError, sqlite3.Error) as exc:
            messagebox.showwarning(self._t("title"), self._friendly_error(exc), parent=self)
