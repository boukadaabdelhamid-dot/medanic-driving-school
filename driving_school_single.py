# -*- coding: utf-8 -*-
"""
نظام إدارة مدرسة تعليم السياقة - الجزائر
Driving School Management System - Algeria
Python 3 | Tkinter | SQLite | reportlab + arabic_reshaper + python-bidi (PDF عربي)

طريقة التشغيل:
    1. ثبّت المكتبات:
        pip install reportlab arabic_reshaper python-bidi
    2. شغّل البرنامج:
        python driving_school_single.py
"""

import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ----- مكتبة PDF -----
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# ----- دعم العربية للـ PDF -----
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_LIBS = True
except ImportError:
    HAS_ARABIC_LIBS = False


# ============================================================================
#  الإعدادات والثوابت
# ============================================================================

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "driving_school.db")

# ----- الخطوط -----
FONT_FAMILY = "Tahoma"
FONT_MAIN   = (FONT_FAMILY, 11)
FONT_BOLD   = (FONT_FAMILY, 11, "bold")
FONT_TITLE  = (FONT_FAMILY, 15, "bold")
FONT_HEADER = (FONT_FAMILY, 18, "bold")
FONT_SMALL  = (FONT_FAMILY, 10)
FONT_TINY   = (FONT_FAMILY, 9)

# ----- الألوان (تصميم عصري وجذاب) -----
COLOR_PRIMARY      = "#4F46E5"   # أزرق بنفسجي جذاب (Indigo)
COLOR_PRIMARY_DARK = "#3730A3"
COLOR_PRIMARY_LIGHT= "#E0E7FF"
COLOR_ACCENT       = "#F59E0B"   # برتقالي دافئ
COLOR_SUCCESS      = "#10B981"   # أخضر نيون منعش
COLOR_DANGER       = "#EF4444"   # أحمر حيوي
COLOR_WARNING      = "#F59E0B"
COLOR_INFO         = "#0EA5E9"   # أزرق سماوي
COLOR_PURPLE       = "#8B5CF6"   # بنفسجي

COLOR_BG           = "#F8FAFC"   # خلفية بيضاء مزرقة مريحة
COLOR_CARD         = "#FFFFFF"
COLOR_SIDEBAR      = "#1E293B"   # سايد بار رمادي مزرق أنيق
COLOR_SIDEBAR_HOVER= "#334155"
COLOR_HEADER       = "#0F172A"
COLOR_TEXT         = "#0F172A"
COLOR_TEXT_LIGHT   = "#64748B"
COLOR_BORDER       = "#CBD5E1"
COLOR_INPUT_BG     = "#F1F5F9"
COLOR_WHITE        = "#FFFFFF"

MONTHS_AR = {"01":"يناير","02":"فبراير","03":"مارس","04":"أبريل","05":"مايو","06":"يونيو",
             "07":"يوليو","08":"أغسطس","09":"سبتمبر","10":"أكتوبر","11":"نوفمبر","12":"ديسمبر"}

STAGE_LABELS = {"code":"الكود (نظري)", "creneau":"الكرينو (مناورات)", "circuit":"الطريق (سياقة)"}
STAGE_ORDER  = ["code", "creneau", "circuit"]
STATUS_PASS  = "ناجح"

STATUS_OPTIONS         = ["لم يبدأ", "قيد التكوين", "ناجح", "راسب"]
GENDER_OPTIONS         = ["ذكر", "أنثى"]
MARITAL_OPTIONS        = ["أعزب", "متزوج", "مطلق", "أرمل"]
LICENSE_OPTIONS        = ["A", "B", "C", "D", "E"]
PAYMENT_METHOD_OPTIONS = ["نقدي", "تحويل بنكي", "شيك"]
BLOOD_TYPE_OPTIONS     = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
EXPENSE_TYPES          = ["وقود","صيانة","كراء","رواتب","تأمين","إعلان","مستلزمات مكتبية","أخرى"]
EXAM_TYPE_OPTIONS      = ["نظري", "تطبيقي"]
EXAM_RESULT_OPTIONS    = ["ناجح", "راسب"]


# ============================================================================
#  دعم العربية في PDF
# ============================================================================

def find_arabic_font():
    """يبحث عن خط TTF يدعم العربية على النظام."""
    candidates = [
        # Windows
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\trado.ttf",
        # macOS
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/nix/store/*/share/fonts/truetype/DejaVuSans.ttf",
    ]
    for p in candidates:
        if "*" in p:
            import glob
            matches = glob.glob(p)
            if matches:
                return matches[0]
        elif os.path.exists(p):
            return p
    # محاولة أخيرة: البحث في مجلدات الخطوط
    for base in ["/usr/share/fonts", "/nix/store"]:
        if os.path.isdir(base):
            for root, _, files in os.walk(base):
                for f in files:
                    if f.lower() in ("dejavusans.ttf", "freesans.ttf", "arial.ttf"):
                        return os.path.join(root, f)
    return None


ARABIC_FONT = "Helvetica"
ARABIC_FONT_BOLD = "Helvetica-Bold"
if HAS_REPORTLAB:
    fp = find_arabic_font()
    if fp:
        try:
            pdfmetrics.registerFont(TTFont("ArabicFont", fp))
            ARABIC_FONT = "ArabicFont"
            # محاولة العثور على نسخة Bold
            bold_path = fp.replace(".ttf", "-Bold.ttf")
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont("ArabicFontBold", bold_path))
                ARABIC_FONT_BOLD = "ArabicFontBold"
            else:
                ARABIC_FONT_BOLD = "ArabicFont"
        except Exception:
            pass


def ar(text):
    """يحوّل النص العربي للعرض الصحيح في PDF (تشكيل + bidi)."""
    if text is None or text == "":
        return ""
    s = str(text)
    if HAS_ARABIC_LIBS:
        try:
            return get_display(arabic_reshaper.reshape(s))
        except Exception:
            return s
    return s


# ============================================================================
#  قاعدة البيانات SQLite
# ============================================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def upgrade_db():
    """يضيف الأعمدة الجديدة لقاعدة بيانات قديمة (توافق رجعي)."""
    conn = get_connection()
    try:
        # أعمدة جدول المترشحين
        cur = conn.execute("PRAGMA table_info(candidates)")
        cand_existing = {row[1] for row in cur.fetchall()}
        cand_cols = [
            ("national_id",        "TEXT DEFAULT ''"),
            ("second_nationality", "TEXT DEFAULT ''"),
            ("current_address",    "TEXT DEFAULT ''"),
            ("is_born_abroad",     "INTEGER DEFAULT 0"),
            ("birth_country",      "TEXT DEFAULT 'الجزائر'"),
            ("embassy",            "TEXT DEFAULT ''"),
            ("consulate",          "TEXT DEFAULT ''"),
            ("file_number",        "TEXT DEFAULT ''"),
            ("file_date",          "TEXT DEFAULT ''"),
            ("address_commune",    "TEXT DEFAULT ''"),
            ("address_wilaya",     "TEXT DEFAULT ''"),
        ]
        for col, dtype in cand_cols:
            if col not in cand_existing:
                conn.execute(f"ALTER TABLE candidates ADD COLUMN {col} {dtype}")

        # أعمدة جدول الممرنين
        cur2 = conn.execute("PRAGMA table_info(instructors)")
        inst_existing = {row[1] for row in cur2.fetchall()}
        inst_cols = [
            ("birth_place",           "TEXT DEFAULT ''"),
            ("contract_duration",     "TEXT DEFAULT ''"),
            ("salary",                "TEXT DEFAULT ''"),
            ("contract_start_date",   "TEXT DEFAULT ''"),
            ("notice_period",         "TEXT DEFAULT '0'"),
            ("contract_signing_date", "TEXT DEFAULT ''"),
        ]
        for col, dtype in inst_cols:
            if col not in inst_existing:
                conn.execute(f"ALTER TABLE instructors ADD COLUMN {col} {dtype}")

        # جدول محاولات الامتحانات (جديد)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exam_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                stage_type TEXT NOT NULL,
                exam_date TEXT DEFAULT (date('now')),
                score REAL DEFAULT 0,
                result TEXT DEFAULT 'راسب',
                notes TEXT DEFAULT '',
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)

        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS school_info (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            name TEXT DEFAULT '', commercial_register TEXT DEFAULT '',
            accreditation_number TEXT DEFAULT '', nif TEXT DEFAULT '',
            nis TEXT DEFAULT '', article_number TEXT DEFAULT '',
            address TEXT DEFAULT '', phone TEXT DEFAULT ''
        );
        INSERT OR IGNORE INTO school_info (id) VALUES (1);

        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            gender TEXT DEFAULT '', birth_date TEXT DEFAULT '',
            birth_place TEXT DEFAULT '',
            phone TEXT DEFAULT '', address TEXT DEFAULT '',
            license_number TEXT DEFAULT '', license_date TEXT DEFAULT '',
            categories TEXT DEFAULT '', experience_years INTEGER DEFAULT 0,
            contract_duration TEXT DEFAULT '', salary TEXT DEFAULT '',
            contract_start_date TEXT DEFAULT '', notice_period TEXT DEFAULT '0',
            contract_signing_date TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            gender TEXT DEFAULT '', birth_date TEXT DEFAULT '',
            birth_place_commune TEXT DEFAULT '', birth_place_wilaya TEXT DEFAULT '',
            marital_status TEXT DEFAULT '', father_name TEXT DEFAULT '',
            mother_name TEXT DEFAULT '', phone TEXT DEFAULT '',
            nationality TEXT DEFAULT 'جزائرية', disability TEXT DEFAULT '',
            blood_type TEXT DEFAULT '', license_type TEXT DEFAULT 'B',
            previous_licenses TEXT DEFAULT '', instructor_id INTEGER,
            total_amount REAL DEFAULT 0,
            registration_date TEXT DEFAULT (date('now')),
            national_id TEXT DEFAULT '',
            second_nationality TEXT DEFAULT '',
            current_address TEXT DEFAULT '',
            is_born_abroad INTEGER DEFAULT 0,
            birth_country TEXT DEFAULT 'الجزائر',
            embassy TEXT DEFAULT '',
            consulate TEXT DEFAULT '',
            FOREIGN KEY (instructor_id) REFERENCES instructors(id)
        );

        CREATE TABLE IF NOT EXISTS training_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL, stage_type TEXT NOT NULL,
            status TEXT DEFAULT 'لم يبدأ', start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '', score REAL DEFAULT 0, notes TEXT DEFAULT '',
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL, date TEXT DEFAULT (date('now')),
            amount REAL NOT NULL, payment_method TEXT DEFAULT 'نقدي',
            notes TEXT DEFAULT '',
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_type TEXT NOT NULL, amount REAL NOT NULL,
            date TEXT DEFAULT (date('now')), notes TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL, plate_number TEXT DEFAULT '',
            insurance_expiry TEXT DEFAULT '', tech_inspection_expiry TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            instructor_id INTEGER NOT NULL,
            vehicle_id INTEGER,
            session_date TEXT NOT NULL,
            session_time TEXT NOT NULL DEFAULT '08:00',
            duration INTEGER NOT NULL DEFAULT 60,
            session_type TEXT DEFAULT 'كرينو',
            notes TEXT DEFAULT '',
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (instructor_id) REFERENCES instructors(id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        );

        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            exam_type TEXT NOT NULL,
            exam_date TEXT DEFAULT (date('now')),
            result TEXT NOT NULL,
            score REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );

        CREATE TABLE IF NOT EXISTS exam_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            stage_type TEXT NOT NULL,
            exam_date TEXT DEFAULT (date('now')),
            score REAL DEFAULT 0,
            result TEXT DEFAULT 'راسب',
            notes TEXT DEFAULT '',
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );

    """)
    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM instructors")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    c.execute("""UPDATE school_info SET name='مدرسة النجاح لتعليم السياقة',
        commercial_register='12345678', accreditation_number='AGR-2020-001',
        nif='000312345678901', nis='120312345678901', article_number='12345678910',
        address='شارع الاستقلال، الجزائر العاصمة', phone='021000000' WHERE id=1""")

    c.execute("""INSERT INTO instructors (first_name,last_name,gender,birth_date,phone,address,
        license_number,license_date,categories,experience_years) VALUES
        ('أحمد','بن علي','ذكر','1980-05-15','0551000001','حي السلام، الجزائر',
         'DZ12345','2005-01-10','B,C',10)""")
    c.execute("""INSERT INTO instructors (first_name,last_name,gender,birth_date,phone,address,
        license_number,license_date,categories,experience_years) VALUES
        ('فاطمة','زهراء','أنثى','1985-09-20','0661000002','حي النور، الجزائر',
         'DZ67890','2010-06-01','A,B',8)""")

    c.execute("""INSERT INTO candidates (first_name,last_name,gender,birth_date,
        birth_place_commune,birth_place_wilaya,marital_status,father_name,mother_name,phone,
        nationality,blood_type,license_type,instructor_id,total_amount,registration_date) VALUES
        ('محمد','بوزيد','ذكر','2000-03-10','باب الوادي','الجزائر','أعزب','علي','خديجة بوزيد',
         '0771000001','جزائرية','A+','B',1,25000,'2024-01-15')""")
    c.execute("""INSERT INTO candidates (first_name,last_name,gender,birth_date,
        birth_place_commune,birth_place_wilaya,marital_status,father_name,mother_name,phone,
        nationality,blood_type,license_type,instructor_id,total_amount,registration_date) VALUES
        ('سارة','حمدي','أنثى','1998-07-22','الحراش','الجزائر','أعزب','كريم','نادية حمدي',
         '0661000003','جزائرية','B+','B',2,25000,'2024-02-01')""")

    for cid, stages in [(1, [('code','ناجح','2024-01-20',18),
                              ('creneau','قيد التكوين','2024-02-01',0),
                              ('circuit','لم يبدأ','',0)]),
                        (2, [('code','ناجح','2024-02-05',17),
                              ('creneau','لم يبدأ','',0),
                              ('circuit','لم يبدأ','',0)])]:
        for stype, status, sdate, score in stages:
            c.execute("""INSERT INTO training_stages
                (candidate_id,stage_type,status,start_date,score) VALUES (?,?,?,?,?)""",
                (cid, stype, status, sdate, score))

    for cid, d_, amt, method, note in [(1,'2024-01-15',15000,'نقدي','دفعة أولى'),
                                        (1,'2024-02-15',10000,'نقدي','دفعة ثانية'),
                                        (2,'2024-02-01',25000,'تحويل بنكي','دفعة كاملة')]:
        c.execute("""INSERT INTO payments
            (candidate_id,date,amount,payment_method,notes) VALUES (?,?,?,?,?)""",
            (cid, d_, amt, method, note))

    for etype, amt, d_, note in [('وقود',5000,'2024-01-31','وقود السيارات التدريبية'),
                                  ('صيانة',12000,'2024-02-10','صيانة دورية للسيارات'),
                                  ('كراء',30000,'2024-02-01','إيجار المقر')]:
        c.execute("INSERT INTO expenses (expense_type,amount,date,notes) VALUES (?,?,?,?)",
                  (etype, amt, d_, note))

    conn.commit()
    conn.close()


# ============================================================================
#  طبقة الوصول إلى قاعدة البيانات
# ============================================================================

class SchoolInfoDB:
    @staticmethod
    def get():
        conn = get_connection()
        row = conn.execute("SELECT * FROM school_info WHERE id=1").fetchone()
        conn.close()
        return dict(row) if row else {}

    @staticmethod
    def update(d):
        conn = get_connection()
        conn.execute("""UPDATE school_info SET name=?,commercial_register=?,
            accreditation_number=?,nif=?,nis=?,article_number=?,address=?,phone=? WHERE id=1""",
            (d['name'], d['commercial_register'], d['accreditation_number'],
             d['nif'], d['nis'], d['article_number'], d['address'], d['phone']))
        conn.commit()
        conn.close()


class InstructorDB:
    @staticmethod
    def get_all(search=""):
        conn = get_connection()
        if search:
            rows = conn.execute("""SELECT * FROM instructors
                WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?""",
                (f"%{search}%",) * 3).fetchall()
        else:
            rows = conn.execute("SELECT * FROM instructors ORDER BY last_name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get(i):
        conn = get_connection()
        row = conn.execute("SELECT * FROM instructors WHERE id=?", (i,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute("""INSERT INTO instructors (first_name,last_name,gender,birth_date,birth_place,phone,
            address,license_number,license_date,categories,experience_years,
            contract_duration, salary, contract_start_date, notice_period, contract_signing_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (d['first_name'], d['last_name'], d['gender'], d['birth_date'], d.get('birth_place',''), d['phone'],
             d['address'], d['license_number'], d['license_date'], d['categories'],
             d['experience_years'], d.get('contract_duration',''), d.get('salary',''),
             d.get('contract_start_date',''), d.get('notice_period','0'), d.get('contract_signing_date','')))
        conn.commit()
        conn.close()

    @staticmethod
    def update(i, d):
        conn = get_connection()
        conn.execute("""UPDATE instructors SET first_name=?,last_name=?,gender=?,birth_date=?,
            birth_place=?,phone=?,address=?,license_number=?,license_date=?,categories=?,experience_years=?,
            contract_duration=?, salary=?, contract_start_date=?, notice_period=?, contract_signing_date=?
            WHERE id=?""", (d['first_name'], d['last_name'], d['gender'], d['birth_date'],
            d.get('birth_place',''), d['phone'], d['address'], d['license_number'], d['license_date'],
            d['categories'], d['experience_years'], d.get('contract_duration',''), d.get('salary',''),
            d.get('contract_start_date',''), d.get('notice_period','0'), d.get('contract_signing_date',''), i))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(i):
        conn = get_connection()
        conn.execute("DELETE FROM instructors WHERE id=?", (i,))
        conn.commit()
        conn.close()


class CandidateDB:
    @staticmethod
    def get_all(search=""):
        conn = get_connection()
        if search:
            rows = conn.execute("""SELECT c.*, i.first_name||' '||i.last_name as instructor_name
                FROM candidates c LEFT JOIN instructors i ON c.instructor_id=i.id
                WHERE c.first_name LIKE ? OR c.last_name LIKE ? OR c.phone LIKE ?""",
                (f"%{search}%",) * 3).fetchall()
        else:
            rows = conn.execute("""SELECT c.*, i.first_name||' '||i.last_name as instructor_name
                FROM candidates c LEFT JOIN instructors i ON c.instructor_id=i.id
                ORDER BY c.last_name""").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get(i):
        conn = get_connection()
        row = conn.execute("SELECT * FROM candidates WHERE id=?", (i,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute("""INSERT INTO candidates (first_name,last_name,gender,birth_date,
            birth_place_commune,birth_place_wilaya,marital_status,father_name,mother_name,phone,
            nationality,disability,blood_type,license_type,previous_licenses,instructor_id,
            total_amount,national_id,second_nationality,current_address,is_born_abroad,
            birth_country,embassy,consulate,file_number,file_date,address_commune,address_wilaya)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (d['first_name'], d['last_name'], d['gender'], d['birth_date'],
             d['birth_place_commune'], d['birth_place_wilaya'], d['marital_status'],
             d['father_name'], d['mother_name'], d['phone'], d['nationality'],
             d['disability'], d['blood_type'], d['license_type'],
             d['previous_licenses'], d.get('instructor_id'), d['total_amount'],
             d.get('national_id',''), d.get('second_nationality',''),
             d.get('current_address',''), d.get('is_born_abroad',0),
             d.get('birth_country','الجزائر'), d.get('embassy',''), d.get('consulate',''),
             d.get('file_number',''), d.get('file_date',''),
             d.get('address_commune',''), d.get('address_wilaya','')))
        lid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("INSERT INTO training_stages (candidate_id,stage_type) VALUES (?,?)",
                     (lid, 'code'))
        conn.commit()
        conn.close()
        return lid

    @staticmethod
    def update(i, d):
        conn = get_connection()
        conn.execute("""UPDATE candidates SET first_name=?,last_name=?,gender=?,birth_date=?,
            birth_place_commune=?,birth_place_wilaya=?,marital_status=?,father_name=?,
            mother_name=?,phone=?,nationality=?,disability=?,blood_type=?,license_type=?,
            previous_licenses=?,instructor_id=?,total_amount=?,national_id=?,
            second_nationality=?,current_address=?,is_born_abroad=?,birth_country=?,
            embassy=?,consulate=?,file_number=?,file_date=?,address_commune=?,address_wilaya=?
            WHERE id=?""",
            (d['first_name'], d['last_name'], d['gender'], d['birth_date'],
             d['birth_place_commune'], d['birth_place_wilaya'], d['marital_status'],
             d['father_name'], d['mother_name'], d['phone'], d['nationality'],
             d['disability'], d['blood_type'], d['license_type'],
             d['previous_licenses'], d.get('instructor_id'), d['total_amount'],
             d.get('national_id',''), d.get('second_nationality',''),
             d.get('current_address',''), d.get('is_born_abroad',0),
             d.get('birth_country','الجزائر'), d.get('embassy',''),
             d.get('consulate',''), d.get('file_number',''), d.get('file_date',''),
             d.get('address_commune',''), d.get('address_wilaya',''), i))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(i):
        conn = get_connection()
        conn.execute("DELETE FROM training_stages WHERE candidate_id=?", (i,))
        conn.execute("DELETE FROM payments WHERE candidate_id=?", (i,))
        conn.execute("DELETE FROM exam_results WHERE candidate_id=?", (i,))
        conn.execute("DELETE FROM sessions WHERE candidate_id=?", (i,))
        conn.execute("DELETE FROM candidates WHERE id=?", (i,))
        conn.commit()
        conn.close()


class TrainingDB:
    @staticmethod
    def get_by_candidate(cid):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM training_stages WHERE candidate_id=?",
                            (cid,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(cid, stage_type):
        conn = get_connection()
        conn.execute("INSERT INTO training_stages (candidate_id,stage_type) VALUES (?,?)",
                     (cid, stage_type))
        conn.commit()
        conn.close()

    @staticmethod
    def update(i, d):
        conn = get_connection()
        conn.execute("""UPDATE training_stages SET status=?,start_date=?,end_date=?,
            score=?,notes=? WHERE id=?""",
            (d['status'], d['start_date'], d['end_date'], d['score'], d['notes'], i))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats():
        conn = get_connection()
        rows = conn.execute("""
            SELECT stage_type, result as status, COUNT(*) as count 
            FROM exam_attempts 
            GROUP BY stage_type, result
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class ExamAttemptsDB:
    @staticmethod
    def get_by_candidate(cid):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM exam_attempts WHERE candidate_id=? ORDER BY stage_type, exam_date",
            (cid,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_candidate_and_stage(cid, stage_type):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM exam_attempts WHERE candidate_id=? AND stage_type=? ORDER BY exam_date",
            (cid, stage_type)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute("""INSERT INTO exam_attempts
            (candidate_id, stage_type, exam_date, score, result, notes)
            VALUES (?,?,?,?,?,?)""",
            (d['candidate_id'], d['stage_type'], d['exam_date'],
             d['score'], d['result'], d['notes']))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(i):
        conn = get_connection()
        conn.execute("DELETE FROM exam_attempts WHERE id=?", (i,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats_by_stage():
        conn = get_connection()
        rows = conn.execute("""
            SELECT stage_type,
                   COUNT(*) as total,
                   SUM(CASE WHEN result='ناجح' THEN 1 ELSE 0 END) as passed
            FROM exam_attempts
            GROUP BY stage_type
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class PaymentDB:
    @staticmethod
    def get_by_candidate(cid):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM payments WHERE candidate_id=? ORDER BY date DESC",
                            (cid,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_total_by_candidate(cid):
        conn = get_connection()
        row = conn.execute("SELECT COALESCE(SUM(amount),0) as t FROM payments WHERE candidate_id=?",
                           (cid,)).fetchone()
        conn.close()
        return row['t'] if row else 0

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute("""INSERT INTO payments (candidate_id,date,amount,payment_method,notes)
            VALUES (?,?,?,?,?)""",
            (d['candidate_id'], d['date'], d['amount'], d['payment_method'], d['notes']))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(i):
        conn = get_connection()
        conn.execute("DELETE FROM payments WHERE id=?", (i,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_total_by_month(y, m):
        conn = get_connection()
        row = conn.execute("""SELECT COALESCE(SUM(amount),0) as t FROM payments
            WHERE strftime('%Y',date)=? AND strftime('%m',date)=?""",
            (str(y), f"{m:02d}")).fetchone()
        conn.close()
        return row['t'] if row else 0

    @staticmethod
    def get_total_by_year(y):
        conn = get_connection()
        row = conn.execute("""SELECT COALESCE(SUM(amount),0) as t FROM payments
            WHERE strftime('%Y',date)=?""", (str(y),)).fetchone()
        conn.close()
        return row['t'] if row else 0

    @staticmethod
    def get_monthly_breakdown(y):
        conn = get_connection()
        rows = conn.execute("""SELECT strftime('%m',date) as month,
            COALESCE(SUM(amount),0) as total FROM payments
            WHERE strftime('%Y',date)=? GROUP BY month ORDER BY month""",
            (str(y),)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class ExpenseDB:
    @staticmethod
    def get_all(search=""):
        conn = get_connection()
        if search:
            rows = conn.execute("""SELECT * FROM expenses
                WHERE expense_type LIKE ? OR notes LIKE ? ORDER BY date DESC""",
                (f"%{search}%", f"%{search}%")).fetchall()
        else:
            rows = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute("INSERT INTO expenses (expense_type,amount,date,notes) VALUES (?,?,?,?)",
                     (d['expense_type'], d['amount'], d['date'], d['notes']))
        conn.commit()
        conn.close()

    @staticmethod
    def update(i, d):
        conn = get_connection()
        conn.execute("UPDATE expenses SET expense_type=?,amount=?,date=?,notes=? WHERE id=?",
                     (d['expense_type'], d['amount'], d['date'], d['notes'], i))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(i):
        conn = get_connection()
        conn.execute("DELETE FROM expenses WHERE id=?", (i,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_total_by_month(y, m):
        conn = get_connection()
        row = conn.execute("""SELECT COALESCE(SUM(amount),0) as t FROM expenses
            WHERE strftime('%Y',date)=? AND strftime('%m',date)=?""",
            (str(y), f"{m:02d}")).fetchone()
        conn.close()
        return row['t'] if row else 0

    @staticmethod
    def get_total_by_year(y):
        conn = get_connection()
        row = conn.execute("""SELECT COALESCE(SUM(amount),0) as t FROM expenses
            WHERE strftime('%Y',date)=?""", (str(y),)).fetchone()
        conn.close()
        return row['t'] if row else 0

    @staticmethod
    def get_monthly_breakdown(y):
        conn = get_connection()
        rows = conn.execute("""SELECT strftime('%m',date) as month,
            COALESCE(SUM(amount),0) as total FROM expenses
            WHERE strftime('%Y',date)=? GROUP BY month ORDER BY month""",
            (str(y),)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class VehicleDB:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM vehicles").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_alerts():
        conn = get_connection()
        today = date.today().strftime('%Y-%m-%d')
        rows = conn.execute("""
            SELECT * FROM vehicles 
            WHERE insurance_expiry <= date(?, '+15 days')
            OR tech_inspection_expiry <= date(?, '+15 days')
        """, (today, today)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class SessionDB:
    """طبقة الوصول لجدول الحصص التدريبية."""

    @staticmethod
    def get_all(date_filter="", instructor_id=None, candidate_id=None):
        conn = get_connection()
        sql = """
            SELECT s.*,
                   c.first_name||' '||c.last_name  AS candidate_name,
                   i.first_name||' '||i.last_name  AS instructor_name
            FROM sessions s
            JOIN candidates  c ON s.candidate_id  = c.id
            JOIN instructors i ON s.instructor_id  = i.id
            WHERE 1=1
        """
        params = []
        if date_filter:
            sql += " AND s.session_date = ?"
            params.append(date_filter)
        if instructor_id:
            sql += " AND s.instructor_id = ?"
            params.append(instructor_id)
        if candidate_id:
            sql += " AND s.candidate_id = ?"
            params.append(candidate_id)
        sql += " ORDER BY s.session_date, s.session_time"
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_today():
        return SessionDB.get_all(date_filter=date.today().strftime('%Y-%m-%d'))

    @staticmethod
    def get_week():
        """حصص الأسبوع القادم (اليوم + 6 أيام)."""
        conn = get_connection()
        today = date.today().strftime('%Y-%m-%d')
        end   = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        rows  = conn.execute("""
            SELECT s.*,
                   c.first_name||' '||c.last_name  AS candidate_name,
                   i.first_name||' '||i.last_name  AS instructor_name
            FROM sessions s
            JOIN candidates  c ON s.candidate_id  = c.id
            JOIN instructors i ON s.instructor_id  = i.id
            WHERE s.session_date BETWEEN ? AND ?
            ORDER BY s.session_date, s.session_time
        """, (today, end)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get(sid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute("""
            INSERT INTO sessions
                (candidate_id, instructor_id, vehicle_id, session_date, session_time,
                 duration, session_type, notes)
            VALUES (?,?,?,?,?,?,?,?)""",
            (d['candidate_id'], d['instructor_id'], d.get('vehicle_id'),
             d['session_date'], d['session_time'], d['duration'],
             d.get('session_type', 'كرينو'), d.get('notes', '')))
        conn.commit()
        conn.close()

    @staticmethod
    def update(sid, d):
        conn = get_connection()
        conn.execute("""
            UPDATE sessions SET candidate_id=?, instructor_id=?, vehicle_id=?,
                session_date=?, session_time=?, duration=?,
                session_type=?, notes=?
            WHERE id=?""",
            (d['candidate_id'], d['instructor_id'], d.get('vehicle_id'),
             d['session_date'], d['session_time'], d['duration'],
             d.get('session_type', 'كرينو'), d.get('notes', ''), sid))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(sid):
        conn = get_connection()
        conn.execute("DELETE FROM sessions WHERE id=?", (sid,))
        conn.commit()
        conn.close()

    @staticmethod
    def _overlapping(rows, session_time, duration):
        """يُعيد قائمة الصفوف المتعارضة زمنياً."""
        try:
            new_start = datetime.strptime(session_time, "%H:%M")
            new_end   = new_start + timedelta(minutes=int(duration))
        except Exception:
            return []
        conflicts = []
        for r in rows:
            try:
                ex_start = datetime.strptime(r['session_time'], "%H:%M")
                ex_end   = ex_start + timedelta(minutes=int(r['duration']))
                if new_start < ex_end and new_end > ex_start:
                    conflicts.append(dict(r))
            except Exception:
                pass
        return conflicts


    @staticmethod
    def check_conflict(instructor_id, session_date, session_time, duration,
                       vehicle_id=None, exclude_id=None):
        """يبحث عن تعارض زمني للممرّن وكذلك للمركبة (إن وُجدت)."""
        conn = get_connection()
        # استعلام الممرّن
        inst_rows = conn.execute("""
            SELECT * FROM sessions
            WHERE instructor_id=? AND session_date=?
              AND id != COALESCE(?,0)
        """, (instructor_id, session_date, exclude_id or 0)).fetchall()

        # استعلام المركبة (إن اختيرت)
        veh_rows = []
        if vehicle_id:
            veh_rows = conn.execute("""
                SELECT * FROM sessions
                WHERE vehicle_id=? AND session_date=?
                  AND id != COALESCE(?,0)
            """, (vehicle_id, session_date, exclude_id or 0)).fetchall()
        conn.close()

        inst_conflicts = SessionDB._overlapping(
            [dict(r) for r in inst_rows], session_time, duration)
        veh_conflicts  = SessionDB._overlapping(
            [dict(r) for r in veh_rows],  session_time, duration)
        return inst_conflicts, veh_conflicts


SESSION_TYPE_OPTIONS = ["كرينو", "طريق", "كود (نظري)", "مناورة حرة"]
TIME_OPTIONS = [f"{h:02d}:{m:02d}" for h in range(7, 20) for m in (0, 30)]
DURATION_OPTIONS = ["30", "45", "60", "90", "120"]


class ExamResultDB:
    """طبقة الوصول لجدول نتائج الامتحانات."""

    @staticmethod
    def get_by_candidate(candidate_id):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM exam_results WHERE candidate_id=? ORDER BY exam_date DESC",
            (candidate_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(d):
        conn = get_connection()
        conn.execute(
            """INSERT INTO exam_results
               (candidate_id, exam_type, exam_date, result, score, notes)
               VALUES (?,?,?,?,?,?)""",
            (d['candidate_id'], d['exam_type'], d['exam_date'],
             d['result'], d.get('score', 0), d.get('notes', ''))
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(rid):
        conn = get_connection()
        conn.execute("DELETE FROM exam_results WHERE id=?", (rid,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_pass_rate_by_type():
        """معدل النجاح لكل نوع امتحان (نظري / تطبيقي)."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT exam_type,
                   COUNT(*) AS total,
                   SUM(CASE WHEN result='ناجح' THEN 1 ELSE 0 END) AS passed
            FROM exam_results
            GROUP BY exam_type
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_monthly_breakdown(year):
        """تفصيل شهري لنتائج الامتحانات في السنة المحددة."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT strftime('%m', exam_date) AS month,
                   exam_type,
                   COUNT(*) AS total,
                   SUM(CASE WHEN result='ناجح' THEN 1 ELSE 0 END) AS passed
            FROM exam_results
            WHERE strftime('%Y', exam_date) = ?
            GROUP BY month, exam_type
            ORDER BY month
        """, (str(year),)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# ============================================================================
#  مكونات الواجهة (UI Helpers)
# ============================================================================

def _clr_lighten(hex_color, amount=0.14):
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r = min(255, int(r + (255-r)*amount))
        g = min(255, int(g + (255-g)*amount))
        b = min(255, int(b + (255-b)*amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color

def _clr_darken(hex_color, amount=0.18):
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r,g,b = int(r*(1-amount)), int(g*(1-amount)), int(b*(1-amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


class ModernButton(tk.Button):
    """زر عصري مسطّح (Flat) بتأثير hover وضغط ناعمَين."""
    def __init__(self, parent, text="", command=None, color=COLOR_PRIMARY,
                 fg="white", icon="", width=None, size="normal", **kw):
        display = f"{icon}  {text}" if icon else text
        if size == "large":
            pady_v, padx_v, font_f = 12, 24, (FONT_FAMILY, 12, "bold")
        elif size == "small":
            pady_v, padx_v, font_f = 4,  10, (FONT_FAMILY, 9,  "bold")
        else:
            pady_v, padx_v, font_f = 8,  18, FONT_BOLD

        super().__init__(parent, text=display, command=command, font=font_f,
                         bg=color, fg=fg, relief="flat", bd=0,
                         padx=padx_v, pady=pady_v, cursor="hand2",
                         activebackground=_clr_darken(color, 0.14),
                         activeforeground="white",
                         highlightthickness=0, **kw)
        if width:
            self.configure(width=width)
        self._c  = color
        self._h  = _clr_lighten(color, 0.14)
        self._p  = _clr_darken(color, 0.18)
        self.bind("<Enter>",          self._on_enter)
        self.bind("<Leave>",          self._on_leave)
        self.bind("<ButtonPress-1>",  self._on_press)
        self.bind("<ButtonRelease-1>",self._on_release)

    def _on_enter(self, e):   self.configure(bg=self._h)
    def _on_leave(self, e):   self.configure(bg=self._c)
    def _on_press(self, e):   self.configure(bg=self._p)
    def _on_release(self, e):
        inside = self.winfo_containing(e.x_root, e.y_root) == self
        self.configure(bg=self._h if inside else self._c)

    # للتوافق مع الكود القديم الذي يستدعي _lighten/_darken كـ static
    @staticmethod
    def _lighten(hex_color, amount=0.15): return _clr_lighten(hex_color, amount)
    @staticmethod
    def _darken(hex_color, amount=0.2):  return _clr_darken(hex_color, amount)


def confirm_delete(name="هذا العنصر"):
    return messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف {name}؟")

def show_info(msg):  messagebox.showinfo("نجاح ✓", msg)
def show_error(msg): messagebox.showerror("خطأ ✗", msg)


def make_card(parent, padding=20):
    """بطاقة بيضاء بظل ناعم وزوايا احترافية."""
    outer = tk.Frame(parent, bg="#d1d9e6", padx=1, pady=1)
    mid   = tk.Frame(outer,  bg="#e8edf3", padx=1, pady=1)
    mid.pack(fill="both", expand=True)
    inner = tk.Frame(mid, bg=COLOR_CARD, padx=padding, pady=padding)
    inner.pack(fill="both", expand=True)
    return outer, inner


def section_title(parent, text, icon=""):
    """عنوان قسم مع أيقونة."""
    f = tk.Frame(parent, bg=COLOR_CARD)
    f.pack(fill="x", pady=(0, 12))
    lbl = tk.Label(f, text=f"{icon}  {text}" if icon else text,
                   font=(FONT_FAMILY, 13, "bold"), bg=COLOR_CARD,
                   fg=COLOR_PRIMARY, anchor="e")
    lbl.pack(side="right")
    line = tk.Frame(f, bg=COLOR_PRIMARY_LIGHT, height=2)
    line.pack(side="right", fill="x", expand=True, padx=(10, 0), pady=(8, 0))
    return f


def make_label(parent, text, bg=COLOR_CARD, fg=COLOR_TEXT, font=None):
    return tk.Label(parent, text=text, bg=bg, fg=fg,
                    font=font or FONT_MAIN, anchor="e")


def make_entry(parent, textvariable, width=24):
    e = tk.Entry(parent, textvariable=textvariable, font=FONT_MAIN,
                 bd=0, relief="flat", bg=COLOR_INPUT_BG, fg=COLOR_TEXT,
                 insertbackground=COLOR_PRIMARY, highlightthickness=1,
                 highlightbackground=COLOR_BORDER,
                 highlightcolor=COLOR_PRIMARY, width=width)
    e.configure(justify="right")
    return e


def make_combo(parent, textvariable, values, width=22, state="readonly"):
    c = ttk.Combobox(parent, textvariable=textvariable, values=values,
                     font=FONT_MAIN, width=width, state=state,
                     style="Modern.TCombobox", justify="right")
    return c


def create_treeview(parent, columns, headings, widths=None, height=15):
    frame = tk.Frame(parent, bg=COLOR_CARD)
    frame.pack(fill="both", expand=True, padx=4, pady=4)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height,
                        style="Modern.Treeview")
    for i, col in enumerate(columns):
        tree.heading(col, text=headings[i], anchor="center")
        tree.column(col, width=(widths[i] if widths else 120), anchor="center")
    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview,
                        style="Thin.Vertical.TScrollbar")
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview,
                        style="Thin.Horizontal.TScrollbar")
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    tree.tag_configure("oddrow",  background="#f8fafc")
    tree.tag_configure("evenrow", background=COLOR_CARD)
    return tree


def insert_zebra(tree, values_list):
    """يضيف صفوفاً للـ Treeview بألوان متناوبة."""
    for r in tree.get_children():
        tree.delete(r)
    for i, vals in enumerate(values_list):
        tag = "oddrow" if i % 2 else "evenrow"
        tree.insert("", "end", values=vals, tags=(tag,))


def stat_card(parent, title, value, icon, color, command=None):
    """بطاقة إحصائية ملونة قابلة للنقر."""
    hc = _clr_lighten(color, 0.12)
    card = tk.Frame(parent, bg=color, padx=20, pady=18,
                    cursor="hand2" if command else "")
    card.pack(side="right", fill="both", expand=True, padx=6)
    top = tk.Frame(card, bg=color); top.pack(fill="x")
    icon_lbl = tk.Label(top, text=icon, font=(FONT_FAMILY, 26),
                        bg=color, fg="white"); icon_lbl.pack(side="right")
    title_lbl = tk.Label(top, text=title, font=(FONT_FAMILY, 10, "bold"),
                         bg=color, fg="white", anchor="e")
    title_lbl.pack(side="right", padx=8)
    val_lbl = tk.Label(card, text=value, font=(FONT_FAMILY, 20, "bold"),
                       bg=color, fg="white", anchor="e")
    val_lbl.pack(fill="x", pady=(6, 0))
    if command:
        arr_lbl = tk.Label(card, text="← عرض التفاصيل",
                           font=(FONT_FAMILY, 8), bg=color, fg="white",
                           anchor="w"); arr_lbl.pack(fill="x", pady=(4, 0))
        all_w = [card, top, icon_lbl, title_lbl, val_lbl, arr_lbl]
        def _enter(e):
            for w in all_w: w.configure(bg=hc)
        def _leave(e):
            for w in all_w: w.configure(bg=color)
        for w in all_w:
            w.bind("<Enter>", _enter); w.bind("<Leave>", _leave)
            w.bind("<Button-1>", lambda e: command())
    return card


# ============================================================================
#  واجهة: لوحة المعلومات (Dashboard)
# ============================================================================

class DashboardFrame(tk.Frame):
    def __init__(self, parent, navigate_cb=None):
        super().__init__(parent, bg=COLOR_BG)
        self._navigate_cb = navigate_cb
        self._build()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=20)
        wrap.pack(fill="both", expand=True)

        title = tk.Label(wrap, text="📊  لوحة المعلومات",
                         font=(FONT_FAMILY, 20, "bold"),
                         bg=COLOR_BG, fg=COLOR_HEADER, anchor="e")
        title.pack(fill="x", pady=(0, 5))
        sub = tk.Label(wrap, text="نظرة شاملة على نشاط المدرسة",
                       font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT, anchor="e")
        sub.pack(fill="x", pady=(0, 20))

        cands = CandidateDB.get_all()
        instructors = InstructorDB.get_all()
        y = str(date.today().year)
        total_pay = PaymentDB.get_total_by_year(y)
        total_exp = ExpenseDB.get_total_by_year(y)
        profit = total_pay - total_exp

        # دوال التنقل (تعمل فقط إذا مُرّر navigate_cb)
        nav = self._navigate_cb
        go_cands  = (lambda: nav(2)) if nav else None
        go_insts  = (lambda: nav(3)) if nav else None
        go_pay    = (lambda: nav(6)) if nav else None
        go_exp    = (lambda: nav(7)) if nav else None

        # صف البطاقات الإحصائية
        stats_row = tk.Frame(wrap, bg=COLOR_BG)
        stats_row.pack(fill="x", pady=(0, 20))
        stat_card(stats_row, "المترشحون", str(len(cands)), "👥", COLOR_PRIMARY,
                  command=go_cands)
        stat_card(stats_row, "الممرنون",  str(len(instructors)), "🚗", COLOR_PURPLE,
                  command=go_insts)
        stat_card(stats_row, "المدفوعات (دج)", f"{total_pay:,.0f}", "💰", COLOR_SUCCESS,
                  command=go_pay)
        stat_card(stats_row, "المصاريف (دج)", f"{total_exp:,.0f}", "💸", COLOR_DANGER,
                  command=go_exp)

        # صف الأرباح الكبير
        profit_color = COLOR_SUCCESS if profit >= 0 else COLOR_DANGER
        pf = tk.Frame(wrap, bg=profit_color, padx=24, pady=20)
        pf.pack(fill="x", pady=(0, 20))
        tk.Label(pf, text=f"💎  الأرباح الصافية لسنة {y}",
                 font=(FONT_FAMILY, 14, "bold"),
                 bg=profit_color, fg="white", anchor="e").pack(side="right")
        tk.Label(pf, text= f"{profit:,.0f} دج",
                 font=(FONT_FAMILY, 22, "bold"),
                 bg=profit_color, fg="white", anchor="w").pack(side="left")

        # إحصائيات النجاح (Success Rates) — مبنية على سجل الامتحانات الفعلي
        exam_stats = {s['stage_type']: s for s in ExamAttemptsDB.get_stats_by_stage()}
        rates_frame = tk.Frame(wrap, bg=COLOR_BG)
        rates_frame.pack(fill="x", pady=(0, 20))

        for stage_code, label in STAGE_LABELS.items():
            es = exam_stats.get(stage_code, {'total': 0, 'passed': 0})
            total  = es.get('total',  0) or 0
            passed = es.get('passed', 0) or 0
            rate   = (passed / total * 100) if total > 0 else 0

            color = COLOR_SUCCESS if rate >= 50 else COLOR_WARNING
            if total == 0: color = COLOR_TEXT_LIGHT

            sc = tk.Frame(rates_frame, bg=COLOR_CARD, padx=15, pady=10,
                          highlightthickness=1, highlightbackground=COLOR_BORDER)
            sc.pack(side="right", fill="both", expand=True, padx=5)

            tk.Label(sc, text=label, font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="e")
            tk.Label(sc, text=f"{rate:.1f}%  نجاح", font=(FONT_FAMILY, 16, "bold"),
                     bg=COLOR_CARD, fg=color).pack(anchor="e")
            tk.Label(sc,
                     text=f"المحاولات: {total}  |  ناجح: {passed}  |  راسب: {total - passed}",
                     font=FONT_TINY, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT).pack(anchor="e")

        # التنبيهات والإشعارات (Notifications & Alerts)
        v_alerts = VehicleDB.get_alerts()
        unpaid = [c for c in cands if (sum(p['amount'] for p in PaymentDB.get_by_candidate(c['id'])) < c['total_amount'])]
        
        if v_alerts or unpaid:
            no_outer, no_body = make_card(wrap, padding=15)
            no_outer.pack(fill="x", pady=(0, 20))
            section_title(no_body, "تنبيهات وإشعارات هامة", icon="🔔")
            
            for v in v_alerts:
                msg = f"مركبة {v['model']} ({v['plate_number']}): قرب انتهاء التأمين/المراقبة"
                tk.Label(no_body, text=msg, font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_DANGER, anchor="e").pack(fill="x")
            
            if unpaid:
                msg = f"هناك {len(unpaid)} مترشحين لم يسددوا كامل المستحقات."
                tk.Label(no_body, text=msg, font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_WARNING, anchor="e").pack(fill="x")


        # ── حصص اليوم والأسبوع ──
        today_sessions = []
        week_sessions  = []
        try:
            today_sessions = SessionDB.get_today()
            week_sessions  = SessionDB.get_week()
        except Exception:
            pass

        sched_outer, sched_body = make_card(wrap, padding=15)
        sched_outer.pack(fill="x", pady=(0, 16))
        sh = tk.Frame(sched_body, bg=COLOR_CARD)
        sh.pack(fill="x", pady=(0, 8))
        section_title(sched_body, f"حصص اليوم  ({len(today_sessions)})", icon="📅")

        if today_sessions:
            sess_tree = create_treeview(sched_body,
                ("time", "candidate", "instructor", "type", "dur"),
                ("الوقت", "المترشح", "الممرن", "النوع", "المدة(د)"),
                (80, 180, 160, 110, 70), height=min(len(today_sessions), 5))
            rows_s = [(s['session_time'], s['candidate_name'],
                       s['instructor_name'], s['session_type'],
                       str(s['duration']))
                      for s in today_sessions]
            insert_zebra(sess_tree, rows_s)
        else:
            tk.Label(sched_body, text="لا توجد حصص مجدولة لهذا اليوم",
                     font=FONT_MAIN, bg=COLOR_CARD,
                     fg=COLOR_TEXT_LIGHT, anchor="e").pack(fill="x", pady=6)

        # أول حصة قادمة (غداً+)
        future = [s for s in week_sessions
                  if s['session_date'] > date.today().strftime('%Y-%m-%d')]
        if future:
            nxt = future[0]
            nxt_bar = tk.Frame(sched_body, bg=COLOR_PRIMARY_LIGHT,
                               padx=12, pady=8)
            nxt_bar.pack(fill="x", pady=(8, 0))
            tk.Label(nxt_bar,
                     text=f"⏭  أقرب حصة قادمة:  {nxt['session_date']}  {nxt['session_time']}  —  {nxt['candidate_name']}  /  {nxt['instructor_name']}",
                     font=FONT_BOLD, bg=COLOR_PRIMARY_LIGHT,
                     fg=COLOR_PRIMARY, anchor="e").pack(fill="x")

        # المترشحون الأخيرون
        outer, body = make_card(wrap)
        outer.pack(fill="both", expand=True)
        section_title(body, "المترشحون المسجلون حديثاً", icon="🆕")

        tree = create_treeview(body,
            ("name", "phone", "license", "instructor", "amount", "date"),
            ("الاسم الكامل", "الهاتف", "نوع الرخصة", "الممرن",
             "المبلغ الإجمالي", "تاريخ التسجيل"),
            (180, 120, 100, 160, 130, 130), height=6)

        latest = sorted(cands, key=lambda x: x.get('registration_date', ''),
                        reverse=True)[:10]
        rows = [(f"{c['last_name']} {c['first_name']}", c['phone'], c['license_type'],
                 c.get('instructor_name', '—') or '—',
                 f"{c['total_amount']:,.0f} دج", c['registration_date'])
                for c in latest]
        insert_zebra(tree, rows)


# ============================================================================
#  واجهة: معلومات المدرسة
# ============================================================================

class SchoolInfoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.vars = {}
        self._build()
        self._load()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=30, pady=20)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="🏫  معلومات المدرسة",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=(0, 5))
        tk.Label(wrap, text="بيانات المدرسة الرسمية المستعملة في الوثائق المطبوعة",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(fill="x", pady=(0, 20))

        outer, card = make_card(wrap, padding=30)
        outer.pack(fill="both", expand=True, padx=80)

        section_title(card, "البيانات الأساسية", icon="📋")

        # إعادة ترتيب الحقول لجعل المعلومات الأساسية (العنوان والهاتف) في الأعلى
        fields = [
            ("اسم المدرسة", "name"), ("رقم الهاتف", "phone"),
            ("العنوان", "address"), ("رقم السجل التجاري", "commercial_register"),
            ("رقم الاعتماد", "accreditation_number"), ("NIF", "nif"),
            ("NIS", "nis"), ("N° Article", "article_number")
        ]
        bf = tk.Frame(card, bg=COLOR_CARD)
        bf.pack(side="bottom", fill="x", pady=(20, 0))
        ModernButton(bf, "حفظ المعلومات", self._save,
                     icon="💾", color=COLOR_SUCCESS).pack(side="right", padx=5)
        ModernButton(bf, "إعادة تحميل", self._load,
                     icon="🔄", color=COLOR_TEXT_LIGHT).pack(side="right", padx=5)

        grid = tk.Frame(card, bg=COLOR_CARD)
        grid.pack(fill="x", expand=True)
        
        # توزيع الحقول بشكل ذكي وبدون تداخل
        # سنقوم بوضع اسم المدرسة والهاتف في الصف الأول
        # ثم العنوان في الصف الثاني (يأخذ العرض كاملاً)
        # ثم بقية الحقول في عمودين
        
        # 1. الصف الأول: اسم المدرسة + الهاتف
        f_name = tk.Frame(grid, bg=COLOR_CARD)
        f_name.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        grid.columnconfigure(0, weight=1)
        make_label(f_name, "اسم المدرسة", font=FONT_BOLD).pack(anchor="e")
        v_name = tk.StringVar()
        self.vars["name"] = v_name
        make_entry(f_name, v_name, width=32).pack(fill="x", ipady=4, pady=(2, 0))
        
        f_phone = tk.Frame(grid, bg=COLOR_CARD)
        f_phone.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        grid.columnconfigure(1, weight=1)
        make_label(f_phone, "رقم الهاتف", font=FONT_BOLD).pack(anchor="e")
        v_phone = tk.StringVar()
        self.vars["phone"] = v_phone
        make_entry(f_phone, v_phone, width=32).pack(fill="x", ipady=4, pady=(2, 0))
        
        # 2. الصف الثاني: العنوان (كامل العرض)
        f_addr = tk.Frame(grid, bg=COLOR_CARD)
        f_addr.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        make_label(f_addr, "العنوان", font=FONT_BOLD).pack(anchor="e")
        v_addr = tk.StringVar()
        self.vars["address"] = v_addr
        make_entry(f_addr, v_addr, width=70).pack(fill="x", ipady=4, pady=(2, 0))
        
        # 3. بقية الحقول (CR, Accreditation, NIF, NIS, Article)
        other_fields = [
            ("رقم السجل التجاري", "commercial_register"), ("رقم الاعتماد", "accreditation_number"),
            ("NIF", "nif"), ("NIS", "nis"),
            ("N° Article", "article_number")
        ]
        
        for i, (label, key) in enumerate(other_fields):
            row = (i // 2) + 2
            col = i % 2
            
            cell = tk.Frame(grid, bg=COLOR_CARD)
            cell.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
            make_label(cell, label, font=FONT_BOLD).pack(anchor="e")
            v = tk.StringVar()
            self.vars[key] = v
            make_entry(cell, v, width=32).pack(fill="x", ipady=4, pady=(2, 0))

    def _load(self):
        d = SchoolInfoDB.get()
        for k, v in self.vars.items():
            v.set(d.get(k, ""))

    def _save(self):
        if not self.vars["name"].get().strip():
            show_error("يرجى إدخال اسم المدرسة")
            return
        SchoolInfoDB.update({k: v.get().strip() for k, v in self.vars.items()})
        show_info("تم حفظ معلومات المدرسة بنجاح")


# ============================================================================
#  نافذة منبثقة لإضافة/تعديل المترشحين (الحل لمشكلة الحقول)
# ============================================================================

class CandidateDialog(tk.Toplevel):
    def __init__(self, parent, on_save, candidate=None):
        super().__init__(parent)
        self.on_save = on_save
        self.candidate = candidate
        self.vars = {}
        self.born_abroad_var = tk.IntVar(value=0)
        self.title("تعديل بيانات المترشح" if candidate else "تسجيل مترشح جديد")
        self.geometry("980x720")
        self.minsize(880, 640)
        self.resizable(True, True)
        self.configure(bg=COLOR_BG)
        self.transient(parent)
        self.grab_set()
        self._build()
        if candidate:
            self._fill(candidate)
        self._toggle_abroad_fields()

    def _instructor_options(self):
        instructors = InstructorDB.get_all()
        self.instructor_map = {f"{i['last_name']} {i['first_name']}": i['id']
                                for i in instructors}
        self.instructor_map[""] = None
        return [""] + list(self.instructor_map.keys())[:-1]

    def _make_field(self, parent, label, key, kind="entry", values=None,
                    width=28, row=0, col=0, colspan=1):
        cell = tk.Frame(parent, bg=COLOR_CARD)
        cell.grid(row=row, column=col, columnspan=colspan,
                  sticky="ew", padx=10, pady=5)
        make_label(cell, label, font=FONT_BOLD).pack(anchor="e")
        v = tk.StringVar()
        self.vars[key] = v
        if kind == "combo":
            w = make_combo(cell, v, values or [], width=width)
        else:
            w = make_entry(cell, v, width=width + 2)
        w.pack(fill="x", ipady=4, pady=(2, 0))
        return v, w, cell

    def _build(self):
        # ===== رأس النافذة =====
        head = tk.Frame(self, bg=COLOR_PRIMARY, pady=16, padx=20)
        head.pack(fill="x", side="top")
        title_text = "✏️  تعديل بيانات المترشح" if self.candidate else "➕  تسجيل مترشح جديد"
        tk.Label(head, text=title_text, font=(FONT_FAMILY, 15, "bold"),
                 bg=COLOR_PRIMARY, fg="white", anchor="e").pack(side="right")
        tk.Label(head, text="استمارة الترشح لاجتياز امتحانات رخصة السياقة",
                 font=(FONT_FAMILY, 10), bg=COLOR_PRIMARY, fg="#c7d2fe",
                 anchor="w").pack(side="left")

        # ===== شريط الأزرار (يُعبَّأ أولاً ليبقى ظاهراً دائماً) =====
        bf = tk.Frame(self, bg=COLOR_BG, pady=10)
        bf.pack(side="bottom", fill="x", padx=20)
        tk.Frame(bf, bg=COLOR_BORDER, height=1).pack(fill="x", pady=(0, 10))
        ModernButton(bf, "إلغاء", self.destroy, icon="✗",
                     color=COLOR_TEXT_LIGHT).pack(side="left", padx=5)
        save_lbl = "💾  حفظ التعديل" if self.candidate else "✅  تسجيل المترشح"
        ModernButton(bf, save_lbl, self._save,
                     color=COLOR_SUCCESS, size="large").pack(side="right", padx=5)

        # ===== المحتوى (يملأ الفراغ المتبقي) =====
        wrap = tk.Frame(self, bg=COLOR_BG, padx=12, pady=8)
        wrap.pack(fill="both", expand=True)

        nb = ttk.Notebook(wrap, style="Modern.TNotebook")
        nb.pack(fill="both", expand=True)

        # ══════════════════════════════════════════════
        # التبويب 1: بيانات الملف والمعلومات الشخصية
        # ══════════════════════════════════════════════
        tab1 = tk.Frame(nb, bg=COLOR_CARD, padx=18, pady=12)
        nb.add(tab1, text="👤  البيانات الشخصية")

        # -- قسم: بيانات الملف (رقم الملف + تاريخ الإيداع) --
        section_title(tab1, "بيانات الملف", icon="📁")
        gf = tk.Frame(tab1, bg=COLOR_CARD)
        gf.pack(fill="x")
        gf.columnconfigure(0, weight=1); gf.columnconfigure(1, weight=1)
        self._make_field(gf, "رقم الملف",           "file_number", row=0, col=0)
        self._make_field(gf, "تاريخ إيداع الملف",   "file_date",   row=0, col=1)

        # -- قسم: المعلومات الشخصية --
        section_title(tab1, "المعلومات الشخصية", icon="📝")
        g1 = tk.Frame(tab1, bg=COLOR_CARD)
        g1.pack(fill="both", expand=True)
        g1.columnconfigure(0, weight=1); g1.columnconfigure(1, weight=1)

        personal = [
            ("اللقب / Nom *",               "last_name",          "entry", None),
            ("الاسم / Prénom *",             "first_name",         "entry", None),
            ("الجنس",                        "gender",             "combo", GENDER_OPTIONS),
            ("الحالة العائلية",              "marital_status",     "combo", MARITAL_OPTIONS),
            ("رقم التعريف الوطني (NIN)",     "national_id",        "entry", None),
            ("فصيلة الدم",                   "blood_type",         "combo", BLOOD_TYPE_OPTIONS),
            ("اسم الأب",                     "father_name",        "entry", None),
            ("اسم ولقب الأم",                "mother_name",        "entry", None),
            ("رقم الهاتف",                   "phone",              "entry", None),
            ("الجنسية الأصلية",              "nationality",        "entry", None),
            ("الجنسية المكتسبة (إن وجدت)",  "second_nationality", "entry", None),
            ("إعاقة / إصابة (إن وجدت)",     "disability",         "entry", None),
        ]
        for i, (lbl, key, kind, vals) in enumerate(personal):
            self._make_field(g1, lbl, key, kind, vals, row=i // 2, col=i % 2)

        # ══════════════════════════════════════════════
        # التبويب 2: الميلاد والعنوان
        # ══════════════════════════════════════════════
        tab2 = tk.Frame(nb, bg=COLOR_CARD, padx=18, pady=12)
        nb.add(tab2, text="🎂  الميلاد والعنوان")

        section_title(tab2, "تاريخ ومكان الميلاد", icon="🎂")

        # خيار: مولود بالخارج
        ab_box = tk.Frame(tab2, bg=COLOR_PRIMARY_LIGHT, padx=12, pady=8)
        ab_box.pack(fill="x", pady=(0, 8))
        tk.Checkbutton(ab_box,
                       text="  مولود(ة) بالخارج — تفعيل حقول بلد الميلاد والسفارة/القنصلية",
                       variable=self.born_abroad_var,
                       command=self._toggle_abroad_fields,
                       font=FONT_BOLD, bg=COLOR_PRIMARY_LIGHT,
                       fg=COLOR_PRIMARY_DARK, activebackground=COLOR_PRIMARY_LIGHT,
                       selectcolor=COLOR_WHITE, anchor="e").pack(anchor="e")

        g2 = tk.Frame(tab2, bg=COLOR_CARD)
        g2.pack(fill="x")
        g2.columnconfigure(0, weight=1); g2.columnconfigure(1, weight=1)

        self._make_field(g2, "تاريخ الميلاد (YYYY-MM-DD)",
                         "birth_date", "entry", row=0, col=0)
        self._make_field(g2, "بلد الميلاد",
                         "birth_country", "entry", row=0, col=1)
        self._make_field(g2, "بلدية / مدينة الميلاد",
                         "birth_place_commune", "entry", row=1, col=0)
        self._make_field(g2, "ولاية الميلاد",
                         "birth_place_wilaya", "entry", row=1, col=1)

        _, _w_emb, c_emb = self._make_field(
            g2, "السفارة (للمولودين بالخارج)", "embassy", "entry", row=2, col=0)
        _, _w_con, c_con = self._make_field(
            g2, "القنصلية أو مكتب التسجيل",   "consulate","entry", row=2, col=1)
        self._abroad_widgets = [c_emb, c_con]

        # -- العنوان الحالي --
        section_title(tab2, "العنوان الحالي", icon="🏠")
        g_addr = tk.Frame(tab2, bg=COLOR_CARD)
        g_addr.pack(fill="x")
        g_addr.columnconfigure(0, weight=1); g_addr.columnconfigure(1, weight=1)
        self._make_field(g_addr, "بلدية / مدينة السكن",
                         "address_commune", "entry", row=0, col=0)
        self._make_field(g_addr, "ولاية السكن",
                         "address_wilaya",  "entry", row=0, col=1)

        addr_cell = tk.Frame(tab2, bg=COLOR_CARD)
        addr_cell.pack(fill="x", padx=10, pady=4)
        make_label(addr_cell, "العنوان الكامل (الشارع، الحي...)", font=FONT_BOLD).pack(anchor="e")
        v_addr = tk.StringVar(); self.vars["current_address"] = v_addr
        make_entry(addr_cell, v_addr, width=80).pack(fill="x", ipady=5, pady=(2, 0))

        # ══════════════════════════════════════════════
        # التبويب 3: التسجيل والتكوين والأصناف السابقة
        # ══════════════════════════════════════════════
        tab3 = tk.Frame(nb, bg=COLOR_CARD, padx=18, pady=12)
        nb.add(tab3, text="🚗  التسجيل والتكوين")

        # -- نوع الرخصة --
        section_title(tab3, "الصنف المطلوب ونوع الرخصة", icon="🎯")
        lic_card = tk.Frame(tab3, bg=COLOR_PRIMARY_LIGHT, padx=14, pady=10)
        lic_card.pack(fill="x", pady=(0, 10))
        tk.Label(lic_card, text="🎯  نوع الرخصة المطلوبة *",
                 font=(FONT_FAMILY, 12, "bold"),
                 bg=COLOR_PRIMARY_LIGHT, fg=COLOR_PRIMARY_DARK, anchor="e").pack(anchor="e")
        v_lic = tk.StringVar(); self.vars["license_type"] = v_lic
        make_combo(lic_card, v_lic, LICENSE_OPTIONS, width=20).pack(
            anchor="e", pady=(4, 2), ipady=4)
        tk.Label(lic_card, text="A: دراجة نارية  |  B: سيارة  |  C: شاحنة  |  D: حافلة  |  E: مقطورة",
                 font=FONT_SMALL, bg=COLOR_PRIMARY_LIGHT, fg=COLOR_PRIMARY_DARK, anchor="e").pack(anchor="e")

        # -- الممرن والمبالغ --
        section_title(tab3, "الممرن والمبالغ المالية", icon="💰")
        opts = self._instructor_options()
        g3 = tk.Frame(tab3, bg=COLOR_CARD)
        g3.pack(fill="x")
        g3.columnconfigure(0, weight=1); g3.columnconfigure(1, weight=1)

        self._make_field(g3, "الممرن المُكلَّف",
                         "instructor_name", "combo", opts, row=0, col=0)
        self._make_field(g3, "المبلغ الإجمالي للتكوين (دج) *",
                         "total_amount", "entry", row=0, col=1)
        if not self.candidate:
            self._make_field(g3, "المبلغ المدفوع عند التسجيل (دج)",
                             "initial_payment", "entry", row=1, col=0)

        # -- الأصناف المتحصل عليها من قبل --
        section_title(tab3, "الأصناف المتحصل عليها من قبل", icon="📋")
        prev_note = tk.Frame(tab3, bg="#fffbeb", padx=10, pady=6)
        prev_note.pack(fill="x", pady=(0, 6))
        tk.Label(prev_note,
                 text="أدخل رموز الأصناف القديمة مفصولة بفاصلة — مثال:  B, A1, C1",
                 font=FONT_SMALL, bg="#fffbeb", fg="#92400e", anchor="e").pack(anchor="e")
        prev_cell = tk.Frame(tab3, bg=COLOR_CARD)
        prev_cell.pack(fill="x", padx=10, pady=2)
        make_label(prev_cell, "الأصناف السابقة (مثال: A, B, C1)", font=FONT_BOLD).pack(anchor="e")
        v_prev = tk.StringVar(); self.vars["previous_licenses"] = v_prev
        make_entry(prev_cell, v_prev, width=60).pack(fill="x", ipady=4, pady=(2, 0))

        # ══════════════════════════════════════════════
        # التبويب 4: نتائج الامتحانات (تعديل فقط)
        # ══════════════════════════════════════════════
        tab4 = tk.Frame(nb, bg=COLOR_CARD, padx=18, pady=12)
        nb.add(tab4, text="📊  نتائج الامتحانات")

        if self.candidate:
            # -- ملخص الإحصائيات --
            self._exam_stats_frame = tk.Frame(tab4, bg=COLOR_BG)
            self._exam_stats_frame.pack(fill="x", pady=(0, 10))

            # -- جدول النتائج --
            section_title(tab4, "سجل الامتحانات", icon="📋")
            tree_outer, tree_card = make_card(tab4, padding=8)
            tree_outer.pack(fill="both", expand=True, pady=(0, 8))
            self._exam_tree = create_treeview(
                tree_card,
                ("id", "exam_type", "exam_date", "result", "score", "notes"),
                ("رقم", "نوع الامتحان", "التاريخ", "النتيجة", "الدرجة", "ملاحظات"),
                (0, 120, 120, 90, 80, 220),
                height=8
            )
            self._exam_tree.column("id", width=0, stretch=False)

            # -- أزرار الإضافة والحذف --
            btn_bar = tk.Frame(tab4, bg=COLOR_CARD)
            btn_bar.pack(fill="x")
            ModernButton(btn_bar, "إضافة نتيجة", self._add_exam_result,
                         icon="➕", color=COLOR_SUCCESS).pack(side="right", padx=4)
            ModernButton(btn_bar, "حذف المحدد", self._delete_exam_result,
                         icon="🗑️", color=COLOR_DANGER).pack(side="right", padx=4)

            self._load_exam_results()
        else:
            tk.Label(tab4,
                     text="احفظ بيانات المترشح أولاً، ثم ارجع لهذا التبويب لإضافة نتائج الامتحانات.",
                     font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT,
                     wraplength=500, justify="right", anchor="center").pack(
                         expand=True, anchor="center")

        # ══════════════════════════════════════════════
        # القيم الافتراضية
        # ══════════════════════════════════════════════
        self.vars["nationality"].set("جزائرية")
        self.vars["birth_country"].set("الجزائر")
        self.vars["license_type"].set("B")

    def _toggle_abroad_fields(self):
        enabled = self.born_abroad_var.get() == 1
        for cell in getattr(self, "_abroad_widgets", []):
            for child in cell.winfo_children():
                try:
                    if isinstance(child, tk.Entry):
                        child.config(state="normal" if enabled else "disabled",
                                     bg=COLOR_INPUT_BG if enabled else "#e2e8f0")
                except Exception:
                    pass

    def _fill(self, c):
        for k, v in self.vars.items():
            if k == "instructor_name":
                inst = InstructorDB.get(c.get("instructor_id")) if c.get("instructor_id") else None
                v.set(f"{inst['last_name']} {inst['first_name']}" if inst else "")
            else:
                v.set(str(c.get(k, "")) if c.get(k) is not None else "")
        self.born_abroad_var.set(int(c.get("is_born_abroad") or 0))

    # ── نتائج الامتحانات ──────────────────────────────────────────────────────
    def _load_exam_results(self):
        if not self.candidate:
            return
        cid = self.candidate['id']
        rows = ExamResultDB.get_by_candidate(cid)

        # --- ملخص الإحصائيات ---
        for w in self._exam_stats_frame.winfo_children():
            w.destroy()

        stats = {}
        for r in rows:
            t = r['exam_type']
            stats.setdefault(t, {"total": 0, "passed": 0})
            stats[t]["total"]  += 1
            if r["result"] == "ناجح":
                stats[t]["passed"] += 1

        for etype in EXAM_TYPE_OPTIONS:
            s = stats.get(etype, {"total": 0, "passed": 0})
            total  = s["total"]
            passed = s["passed"]
            failed = total - passed
            pct    = int(passed / total * 100) if total else 0
            color  = COLOR_SUCCESS if pct >= 50 else (COLOR_WARNING if total == 0 else COLOR_DANGER)
            card   = tk.Frame(self._exam_stats_frame, bg=color,
                              padx=14, pady=10, relief="flat")
            card.pack(side="right", padx=6)
            tk.Label(card, text=f"امتحان {etype}",
                     font=FONT_BOLD, bg=color, fg="white").pack()
            tk.Label(card, text=f"{passed}/{total}  ({pct}%  ناجح)",
                     font=(FONT_FAMILY, 10), bg=color, fg="white").pack()
            tk.Label(card, text=f"✅ {passed}  ❌ {failed}  |  محاولات: {total}",
                     font=FONT_TINY, bg=color, fg="white").pack()

        # --- ملء الجدول ---
        values = [
            (r['id'], r['exam_type'], r['exam_date'],
             r['result'], f"{r['score']:g}" if r['score'] else "—",
             r['notes'] or "")
            for r in rows
        ]
        insert_zebra(self._exam_tree, values)

        # لون النتيجة (ناجح = أخضر، راسب = أحمر)
        for item in self._exam_tree.get_children():
            vals = self._exam_tree.item(item, "values")
            if vals and vals[3] == "ناجح":
                self._exam_tree.item(item, tags=("pass",))
            else:
                self._exam_tree.item(item, tags=("fail",))
        self._exam_tree.tag_configure("pass", foreground=COLOR_SUCCESS)
        self._exam_tree.tag_configure("fail", foreground=COLOR_DANGER)

    def _add_exam_result(self):
        if not self.candidate:
            return
        def on_save(data):
            ExamResultDB.add(data)
            self._load_exam_results()
            show_info("تمت إضافة النتيجة بنجاح")
        ExamResultDialog(self, self.candidate['id'], on_save=on_save)

    def _delete_exam_result(self):
        if not self.candidate:
            return
        sel = self._exam_tree.selection()
        if not sel:
            show_error("يرجى تحديد نتيجة من الجدول"); return
        rid = self._exam_tree.item(sel[0])['values'][0]
        if confirm_delete("هذه النتيجة"):
            ExamResultDB.delete(rid)
            self._load_exam_results()
            show_info("تم حذف النتيجة")

    def _save(self):
        try:
            total = float(self.vars["total_amount"].get().replace(",", ".").replace(" ", "") or 0)
        except ValueError:
            total = 0

        initial = 0
        if "initial_payment" in self.vars:
            try:
                initial = float(self.vars["initial_payment"].get().replace(",", ".").replace(" ", "") or 0)
            except ValueError:
                initial = 0

        instr = self.instructor_map.get(self.vars["instructor_name"].get())

        text_keys = ["first_name", "last_name", "birth_date", "birth_place_commune",
                     "birth_place_wilaya", "father_name", "mother_name", "phone",
                     "disability", "previous_licenses", "national_id",
                     "second_nationality", "current_address", "embassy", "consulate",
                     "file_number", "file_date", "address_commune", "address_wilaya"]
        d = {k: self.vars[k].get().strip() for k in text_keys}
        for k in ["gender", "marital_status", "blood_type", "license_type"]:
            d[k] = self.vars[k].get()
        d["nationality"]    = self.vars["nationality"].get().strip() or "جزائرية"
        d["birth_country"]  = self.vars["birth_country"].get().strip() or "الجزائر"
        d["instructor_id"]  = instr
        d["total_amount"]   = total
        d["is_born_abroad"] = self.born_abroad_var.get()
        if not self.candidate:
            d["initial_payment"] = initial

        if not d["first_name"] or not d["last_name"]:
            show_error("الاسم واللقب إلزاميان"); return
        if not d["license_type"]:
            show_error("يرجى تحديد نوع الرخصة المطلوبة"); return
        if d["is_born_abroad"] and not (d["embassy"] or d["consulate"]):
            if not messagebox.askyesno("تأكيد",
                "حدّدت أن المترشح مولود بالخارج لكن لم تُدخل السفارة/القنصلية.\nهل تريد المتابعة؟"):
                return

        self.on_save(d)
        self.destroy()


# ============================================================================
#  نافذة: إضافة نتيجة امتحان
# ============================================================================

class ExamResultDialog(tk.Toplevel):
    """نافذة إضافة نتيجة امتحان لمترشح محدد."""

    def __init__(self, parent, candidate_id, on_save):
        super().__init__(parent)
        self.candidate_id = candidate_id
        self.on_save = on_save
        self.title("إضافة نتيجة امتحان")
        self.geometry("480x400")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.transient(parent)
        self.grab_set()
        self._build()

    def _build(self):
        head = tk.Frame(self, bg=COLOR_PRIMARY, pady=14, padx=20)
        head.pack(fill="x")
        tk.Label(head, text="📝  إضافة نتيجة امتحان",
                 font=(FONT_FAMILY, 14, "bold"),
                 bg=COLOR_PRIMARY, fg="white", anchor="e").pack(side="right")

        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)
        wrap.columnconfigure(0, weight=1); wrap.columnconfigure(1, weight=1)

        def lbl_entry(row, col, text, var, kind="entry", values=None, colspan=1):
            f = tk.Frame(wrap, bg=COLOR_BG)
            f.grid(row=row, column=col, columnspan=colspan,
                   sticky="ew", padx=8, pady=6)
            tk.Label(f, text=text, font=FONT_BOLD, bg=COLOR_BG,
                     fg=COLOR_TEXT, anchor="e").pack(anchor="e")
            if kind == "combo":
                w = make_combo(f, var, values or [], width=22)
            else:
                w = make_entry(f, var, width=24)
            w.pack(fill="x", ipady=5, pady=(2, 0))

        self.v_type   = tk.StringVar(value=EXAM_TYPE_OPTIONS[0])
        self.v_date   = tk.StringVar(value=str(date.today()))
        self.v_result = tk.StringVar(value=EXAM_RESULT_OPTIONS[0])
        self.v_score  = tk.StringVar(value="")
        self.v_notes  = tk.StringVar(value="")

        lbl_entry(0, 0, "نوع الامتحان *",         self.v_type,   "combo", EXAM_TYPE_OPTIONS)
        lbl_entry(0, 1, "تاريخ الامتحان (YYYY-MM-DD) *", self.v_date, "entry")
        lbl_entry(1, 0, "النتيجة *",               self.v_result, "combo", EXAM_RESULT_OPTIONS)
        lbl_entry(1, 1, "الدرجة / العلامة (اختياري)", self.v_score, "entry")
        lbl_entry(2, 0, "ملاحظات (اختياري)",       self.v_notes,  "entry", colspan=2)

        bf = tk.Frame(self, bg=COLOR_BG, pady=10)
        bf.pack(side="bottom", fill="x", padx=20)
        tk.Frame(bf, bg=COLOR_BORDER, height=1).pack(fill="x", pady=(0, 8))
        ModernButton(bf, "إلغاء", self.destroy,
                     icon="✗", color=COLOR_TEXT_LIGHT).pack(side="left", padx=5)
        ModernButton(bf, "✅  حفظ النتيجة", self._save,
                     color=COLOR_SUCCESS, size="large").pack(side="right", padx=5)

    def _save(self):
        exam_date = self.v_date.get().strip()
        exam_type = self.v_type.get()
        result    = self.v_result.get()
        if not exam_type or not result:
            show_error("نوع الامتحان والنتيجة إلزاميان"); return
        try:
            datetime.strptime(exam_date, "%Y-%m-%d")
        except ValueError:
            show_error("صيغة التاريخ غير صحيحة. استخدم: YYYY-MM-DD"); return
        try:
            score = float(self.v_score.get().replace(",", ".") or 0)
        except ValueError:
            score = 0
        self.on_save({
            "candidate_id": self.candidate_id,
            "exam_type":    exam_type,
            "exam_date":    exam_date,
            "result":       result,
            "score":        score,
            "notes":        self.v_notes.get().strip(),
        })
        self.destroy()


# ============================================================================
#  واجهة: المترشحون (مُصلَحة بالكامل)
# ============================================================================

class CandidatesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_id = None
        self._build()
        self._load_list()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)

        # رأس الصفحة + شريط الأدوات
        head = tk.Frame(wrap, bg=COLOR_BG)
        head.pack(fill="x", pady=(0, 15))
        right_head = tk.Frame(head, bg=COLOR_BG); right_head.pack(side="right")
        tk.Label(right_head, text="🧾  إدارة المترشحين",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(anchor="e")
        tk.Label(right_head, text="إضافة وتعديل وحذف وعرض كل المترشحين",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(anchor="e")

        left_head = tk.Frame(head, bg=COLOR_BG); left_head.pack(side="left")
        ModernButton(left_head, "تسجيل مترشح جديد", self._add_dialog,
                     icon="➕", color=COLOR_SUCCESS).pack(side="right", padx=4)
        ModernButton(left_head, "تعديل المحدد", self._edit_dialog,
                     icon="✏️", color=COLOR_PRIMARY).pack(side="right", padx=4)
        ModernButton(left_head, "نتائج الامتحانات", self._open_exam_results,
                     icon="📊", color=COLOR_PURPLE).pack(side="right", padx=4)
        ModernButton(left_head, "بطاقة التكوين", self._print_training_card,
                     icon="📋", color=COLOR_ACCENT).pack(side="right", padx=4)
        ModernButton(left_head, "حذف", self._delete,
                     icon="🗑️", color=COLOR_DANGER).pack(side="right", padx=4)

        # تنبيه إرشادي بارز
        hint = tk.Frame(wrap, bg=COLOR_PRIMARY_LIGHT, padx=15, pady=10)
        hint.pack(fill="x", pady=(0, 10))
        tk.Label(hint,
                 text="💡  لتسجيل مترشح جديد: اضغط على زر  «➕ تسجيل مترشح جديد»  أعلاه — ستفتح نافذة تحتوي على 3 تبويبات (البيانات الشخصية + الميلاد والعنوان + التسجيل).",
                 font=FONT_BOLD, bg=COLOR_PRIMARY_LIGHT,
                 fg=COLOR_PRIMARY_DARK, anchor="e",
                 wraplength=1200, justify="right").pack(anchor="e")

        # شريط البحث
        search_card_outer, search_card = make_card(wrap, padding=15)
        search_card_outer.pack(fill="x", pady=(0, 10))
        tk.Label(search_card, text="🔍", font=(FONT_FAMILY, 14),
                 bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(side="right", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_list())
        e = make_entry(search_card, self.search_var, width=40)
        e.pack(side="right", fill="x", expand=True, ipady=6)
        tk.Label(search_card, text="ابحث بالاسم أو اللقب أو الهاتف:",
                 font=FONT_BOLD, bg=COLOR_CARD,
                 fg=COLOR_TEXT, anchor="e").pack(side="right", padx=10)

        # جدول المترشحين
        table_outer, table_card = make_card(wrap, padding=10)
        table_outer.pack(fill="both", expand=True)
        cols = ("id", "last_name", "first_name", "national_id", "gender", "phone",
                "license_type", "instructor_name", "total_amount", "registration_date")
        heads = ("رقم", "اللقب", "الاسم", "رقم التعريف", "الجنس", "الهاتف",
                 "الرخصة", "الممرن", "المبلغ", "تاريخ التسجيل")
        widths = (50, 110, 110, 130, 70, 110, 80, 140, 100, 110)
        self.tree = create_treeview(table_card, cols, heads, widths, height=18)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._edit_dialog())

    def _load_list(self):
        rows = CandidateDB.get_all(self.search_var.get())
        values = [(r['id'], r['last_name'], r['first_name'],
                   r.get('national_id', '') or '—', r['gender'], r['phone'],
                   r['license_type'], r.get('instructor_name', '') or '—',
                   f"{r['total_amount']:,.0f} دج", r['registration_date'])
                  for r in rows]
        insert_zebra(self.tree, values)

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_id = self.tree.item(sel[0])['values'][0]

    def _add_dialog(self):
        CandidateDialog(self, on_save=self._do_add)

    def _do_add(self, data):
        init_pay = data.pop("initial_payment", 0)
        cid = CandidateDB.add(data)
        if init_pay > 0 and cid:
            PaymentDB.add({"candidate_id": cid, "date": str(date.today()), "amount": init_pay, "payment_method": "نقدي", "notes": "الدفعة الأولى عند التسجيل"})
        self._load_list()
        show_info("تم إضافة المترشح بنجاح")

    def _edit_dialog(self):
        if not self.selected_id:
            show_error("يرجى تحديد مترشح من القائمة")
            return
        cand = CandidateDB.get(self.selected_id)
        if cand:
            CandidateDialog(self, on_save=lambda d: self._do_update(d), candidate=cand)

    def _do_update(self, data):
        CandidateDB.update(self.selected_id, data)
        self._load_list()
        show_info("تم تعديل بيانات المترشح")

    def _delete(self):
        if not self.selected_id:
            show_error("يرجى تحديد مترشح من القائمة")
            return
        if confirm_delete("هذا المترشح وكل بياناته (التكوين والمدفوعات)"):
            CandidateDB.delete(self.selected_id)
            self.selected_id = None
            self._load_list()
            show_info("تم حذف المترشح")

    def _open_exam_results(self):
        """فتح نافذة تعديل المترشح مع الانتقال مباشرة لتبويب نتائج الامتحانات."""
        if not self.selected_id:
            show_error("يرجى تحديد مترشح من القائمة"); return
        cand = CandidateDB.get(self.selected_id)
        if cand:
            dlg = CandidateDialog(self, on_save=lambda d: self._do_update(d), candidate=cand)
            # الانتقال للتبويب الرابع (الفهرس 3)
            try:
                dlg.children['!notebook'].select(3)
            except Exception:
                try:
                    for child in dlg.winfo_children():
                        if isinstance(child, tk.Frame):
                            for nb in child.winfo_children():
                                if isinstance(nb, ttk.Notebook):
                                    nb.select(3)
                                    break
                except Exception:
                    pass

    def _print_training_card(self):
        if not self.selected_id:
            show_error("يرجى تحديد مترشح من القائمة أولاً"); return
        temp_doc = DocumentsFrame(self)
        temp_doc.selected_candidate_id = self.selected_id
        temp_doc._doc_training_card()
        temp_doc.destroy()


# ============================================================================
#  نافذة منبثقة للممرنين
# ============================================================================

class InstructorDialog(tk.Toplevel):
    def __init__(self, parent, on_save, instructor=None):
        super().__init__(parent)
        self.on_save = on_save
        self.instructor = instructor
        self.vars = {}
        self.title("بيانات الممرن")
        self.geometry("850x680")
        self.configure(bg=COLOR_BG)
        self.transient(parent)
        self.grab_set()
        self._build()
        if instructor:
            self._fill(instructor)

    def _build(self):
        head = tk.Frame(self, bg=COLOR_PURPLE, pady=15, padx=20)
        head.pack(fill="x")
        title_text = "✏️  تعديل بيانات الممرن" if self.instructor else "➕  إضافة ممرن جديد"
        tk.Label(head, text=title_text, font=(FONT_FAMILY, 15, "bold"),
                 bg=COLOR_PURPLE, fg="white", anchor="e").pack(side="right")

        wrap = tk.Frame(self, bg=COLOR_BG, padx=15, pady=10)
        wrap.pack(fill="both", expand=True)
        
        # استخدام Notebook لتقسيم البيانات إذا كانت كثيرة لضمان الوضوح
        nb = ttk.Notebook(wrap, style="Modern.TNotebook")
        nb.pack(fill="both", expand=True)
        
        # التبويب 1: البيانات الشخصية والمهنية
        tab1 = tk.Frame(nb, bg=COLOR_CARD, padx=15, pady=10)
        nb.add(tab1, text="👤 البيانات الأساسية")
        
        grid1 = tk.Frame(tab1, bg=COLOR_CARD)
        grid1.pack(fill="both", expand=True)
        grid1.columnconfigure(0, weight=1)
        grid1.columnconfigure(1, weight=1)

        fields1 = [
            ("الاسم *", "first_name", "entry"),
            ("اللقب *", "last_name", "entry"),
            ("الجنس", "gender", "combo", GENDER_OPTIONS),
            ("تاريخ الميلاد", "birth_date", "entry"),
            ("مكان الميلاد", "birth_place", "entry"),
            ("رقم الهاتف", "phone", "entry"),
            ("العنوان", "address", "entry"),
            ("رقم رخصة السياقة", "license_number", "entry"),
            ("تاريخ الحصول عليها", "license_date", "entry"),
            ("الأصناف (مثال: A,B)", "categories", "entry"),
            ("سنوات الخبرة", "experience_years", "entry"),
        ]
        
        for i, fi in enumerate(fields1):
            row, col = i // 2, i % 2
            cell = tk.Frame(grid1, bg=COLOR_CARD)
            cell.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
            make_label(cell, fi[0], font=FONT_BOLD).pack(anchor="e")
            v = tk.StringVar(); self.vars[fi[1]] = v
            if fi[2] == "combo":
                w = make_combo(cell, v, fi[3], width=28)
            else:
                w = make_entry(cell, v, width=30)
            w.pack(fill="x", ipady=3, pady=(2, 0))

        # التبويب 2: بيانات العقد والتوظيف
        tab2 = tk.Frame(nb, bg=COLOR_CARD, padx=15, pady=10)
        nb.add(tab2, text="📜 بيانات العقد")
        
        grid2 = tk.Frame(tab2, bg=COLOR_CARD)
        grid2.pack(fill="both", expand=True)
        grid2.columnconfigure(0, weight=1)
        grid2.columnconfigure(1, weight=1)
        
        fields2 = [
            ("مدة العقد (مثلاً: سنة)", "contract_duration", "entry"),
            ("الأجر الشهري (دج)", "salary", "entry"),
            ("تاريخ بداية العمل", "contract_start_date", "entry"),
            ("تاريخ إمضاء العقد", "contract_signing_date", "entry"),
            ("مدة الإخطار (بالأشهر)", "notice_period", "entry"),
        ]
        
        for i, fi in enumerate(fields2):
            row, col = i // 2, i % 2
            cell = tk.Frame(grid2, bg=COLOR_CARD)
            cell.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
            make_label(cell, fi[0], font=FONT_BOLD).pack(anchor="e")
            v = tk.StringVar(); self.vars[fi[1]] = v
            w = make_entry(cell, v, width=30)
            w.pack(fill="x", ipady=3, pady=(2, 0))

        bf = tk.Frame(self, bg=COLOR_BG, pady=12)
        bf.pack(side="bottom", fill="x", padx=20)
        ModernButton(bf, "إلغاء", self.destroy, icon="✗",
                     color=COLOR_TEXT_LIGHT).pack(side="left", padx=5)
        ModernButton(bf, "حفظ البيانات", self._save, icon="💾",
                     color=COLOR_SUCCESS).pack(side="right", padx=5)

    def _fill(self, d):
        for k, v in self.vars.items():
            v.set(str(d.get(k, "")))

    def _save(self):
        d = {k: self.vars[k].get().strip() for k in
             ("first_name","last_name","birth_date","birth_place","phone","address",
              "license_number","license_date","categories","contract_duration",
              "salary","contract_start_date","notice_period","contract_signing_date")}
        d["gender"] = self.vars["gender"].get()
        d["experience_years"] = self.vars["experience_years"].get().strip() or "0"
        if not d["first_name"] or not d["last_name"]:
            show_error("الاسم واللقب إلزاميان"); return
        self.on_save(d); self.destroy()


# ============================================================================
#  واجهة: الممرنون
# ============================================================================

class InstructorsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_id = None
        self._build(); self._load_list()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)

        head = tk.Frame(wrap, bg=COLOR_BG)
        head.pack(fill="x", pady=(0, 15))
        rh = tk.Frame(head, bg=COLOR_BG); rh.pack(side="right")
        tk.Label(rh, text="🚗  إدارة الممرنين",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(anchor="e")
        tk.Label(rh, text="إدارة الممرنين العاملين في المدرسة",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(anchor="e")
        lh = tk.Frame(head, bg=COLOR_BG); lh.pack(side="left")
        ModernButton(lh, "إضافة ممرن", self._add_dialog,
                     icon="➕", color=COLOR_SUCCESS).pack(side="right", padx=4)
        ModernButton(lh, "تعديل", self._edit_dialog,
                     icon="✏️", color=COLOR_PURPLE).pack(side="right", padx=4)
        ModernButton(lh, "بطاقة التكوين", self._print_training_card,
                     icon="📋", color=COLOR_SUCCESS).pack(side="right", padx=4)
        ModernButton(lh, "عقد العمل", self._print_contract,
                     icon="📜", color=COLOR_PRIMARY).pack(side="right", padx=4)
        ModernButton(lh, "حذف", self._delete,
                     icon="🗑️", color=COLOR_DANGER).pack(side="right", padx=4)

        sco, sc = make_card(wrap, padding=15); sco.pack(fill="x", pady=(0, 10))
        tk.Label(sc, text="🔍", font=(FONT_FAMILY, 14),
                 bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(side="right", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_list())
        make_entry(sc, self.search_var, width=40).pack(side="right", fill="x",
                                                       expand=True, ipady=6)
        tk.Label(sc, text="ابحث بالاسم أو الهاتف:", font=FONT_BOLD,
                 bg=COLOR_CARD, fg=COLOR_TEXT, anchor="e").pack(side="right", padx=10)

        to, tc = make_card(wrap, padding=10); to.pack(fill="both", expand=True)
        self.tree = create_treeview(tc,
            ("id","last_name","first_name","gender","phone","categories","experience_years"),
            ("رقم","اللقب","الاسم","الجنس","الهاتف","الأصناف","سنوات الخبرة"),
            (50,140,140,80,130,120,130), height=18)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._edit_dialog())

    def _load_list(self):
        rows = InstructorDB.get_all(self.search_var.get())
        values = [(r['id'], r['last_name'], r['first_name'], r['gender'],
                   r['phone'], r['categories'], r['experience_years']) for r in rows]
        insert_zebra(self.tree, values)

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_id = self.tree.item(sel[0])['values'][0]

    def _add_dialog(self):
        InstructorDialog(self, on_save=self._do_add)

    def _do_add(self, data):
        InstructorDB.add(data); self._load_list()
        show_info("تم إضافة الممرن بنجاح")

    def _edit_dialog(self):
        if not self.selected_id:
            show_error("يرجى تحديد ممرن من القائمة"); return
        ins = InstructorDB.get(self.selected_id)
        if ins:
            InstructorDialog(self, on_save=self._do_update, instructor=ins)

    def _do_update(self, data):
        InstructorDB.update(self.selected_id, data); self._load_list()
        show_info("تم تعديل بيانات الممرن")

    def _print_training_card(self):
        if not self.selected_id:
            show_error("يرجى تحديد ممرن من القائمة أولاً"); return
        
        # جلب المترشحين التابعين لهذا الممرن
        conn = get_connection()
        rows = conn.execute("SELECT id, last_name, first_name FROM candidates WHERE instructor_id=?", (self.selected_id,)).fetchall()
        conn.close()
        
        if not rows:
            show_error("لا يوجد مترشحون مسجلون لهذا الممرن"); return
            
        # نافذة اختيار المترشح
        win = tk.Toplevel(self)
        win.title("اختر المترشح")
        win.geometry("450x500")
        win.configure(bg=COLOR_BG)
        win.transient(self); win.grab_set()
        
        tk.Label(win, text="اختر المترشح لطباعة بطاقة التكوين له:", font=FONT_BOLD, bg=COLOR_BG).pack(pady=10)
        
        tree = create_treeview(win, ("id","name"), ("رقم","الاسم واللقب"), (50,300), height=15)
        for r in rows:
            tree.insert("", "end", values=(r['id'], f"{r['last_name']} {r['first_name']}"))
        
        def do_print():
            sel = tree.selection()
            if not sel: return
            cid = tree.item(sel[0])['values'][0]
            # استدعاء دالة الطباعة من واجهة الوثائق (أو بشكل مباشر)
            # سنقوم بمحاكاة اختيار المترشح في واجهة الوثائق
            for tab in self.master.winfo_children():
                if isinstance(tab, DocumentsFrame):
                    tab.selected_candidate_id = cid
                    tab._doc_training_card()
                    win.destroy()
                    return
            # إذا لم نجدها (نادر جداً)، ننشئ نسخة مؤقتة
            temp_doc = DocumentsFrame(self)
            temp_doc.selected_candidate_id = cid
            temp_doc._doc_training_card()
            win.destroy()

        ModernButton(win, "طباعة البطاقة", do_print, color=COLOR_PRIMARY).pack(pady=15)

    def _print_contract(self):
        if not self.selected_id:
            show_error("يرجى تحديد ممرن من القائمة أولاً"); return
        
        ins = InstructorDB.get(self.selected_id)
        school = SchoolInfoDB.get()
        
        import tempfile, os
        from datetime import datetime
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        
        temp_dir = tempfile.gettempdir()
        path = os.path.join(temp_dir, f"instructor_contract_{ins['id']}_{int(datetime.now().timestamp())}.pdf")
        c = canvas.Canvas(path, pagesize=A4)
        
        def draw_text(x_cm, y_cm, text, font=ARABIC_FONT, size=11, align="right", bold=False):
            f = ARABIC_FONT_BOLD if bold else font
            c.setFont(f, size)
            text_ar = ar(str(text))
            if align == "right":
                c.drawRightString(x_cm * cm, y_cm * cm, text_ar)
            elif align == "center":
                c.drawCentredString(x_cm * cm, y_cm * cm, text_ar)
            else:
                c.drawString(x_cm * cm, y_cm * cm, text_ar)

        # 1. الترويسة
        draw_text(20.0, 28.5, f"مدرسة تعليم سياقة المركبات ذات المحرك: {school.get('name','')}", ARABIC_FONT_BOLD, 12)
        draw_text(20.0, 27.8, f"العنوان: {school.get('address','')}", size=11)
        draw_text(20.0, 27.1, f"رقم الاعتماد: {school.get('accreditation_number','')}", size=11)
        draw_text(20.0, 26.4, f"رقم السجل التجاري: {school.get('commercial_register','')}", size=11)
        draw_text(20.0, 25.7, f"الرقم الجبائي: {school.get('nif','')}", size=11)

        # 2. العنوان الرئيسي
        c.setLineWidth(1)
        c.rect(7.5*cm, 23.5*cm, 6*cm, 1.2*cm)
        draw_text(10.5, 24.0, "عقد عمل", ARABIC_FONT_BOLD, 22, "center")

        # 3. الأطراف
        y = 22.0
        draw_text(20.0, y, "بين:", ARABIC_FONT_BOLD, 12)
        draw_text(19.0, y, f"مدرسة تعليم سياقة المركبات ذات المحرك المذكورة أعلاه، الممثلة بالسيد مدير مدرسة")
        draw_text(19.0, y-0.6, "تعليم سياقة المركبات ذات المحرك.", align="right")
        draw_text(2.5, y-0.6, "من جهة،", ARABIC_FONT_BOLD, 11)

        y -= 1.8
        draw_text(20.0, y, "و:", ARABIC_FONT_BOLD, 12)
        ins_name = f"{ins['last_name']} {ins['first_name']}"
        draw_text(19.0, y, f"السيد: {ins_name}،   المولود في : {ins['birth_date']} بـ: {ins.get('birth_place','........')}")
        draw_text(19.0, y-0.7, f"الساكن بـ: {ins['address']}")
        draw_text(2.5, y-0.7, "من جهة أخرى،", ARABIC_FONT_BOLD, 11)

        # 4. المواد
        y -= 1.8
        c.setFont(ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y, "المادة الأولى: يوظف السيد:", align="right", bold=True)
        draw_text(15.5, y, f"{ins_name} بصفة ممرن وذلك طبقاً لأحكام القرار الوزاري المشترك")
        draw_text(19.5, y-0.6, "المؤرخ في 1979/09/15 المحدد لكيفيات وشروط استغلال مؤسسات تعليم سياقة المركبات ذات المحرك.")

        y -= 1.4
        dur = ins.get('contract_duration','') or "...................."
        draw_text(20.0, y, f"المادة 02: يبرم عقد العمل هذا لمدة {dur}", bold=True)
        
        y -= 0.8
        sal = ins.get('salary','') or "...................."
        draw_text(20.0, y, f"المادة 03: يستفيد السيد {ins_name} من أجر شهري قدره {sal} دج", bold=True)
        draw_text(18.5, y-0.6, "ويمكن أن يكون هذا الأجر محل مراجعة باتفاق الطرفين.")

        y -= 1.4
        draw_text(20.0, y, f"المادة 04: تمنح للسيد {ins_name} كل الضمانات الواردة في تشريع العمل والضمان الاجتماعي.", bold=True)

        y -= 0.8
        draw_text(20.0, y, f"المادة 05: يتولى السيد {ins_name} المهام التالية:", bold=True)
        tasks = [
            "- تلقين الدروس النظرية والتطبيقية المتعلقة بقانون المرور لفائدة المترشحين لرخصة السياقة.",
            "- تعليم وتمرين المترشحين سياقة المركبات ذات المحرك.",
            "- تعليم وإعلام المترشحين بمختلف النصوص التنظيمية التي تحكم قانون المرور مع التقيد بالبرنامج",
            "  الوطني للتكوين الخاص بسياقة المركبات ذات المحرك الصادر عن وزارة النقل."
        ]
        for task in tasks:
            y -= 0.6
            draw_text(19.0, y, task)

        y -= 1.0
        draw_text(20.0, y, "المادة 06: يقع على عاتق الممرن أو مدير مدرسة تعليم سياقة المركبات ذات المحرك حسب الحالة إعداد البطاقات", bold=True)
        draw_text(19.5, y-0.6, "الخاصة بكل الدروس المقدمة للمترشحين في مجال تعليم سياقة المركبات وفقاً للبرنامج")
        draw_text(19.5, y-1.2, "الوطني المذكور أعلاه.")

        y -= 2.0
        not_p = ins.get('notice_period','') or "...."
        draw_text(20.0, y, f"المادة 07: في حالة نقض العقد الحالي، على الطرفين القيام بالإخطار بمدة لا تقل عن {not_p} شهر.", bold=True)
        
        y -= 0.8
        st_d = ins.get('contract_start_date','') or "...................."
        draw_text(20.0, y, f"المادة 08: يسري مفعول هذا العقد ابتداءً من {st_d}", bold=True)

        # 5. الخاتمة والتوقيعات
        y -= 1.5
        wilaya = school.get('address', '').split(' ')[-1] if school.get('address') else '........'
        sig_date = ins.get('contract_signing_date','') or "...................."
        draw_text(12.0, y, f"حرر بـ: {wilaya}              في: {sig_date}", size=12)

        y -= 1.5
        draw_text(17.5, y, "اسم الممرن ولقبه", ARABIC_FONT_BOLD, 12, "center")
        draw_text(17.5, y-0.6, "قرىء وصودق عليه", size=10, align="center")
        
        draw_text(5.5, y, "مدير مدرسة تعليم سياقة", ARABIC_FONT_BOLD, 12, "center")
        draw_text(5.5, y-0.6, "المركبات ذات المحرك", ARABIC_FONT_BOLD, 12, "center")

        c.save()
        try:
            # محاولة الطباعة المباشرة
            os.startfile(path, 'print')
        except Exception:
            # في حال فشل الطباعة المباشرة، نكتفي بفتح الملف
            try: os.startfile(path)
            except Exception as e: show_error(f"خطأ: {e}")

    def _delete(self):
        if not self.selected_id:
            show_error("يرجى تحديد ممرن من القائمة"); return
        if confirm_delete("هذا الممرن"):
            InstructorDB.delete(self.selected_id)
            self.selected_id = None
            self._load_list()
            show_info("تم حذف الممرن")


# ============================================================================
#  واجهة: مراحل التكوين
# ============================================================================

class TrainingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_candidate_id = None
        self.selected_stage_id = None
        self.stage_vars = {}
        self.current_stages = []
        self._build(); self._load_candidates()

    @staticmethod
    def _is_unlocked(stages, stage_type):
        """مرحلة مفتوحة فقط إذا كل المراحل السابقة بحالة 'ناجح'."""
        try:
            idx = STAGE_ORDER.index(stage_type)
        except ValueError:
            return True
        if idx == 0:
            return True
        by_type = {}
        for s in stages:
            if s['stage_type'] not in by_type or s['status'] == STATUS_PASS:
                by_type[s['stage_type']] = s
        for prev_type in STAGE_ORDER[:idx]:
            prev = by_type.get(prev_type)
            if not prev or prev.get('status') != STATUS_PASS:
                return False
        return True

    def _get_active_stage(self):
        if not self.selected_candidate_id: return None
        stages = TrainingDB.get_by_candidate(self.selected_candidate_id)
        if not stages: return None
        stages.sort(key=lambda s: s['id'], reverse=True)
        return stages[0]

    def _get_candidate_name(self):
        if not self.selected_candidate_id: return ""
        conn = get_connection()
        c = conn.execute("SELECT first_name, last_name FROM candidates WHERE id=?", (self.selected_candidate_id,)).fetchone()
        conn.close()
        return f"{c['first_name']} {c['last_name']}" if c else ""

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="📚  مراحل التكوين",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=0)
        tk.Label(wrap, text="إدارة مراحل التكوين الثلاث: الكود، الكرينو، السياقة",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(fill="x", pady=(0, 10))

        main_container = tk.Frame(wrap, bg=COLOR_BG)
        main_container.pack(fill="both", expand=True)

        # يمين: لوحة التحكم والعمليات السريعة
        right_frame = tk.Frame(main_container, bg=COLOR_BG, width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        fo, fc = make_card(right_frame); fo.pack(fill="both", expand=True)
        section_title(fc, "إدارة المرحلة الحالية", icon="🎯")

        self.lbl_cand_name = tk.Label(fc, text="الرجاء اختيار مترشح", font=(FONT_FAMILY, 14, "bold"), bg=COLOR_CARD, fg=COLOR_HEADER)
        self.lbl_cand_name.pack(pady=5)
        
        lbl_hours = tk.Label(fc, text="الحجم الساعي: 30 ساعة كود | 30 ساعة سياقة", font=(FONT_FAMILY, 10), bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT)
        lbl_hours.pack(pady=(0, 10))

        self.lbl_current_stage = tk.Label(fc, text="المرحلة: -", font=(FONT_FAMILY, 14, "bold"), bg=COLOR_CARD, fg=COLOR_PRIMARY)
        self.lbl_current_stage.pack(pady=5)
        
        self.lbl_stage_status = tk.Label(fc, text="الحالة: -", font=FONT_MAIN, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT)
        self.lbl_stage_status.pack(pady=5)

        self.btn_exam_results = ModernButton(fc, "نتائج الامتحانات", self._show_exam_results_window, icon="📋", color=COLOR_PURPLE)
        self.btn_exam_results.pack(fill="x", pady=(15, 5), ipady=2)

        self.btn_history = ModernButton(fc, "سجل مراحل التكوين", self._show_history_window, icon="📜", color=COLOR_PRIMARY)
        self.btn_history.pack(fill="x", pady=(0, 10), ipady=2)

        action_btns = tk.Frame(fc, bg=COLOR_CARD)
        action_btns.pack(fill="x", pady=5)

        self.btn_pass = ModernButton(action_btns, "نجاح", self._quick_pass, icon="✅", color=COLOR_SUCCESS)
        self.btn_pass.pack(side="right", fill="x", expand=True, padx=(0, 2), ipady=2)

        self.btn_fail = ModernButton(action_btns, "رسوب", self._quick_fail, icon="❌", color=COLOR_WARNING)
        self.btn_fail.pack(side="left", fill="x", expand=True, padx=(2, 0), ipady=2)

        self._set_buttons_state("disabled")

        # يسار: شريط البحث + المترشحين + المراحل
        left_frame = tk.Frame(main_container, bg=COLOR_BG)
        left_frame.pack(side="left", fill="both", expand=True)

        # شريط البحث
        sco, sc = make_card(left_frame, padding=5); sco.pack(fill="x", pady=(0, 5))
        tk.Label(sc, text="🔍", font=(FONT_FAMILY, 14),
                 bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(side="right", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_candidates())
        make_entry(sc, self.search_var, width=30).pack(side="right", fill="x", expand=True, ipady=4)
        tk.Label(sc, text="ابحث عن مترشح:", font=FONT_BOLD,
                 bg=COLOR_CARD, fg=COLOR_TEXT, anchor="e").pack(side="right", padx=10)

        # قائمة المترشحين
        co, cc = make_card(left_frame, padding=5); co.pack(fill="both", expand=True, pady=(0, 5))
        section_title(cc, "اختر المترشح", icon="👤")
        self.cand_tree = create_treeview(cc,
            ("id","last_name","first_name","phone","license_type"),
            ("رقم","اللقب","الاسم","الهاتف","نوع الرخصة"),
            (50,150,150,130,100), height=10)
        self.cand_tree.bind("<<TreeviewSelect>>", self._on_candidate_select)

    def _load_candidates(self):
        rows = CandidateDB.get_all(self.search_var.get())
        values = [(r['id'], r['last_name'], r['first_name'],
                   r['phone'], r['license_type']) for r in rows]
        insert_zebra(self.cand_tree, values)

    def _on_candidate_select(self, event):
        sel = self.cand_tree.selection()
        if not sel: return
        self.selected_candidate_id = self.cand_tree.item(sel[0])['values'][0]
        self._load_stages()
        self._update_action_panel()

    def _set_buttons_state(self, state):
        self.btn_pass.config(state=state)
        self.btn_fail.config(state=state)
        has_cand = "normal" if self.selected_candidate_id else "disabled"
        self.btn_history.config(state=has_cand)
        self.btn_exam_results.config(state=has_cand)

    def _update_action_panel(self):
        name = self._get_candidate_name()
        self.lbl_cand_name.config(text=f"المترشح: {name}")
        
        active = self._get_active_stage()
        if not active:
            self.lbl_current_stage.config(text="لا توجد مراحل")
            self.lbl_stage_status.config(text="")
            self._set_buttons_state("disabled")
            return
            
        stage_name = STAGE_LABELS.get(active['stage_type'], active['stage_type'])
        
        if active['status'] == STATUS_PASS and active['stage_type'] == "circuit":
            self.lbl_current_stage.config(text="🎓 تخرج بنجاح!")
            self.lbl_stage_status.config(text="أنهى جميع المراحل (الكود، الكرينو، السيركوي)")
            self._set_buttons_state("disabled")
        else:
            self.lbl_current_stage.config(text=f"المرحلة: {stage_name}")
            self.lbl_stage_status.config(text=f"الحالة: {active['status']}")
            
            if active['status'] == STATUS_PASS:
                self._set_buttons_state("disabled")
            else:
                self._set_buttons_state("normal")

    def _load_stages(self):
        if not self.selected_candidate_id:
            self.current_stages = []; return
        stages_raw = TrainingDB.get_by_candidate(self.selected_candidate_id)
        order_idx = {t: i for i, t in enumerate(STAGE_ORDER)}
        self.current_stages = sorted(
            stages_raw, key=lambda s: (order_idx.get(s['stage_type'], 99), s['id']))

    def _show_history_window(self):
        if not self.selected_candidate_id: return
        win = tk.Toplevel(self)
        win.title(f"سجل مراحل التكوين - {self._get_candidate_name()}")
        win.geometry("900x450")
        win.configure(bg=COLOR_BG)
        win.transient(self.winfo_toplevel())

        tk.Label(win, text=f"سجل مراحل التكوين للمترشح: {self._get_candidate_name()}",
                 font=(FONT_FAMILY, 16, "bold"), bg=COLOR_BG, fg=COLOR_HEADER).pack(pady=15)

        tree = create_treeview(win,
            ("id","stage_type","status","start_date","end_date","score","notes"),
            ("رقم","المرحلة","الحالة","تاريخ البداية","تاريخ النهاية","النتيجة","ملاحظات"),
            (40,150,120,110,110,80,150), height=15)

        values = []
        for s in self.current_stages:
            unlocked = self._is_unlocked(self.current_stages, s['stage_type'])
            label = STAGE_LABELS.get(s['stage_type'], s['stage_type'])
            if not unlocked:
                label = f"🔒  {label}  (مقفلة)"
            elif s['status'] == STATUS_PASS:
                label = f"✅  {label}"
            elif s['status'] == "راسب":
                label = f"❌  {label}"
            else:
                label = f"▶  {label}"
            values.append((s['id'], label, s['status'],
                           s['start_date'] or "", s['end_date'] or "",
                           s['score'] or "", s['notes'] or ""))
        insert_zebra(tree, values)

        ModernButton(win, "إغلاق", win.destroy, color=COLOR_TEXT_LIGHT).pack(pady=15)

    def _show_exam_results_window(self):
        if not self.selected_candidate_id: return
        cid  = self.selected_candidate_id
        name = self._get_candidate_name()

        win = tk.Toplevel(self)
        win.title(f"نتائج الامتحانات - {name}")
        win.geometry("1000x620")
        win.configure(bg=COLOR_BG)
        win.transient(self.winfo_toplevel())

        # ── العنوان ──────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=COLOR_PRIMARY, padx=20, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📋  نتائج الامتحانات للمترشح: {name}",
                 font=(FONT_FAMILY, 16, "bold"), bg=COLOR_PRIMARY, fg="white").pack(side="right")

        # ── صف الإحصائيات السريعة ────────────────────────────────────
        stats_frame = tk.Frame(win, bg=COLOR_BG, padx=15, pady=10)
        stats_frame.pack(fill="x")
        self._exam_stats_frame = stats_frame

        # ── شريط الأدوات ─────────────────────────────────────────────
        toolbar = tk.Frame(win, bg=COLOR_BG, padx=15, pady=0)
        toolbar.pack(fill="x")

        stage_var = tk.StringVar(value=list(STAGE_LABELS.keys())[0])
        stage_labels_list = [f"{v}  ({k})" for k, v in STAGE_LABELS.items()]
        stage_keys = list(STAGE_LABELS.keys())

        tk.Label(toolbar, text="اختر المرحلة:", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT).pack(side="right", padx=(0, 6))
        stage_combo = make_combo(toolbar, stage_var, stage_labels_list, width=28)
        stage_combo.current(0)
        stage_combo.pack(side="right")

        ModernButton(toolbar, "تسجيل نتيجة امتحان", icon="➕", color=COLOR_SUCCESS,
                     command=lambda: self._add_exam_attempt_dialog(
                         win, cid, stage_keys[stage_combo.current()],
                         lambda: self._refresh_exam_window(win, cid, tree_ref, self._exam_stats_frame))
                     ).pack(side="right", padx=(8, 0), ipady=2)

        ModernButton(toolbar, "حذف المحدد", icon="🗑️", color=COLOR_DANGER,
                     command=lambda: self._delete_exam_attempt(cid, tree_ref,
                         lambda: self._refresh_exam_window(win, cid, tree_ref, self._exam_stats_frame))
                     ).pack(side="left", padx=(0, 0), ipady=2)

        # ── جدول النتائج ─────────────────────────────────────────────
        table_frame = tk.Frame(win, bg=COLOR_BG, padx=15, pady=5)
        table_frame.pack(fill="both", expand=True)

        tree_ref = create_treeview(table_frame,
            ("id","stage","exam_date","score","result","notes"),
            ("رقم","المرحلة","تاريخ الامتحان","العلامة / 40","النتيجة","ملاحظات"),
            (40, 180, 120, 110, 100, 220), height=15)

        ModernButton(win, "إغلاق", win.destroy, color=COLOR_TEXT_LIGHT).pack(pady=8)

        self._refresh_exam_window(win, cid, tree_ref, self._exam_stats_frame)

    def _refresh_exam_window(self, win, cid, tree, stats_frame):
        attempts = ExamAttemptsDB.get_by_candidate(cid)
        values = []
        for a in attempts:
            stage_label = STAGE_LABELS.get(a['stage_type'], a['stage_type'])
            result_icon = "✅ ناجح" if a['result'] == STATUS_PASS else "❌ راسب"
            values.append((a['id'], stage_label, a['exam_date'],
                           a['score'] if a['score'] else "—",
                           result_icon, a['notes'] or ""))
        insert_zebra(tree, values)

        for w in stats_frame.winfo_children():
            w.destroy()

        stats_by_stage = {s['stage_type']: s
                          for s in ExamAttemptsDB.get_stats_by_stage()}

        for code, label in STAGE_LABELS.items():
            s = stats_by_stage.get(code, {'total': 0, 'passed': 0})
            total  = s.get('total', 0) or 0
            passed = s.get('passed', 0) or 0
            rate   = (passed / total * 100) if total > 0 else 0
            color  = COLOR_SUCCESS if rate >= 50 else (COLOR_DANGER if total > 0 else COLOR_TEXT_LIGHT)

            sc = tk.Frame(stats_frame, bg=COLOR_CARD, padx=14, pady=10,
                          highlightthickness=1, highlightbackground=COLOR_BORDER)
            sc.pack(side="right", fill="both", expand=True, padx=6)
            tk.Label(sc, text=label, font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="e")
            tk.Label(sc, text=f"{rate:.0f}%  نجاح", font=(FONT_FAMILY, 18, "bold"),
                     bg=COLOR_CARD, fg=color).pack(anchor="e")
            tk.Label(sc, text=f"إجمالي المحاولات: {total}  |  ناجح: {passed}  |  راسب: {total - passed}",
                     font=FONT_TINY, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT).pack(anchor="e")

    def _add_exam_attempt_dialog(self, parent_win, cid, stage_type, on_save):
        dlg = tk.Toplevel(parent_win)
        dlg.title("تسجيل نتيجة امتحان")
        dlg.geometry("440x360")
        dlg.configure(bg=COLOR_BG)
        dlg.transient(parent_win)
        dlg.grab_set()

        tk.Label(dlg, text="تسجيل نتيجة امتحان جديدة",
                 font=(FONT_FAMILY, 15, "bold"), bg=COLOR_BG, fg=COLOR_HEADER).pack(pady=(18, 10))

        outer, body = make_card(dlg, padding=18)
        outer.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        vars_ = {}

        def field_row(label, key, widget_type="entry", options=None, default=""):
            row = tk.Frame(body, bg=COLOR_CARD); row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=FONT_BOLD, bg=COLOR_CARD,
                     fg=COLOR_TEXT, width=14, anchor="e").pack(side="right")
            v = tk.StringVar(value=default)
            vars_[key] = v
            if widget_type == "combo":
                w = make_combo(row, v, options, width=18)
                w.set(options[0] if options else "")
                if default:
                    w.set(default)
            else:
                w = make_entry(row, v, width=20)
            w.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=3)

        stage_label = STAGE_LABELS.get(stage_type, stage_type)
        tk.Label(body, text=f"المرحلة: {stage_label}",
                 font=(FONT_FAMILY, 12, "bold"), bg=COLOR_CARD,
                 fg=COLOR_PRIMARY, anchor="e").pack(fill="x", pady=(0, 8))

        field_row("تاريخ الامتحان:", "exam_date", default=str(date.today()))
        field_row("العلامة (/ 40):", "score", default="0")
        field_row("النتيجة:", "result", "combo", ["راسب", "ناجح"], default="راسب")
        field_row("ملاحظات:", "notes", default="")

        def _save():
            try:
                score_val = float(vars_['score'].get() or 0)
            except ValueError:
                show_error("العلامة يجب أن تكون رقماً")
                return
            ExamAttemptsDB.add({
                'candidate_id': cid,
                'stage_type':   stage_type,
                'exam_date':    vars_['exam_date'].get() or str(date.today()),
                'score':        score_val,
                'result':       vars_['result'].get(),
                'notes':        vars_['notes'].get(),
            })
            dlg.destroy()
            on_save()
            show_info("تم تسجيل نتيجة الامتحان بنجاح!")

        btn_frame = tk.Frame(dlg, bg=COLOR_BG); btn_frame.pack(fill="x", padx=15, pady=(0, 12))
        ModernButton(btn_frame, "حفظ", _save, icon="💾", color=COLOR_SUCCESS).pack(side="right", ipady=2)
        ModernButton(btn_frame, "إلغاء", dlg.destroy, color=COLOR_TEXT_LIGHT).pack(side="left", ipady=2)

    def _delete_exam_attempt(self, cid, tree, on_delete):
        sel = tree.selection()
        if not sel:
            show_error("الرجاء تحديد سجل لحذفه")
            return
        attempt_id = tree.item(sel[0])['values'][0]
        if not confirm_delete("هذه النتيجة"):
            return
        ExamAttemptsDB.delete(attempt_id)
        on_delete()
        show_info("تم حذف نتيجة الامتحان.")

    def _quick_pass(self):
        active = self._get_active_stage()
        if not active: return
        
        # 1. تحديث المرحلة الحالية إلى ناجح
        from datetime import date
        today = str(date.today())
        TrainingDB.update(active['id'], {
            "status": STATUS_PASS, "start_date": today, "end_date": today,
            "score": 0, "notes": ""})
            
        # 2. إضافة المرحلة التالية إذا وجدت
        idx = STAGE_ORDER.index(active['stage_type'])
        if idx + 1 < len(STAGE_ORDER):
            next_stage = STAGE_ORDER[idx + 1]
            existing = TrainingDB.get_by_candidate(self.selected_candidate_id)
            has_next = any(s['stage_type'] == next_stage for s in existing)
            if not has_next:
                TrainingDB.add(self.selected_candidate_id, next_stage)
                
        self._load_stages()
        self._update_action_panel()
        show_info("تم تسجيل النجاح والمرور للمرحلة التالية بنجاح!")

    def _quick_fail(self):
        active = self._get_active_stage()
        if not active: return
        
        # 1. تحديث المرحلة الحالية إلى راسب
        TrainingDB.update(active['id'], {
            "status": "راسب", "start_date": active['start_date'], "end_date": active['end_date'],
            "score": 0, "notes": ""})
            
        # 2. إضافة نفس المرحلة كمحاولة جديدة
        TrainingDB.add(self.selected_candidate_id, active['stage_type'])
        
        self._load_stages()
        self._update_action_panel()
        show_info("تم تسجيل الرسوب. تمت إضافة محاولة جديدة للمترشح.")


# ============================================================================
#  واجهة: المدفوعات
# ============================================================================

class PaymentsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_candidate_id = None
        self.selected_payment_id = None
        self.vars = {}
        self._build(); self._load_candidates()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=10, pady=5)
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text="💰  إدارة المدفوعات", font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=(0, 5))
        tk.Label(wrap, text="تسجيل مدفوعات المترشحين ومتابعة المتبقي", font=FONT_MAIN,
                 bg=COLOR_BG, fg=COLOR_TEXT_LIGHT, anchor="e").pack(fill="x", pady=(0, 10))

        # حاوية رئيسية تنقسم ليمين ويسار
        main_container = tk.Frame(wrap, bg=COLOR_BG)
        main_container.pack(fill="both", expand=True)

        # يمين: الملخص المالي + نموذج إضافة دفعة
        right = tk.Frame(main_container, bg=COLOR_BG, width=320)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        sm = tk.Frame(right, bg=COLOR_PRIMARY, padx=10, pady=5)
        sm.pack(fill="x", pady=(0, 5))
        
        row_sm1 = tk.Frame(sm, bg=COLOR_PRIMARY)
        row_sm1.pack(fill="x")
        self.lbl_total = tk.Label(row_sm1, text="المبلغ الإجمالي: -", font=FONT_BOLD, bg=COLOR_PRIMARY, fg="white")
        self.lbl_total.pack(anchor="center")
        
        row_sm2 = tk.Frame(sm, bg=COLOR_PRIMARY)
        row_sm2.pack(fill="x", pady=(2, 0))
        self.lbl_paid = tk.Label(row_sm2, text="المدفوع: -", font=FONT_BOLD, bg=COLOR_PRIMARY, fg="#a7f3d0")
        self.lbl_paid.pack(side="right", expand=True)
        self.lbl_remaining = tk.Label(row_sm2, text="المتبقي: -", font=(FONT_FAMILY, 12, "bold"), bg=COLOR_PRIMARY, fg=COLOR_ACCENT)
        self.lbl_remaining.pack(side="left", expand=True)

        fo, fc = make_card(right); fo.pack(fill="x", pady=(0, 5))
        
        # نقل زر السجل ليكون في الأعلى للوصول السريع وملاحظة واضحة
        ModernButton(fc, "عرض سجل الدفعات (التاريخ)", self._show_history_window, icon="📜", color=COLOR_PRIMARY).pack(fill="x", pady=(0, 10), ipady=2)
        
        section_title(fc, "إضافة دفعة", icon="➕")
        
        fields = [("التاريخ", "date", "entry"), ("المبلغ (دج)", "amount", "entry"),
                  ("الوسيلة", "payment_method", "combo", PAYMENT_METHOD_OPTIONS), ("ملاحظة", "notes", "entry")]
        
        for fi in fields:
            row = tk.Frame(fc, bg=COLOR_CARD); row.pack(fill="x", pady=2)
            make_label(row, fi[0], font=FONT_BOLD).pack(side="right")
            v = tk.StringVar(); self.vars[fi[1]] = v
            if fi[2] == "combo":
                w = make_combo(row, v, fi[3], width=15)
                w.set(PAYMENT_METHOD_OPTIONS[0])
            else:
                w = make_entry(row, v, width=15)
            w.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=2)
            
        self.vars["date"].set(str(date.today()))
        
        bf = tk.Frame(fc, bg=COLOR_CARD); bf.pack(fill="x", pady=(10, 0))
        
        row1 = tk.Frame(bf, bg=COLOR_CARD); row1.pack(fill="x")
        ModernButton(row1, "إضافة دفعة", self._add, icon="💾", color=COLOR_SUCCESS).pack(side="right", fill="x", expand=True, padx=(0, 2), ipady=2)
        ModernButton(row1, "استرداد", self._refund, icon="↩️", color=COLOR_WARNING).pack(side="left", fill="x", expand=True, padx=(2, 0), ipady=2)
        
        ModernButton(bf, "طباعة وصل الدفع", self._print_receipt, icon="🖨️", color=COLOR_PURPLE).pack(fill="x", pady=(4, 0), ipady=2)

        # يسار: البحث + قائمة المترشحين
        left = tk.Frame(main_container, bg=COLOR_BG)
        left.pack(side="left", fill="both", expand=True)

        # بحث + مترشحين في نفس البطاقة لتوفير المساحة
        co, cc = make_card(left, padding=5); co.pack(fill="both", expand=True, pady=(0, 10))
        
        sc = tk.Frame(cc, bg=COLOR_CARD); sc.pack(fill="x", pady=(0, 5))
        tk.Label(sc, text="بحث:", font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_candidates())
        make_entry(sc, self.search_var, width=25).pack(side="right", fill="x", expand=True, ipady=3, padx=5)

        self.cand_tree = create_treeview(cc,
            ("id","last_name","first_name","phone","total_amount"),
            ("رقم","اللقب","الاسم","الهاتف","المبلغ الإجمالي"),
            (50,140,140,120,140), height=12)
        self.cand_tree.bind("<<TreeviewSelect>>", self._on_candidate_select)

    def _load_candidates(self):
        rows = CandidateDB.get_all(self.search_var.get())
        values = [(r['id'], r['last_name'], r['first_name'], r['phone'],
                   f"{r['total_amount']:,.0f} دج") for r in rows]
        insert_zebra(self.cand_tree, values)

    def _on_candidate_select(self, event):
        sel = self.cand_tree.selection()
        if not sel: return
        self.selected_candidate_id = self.cand_tree.item(sel[0])['values'][0]
        self._refresh_candidate_ui()

    def _refresh_candidate_ui(self):
        cand = CandidateDB.get(self.selected_candidate_id)
        total = cand['total_amount'] if cand else 0
        paid = PaymentDB.get_total_by_candidate(self.selected_candidate_id) if cand else 0
        rem = total - paid
        self.lbl_total.config(text=f"المبلغ الإجمالي: {total:,.0f} دج")
        self.lbl_paid.config(text=f"المدفوع: {paid:,.0f} دج")
        self.lbl_remaining.config(
            text=f"المتبقي: {rem:,.0f} دج",
            fg=COLOR_ACCENT if rem > 0 else "#a7f3d0")
        self._load_payments()

    def _load_payments(self):
        if not hasattr(self, 'pay_tree') or not self.pay_tree.winfo_exists():
            return
        if not self.selected_candidate_id:
            insert_zebra(self.pay_tree, []); return
        rows = PaymentDB.get_by_candidate(self.selected_candidate_id)
        values = [(p['id'], p['date'], f"{p['amount']:,.0f}",
                   p['payment_method'], p['notes']) for p in rows]
        insert_zebra(self.pay_tree, values)

    def _show_history_window(self):
        if not self.selected_candidate_id: return
        win = tk.Toplevel(self)
        cand = CandidateDB.get(self.selected_candidate_id)
        name = f"{cand['first_name']} {cand['last_name']}" if cand else ""
        win.title(f"سجل المدفوعات - {name}")
        win.geometry("850x450")
        win.configure(bg=COLOR_BG)
        win.transient(self.winfo_toplevel())
        
        lbl = tk.Label(win, text=f"سجل المدفوعات للمترشح: {name}", font=(FONT_FAMILY, 16, "bold"), bg=COLOR_BG, fg=COLOR_HEADER)
        lbl.pack(pady=15)
        
        self.pay_tree = create_treeview(win,
            ("id","date","amount","payment_method","notes"),
            ("رقم","التاريخ","المبلغ (دج)","طريقة الدفع","ملاحظة"),
            (50,120,130,140,250), height=12)
        self.pay_tree.bind("<<TreeviewSelect>>", self._on_payment_select)
        
        self._load_payments()
        
        bf = tk.Frame(win, bg=COLOR_BG)
        bf.pack(fill="x", pady=15, padx=20)
        ModernButton(bf, "حذف الدفعة المحددة", self._delete, icon="🗑️", color=COLOR_DANGER).pack(side="left")
        ModernButton(bf, "إغلاق", win.destroy, color=COLOR_TEXT_LIGHT).pack(side="right")

    def _on_payment_select(self, event):
        sel = self.pay_tree.selection()
        if sel:
            self.selected_payment_id = self.pay_tree.item(sel[0])['values'][0]

    def _add(self):
        if not self.selected_candidate_id:
            show_error("يرجى تحديد مترشح من القائمة أولاً"); return
        try:
            amt_str = self.vars["amount"].get().replace(",", ".").replace(" ", "")
            amt = float(amt_str or 0)
            if amt <= 0:
                show_error("يرجى إدخال مبلغ صحيح أكبر من الصفر"); return
        except ValueError:
            show_error("المبلغ يجب أن يكون رقماً (تأكد من عدم وجود مسافات غير ضرورية)"); return
        PaymentDB.add({"candidate_id": self.selected_candidate_id,
                       "date": self.vars["date"].get().strip() or str(date.today()),
                       "amount": amt,
                       "payment_method": self.vars["payment_method"].get() or "نقدي",
                       "notes": self.vars["notes"].get().strip()})
        self.vars["amount"].set(""); self.vars["notes"].set("")
        self._refresh_candidate_ui()
        
        if messagebox.askyesno("نجاح", "تم تسجيل الدفعة بنجاح!\nهل ترغب في طباعة وصل دفع الآن؟"):
            self._print_receipt()

    def _print_receipt(self):
        if not self.selected_candidate_id:
            show_error("يرجى تحديد مترشح من القائمة أولاً"); return
            
        cand = CandidateDB.get(self.selected_candidate_id)
        if not cand: return
        
        school = SchoolInfoDB.get()
        payments = PaymentDB.get_by_candidate(cand['id'])
        total_paid = sum(p['amount'] for p in payments)
        rem = cand['total_amount'] - total_paid

        import tempfile, os
        from datetime import datetime
        temp_dir = tempfile.gettempdir()
        filename = f"receipt_{cand['id']}_{int(datetime.now().timestamp())}.html"
        path = os.path.join(temp_dir, filename)

        # إنشاء صفحة HTML للوصل لكي تفتح في المتصفح وتطبع تلقائياً
        school_name = school.get('name', 'مدرسة تعليم السياقة')
        school_address = school.get('address', '')
        school_phone = school.get('phone', '')
        cand_name = f"{cand.get('last_name','')} {cand.get('first_name','')}"
        cand_phone = cand.get('phone', '')
        
        rows_html = ""
        for i, p in enumerate(payments, 1):
            notes = p.get('notes', '') or '-'
            method = p.get('payment_method', '')
            amt = f"{p['amount']:,.0f}"
            date_str = p.get('date', '')
            rows_html += f"<tr><td>{i}</td><td>{date_str}</td><td>{amt}</td><td>{method}</td><td>{notes}</td></tr>"

        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>وصل دفع - {cand_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 30px; font-size: 15px; color: #111; }}
                .header {{ text-align: center; border-bottom: 3px solid #2563eb; padding-bottom: 15px; margin-bottom: 30px; }}
                .header h1 {{ margin: 0 0 10px 0; color: #1e3a8a; font-size: 26px; }}
                .header p {{ margin: 5px 0; font-size: 14px; color: #444; }}
                .title {{ text-align: center; font-size: 22px; font-weight: bold; margin: 20px 0; border: 1px solid #ccc; display: inline-block; padding: 10px 40px; border-radius: 5px; background: #f8fafc; }}
                .center-title {{ text-align: center; }}
                .info {{ margin-bottom: 30px; font-size: 16px; }}
                .info p {{ margin: 8px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 15px; }}
                th, td {{ border: 1px solid #cbd5e1; padding: 12px 8px; text-align: center; }}
                th {{ background-color: #2563eb; color: white; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f8fafc; }}
                .summary-container {{ display: flex; justify-content: flex-end; }}
                .summary {{ width: 50%; }}
                .summary th {{ background-color: #f1f5f9; color: #111; text-align: right; padding-right: 15px; }}
                .summary td {{ font-weight: bold; font-size: 16px; }}
                .footer {{ margin-top: 50px; text-align: left; padding-left: 10%; font-size: 16px; }}
                .footer p {{ margin: 10px 0; }}
                @media print {{
                    @page {{ margin: 1cm; }}
                    body {{ padding: 0; }}
                    .title {{ border: 1px solid #000; }}
                    th {{ background-color: #ddd !important; color: #000 !important; -webkit-print-color-adjust: exact; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9 !important; -webkit-print-color-adjust: exact; }}
                }}
            </style>
        </head>
        <body onload="setTimeout(function(){{ window.print(); }}, 500);">
            <div class="header">
                <h1>{school_name}</h1>
                <p>العنوان: {school_address} | الهاتف: {school_phone}</p>
            </div>
            
            <div class="center-title">
                <div class="title">وصل دفع</div>
            </div>
            
            <div class="info">
                <p><strong>المترشح:</strong> {cand_name}</p>
                <p><strong>رقم الهاتف:</strong> {cand_phone}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>رقم</th>
                        <th>التاريخ</th>
                        <th>المبلغ (دج)</th>
                        <th>طريقة الدفع</th>
                        <th>ملاحظة</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <div class="summary-container">
                <table class="summary">
                    <tr><th>المبلغ الإجمالي للتكوين</th><td>{cand['total_amount']:,.0f} دج</td></tr>
                    <tr><th>مجموع المدفوعات</th><td>{total_paid:,.0f} دج</td></tr>
                    <tr><th>المبلغ المتبقي</th><td>{rem:,.0f} دج</td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>حُرّر بتاريخ: {date.today().strftime('%Y-%m-%d')}</p>
                <br>
                <p>ختم وتوقيع المسؤول: ............................</p>
            </div>
        </body>
        </html>
        """
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            try:
                os.startfile(path, 'print')
            except Exception:
                os.startfile(path)
        except Exception as e:
            show_error(f"حدث خطأ أثناء طباعة الوصل:\n{e}")

    def _refund(self):
        if not self.selected_candidate_id:
            show_error("يرجى تحديد مترشح من القائمة أولاً"); return
        try:
            amt_str = self.vars["amount"].get().replace(",", ".").replace(" ", "")
            amt = float(amt_str or 0)
            if amt <= 0:
                show_error("يرجى إدخال مبلغ صحيح أكبر من الصفر"); return
        except ValueError:
            show_error("المبلغ يجب أن يكون رقماً (تأكد من عدم وجود مسافات غير ضرورية)"); return
        notes = self.vars["notes"].get().strip()
        notes = f"استرداد مبلغ: {notes}" if notes else "استرداد مبلغ"
        PaymentDB.add({"candidate_id": self.selected_candidate_id,
                       "date": self.vars["date"].get().strip() or str(date.today()),
                       "amount": -amt,
                       "payment_method": self.vars["payment_method"].get() or "نقدي",
                       "notes": notes})
        self.vars["amount"].set(""); self.vars["notes"].set("")
        self._refresh_candidate_ui()
        show_info("تم استرداد المبلغ بنجاح")

    def _delete(self):
        if not self.selected_payment_id:
            show_error("يرجى تحديد دفعة من السجل"); return
        if confirm_delete("هذه الدفعة"):
            PaymentDB.delete(self.selected_payment_id)
            self.selected_payment_id = None
            self._refresh_candidate_ui()
            show_info("تم حذف الدفعة")


# ============================================================================
#  واجهة: المصاريف
# ============================================================================

class ExpensesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_id = None
        self.vars = {}
        self._build(); self._load_list()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text="💸  إدارة المصاريف",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=(0, 5))
        tk.Label(wrap, text="تسجيل ومتابعة كل المصاريف الشهرية والسنوية",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(fill="x", pady=(0, 15))

        bottom = tk.Frame(wrap, bg=COLOR_BG); bottom.pack(fill="both", expand=True)

        # يمين: نموذج
        right = tk.Frame(bottom, bg=COLOR_BG, width=340); right.pack(side="right", fill="y")
        right.pack_propagate(False)
        fo, fc = make_card(right); fo.pack(fill="both", expand=True, padx=(10, 0))
        section_title(fc, "بيانات المصروف", icon="💸")

        fields = [("نوع المصروف *", "expense_type", "combo", EXPENSE_TYPES),
                  ("المبلغ (دج) *", "amount", "entry"),
                  ("التاريخ *", "date", "entry"),
                  ("ملاحظة", "notes", "entry")]
        for fi in fields:
            row = tk.Frame(fc, bg=COLOR_CARD); row.pack(fill="x", pady=8)
            make_label(row, fi[0], font=FONT_BOLD).pack(anchor="e")
            v = tk.StringVar(); self.vars[fi[1]] = v
            if fi[2] == "combo":
                w = make_combo(row, v, fi[3], width=22, state="normal")
            else:
                w = make_entry(row, v, width=24)
            w.pack(fill="x", ipady=5, pady=(3, 0))
        self.vars["date"].set(str(date.today()))

        bf = tk.Frame(fc, bg=COLOR_CARD); bf.pack(fill="x", pady=(15, 0))
        ModernButton(bf, "إضافة", self._add, icon="➕",
                     color=COLOR_SUCCESS).pack(fill="x", pady=3)
        ModernButton(bf, "تعديل", self._update, icon="✏️",
                     color=COLOR_PRIMARY).pack(fill="x", pady=3)
        ModernButton(bf, "حذف", self._delete, icon="🗑️",
                     color=COLOR_DANGER).pack(fill="x", pady=3)
        ModernButton(bf, "مسح الحقول", self._clear, icon="🔄",
                     color=COLOR_TEXT_LIGHT).pack(fill="x", pady=3)

        # يسار: جدول
        lo, lc = make_card(bottom, padding=10); lo.pack(side="left", fill="both",
                                                        expand=True, padx=(0, 10))
        sb_outer, sb = make_card(lc, padding=10); sb_outer.pack(fill="x", pady=(0, 5))
        tk.Label(sb, text="🔍", font=(FONT_FAMILY, 14),
                 bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(side="right", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_list())
        make_entry(sb, self.search_var, width=30).pack(side="right", fill="x",
                                                       expand=True, ipady=5)
        tk.Label(sb, text="بحث:", font=FONT_BOLD, bg=COLOR_CARD,
                 fg=COLOR_TEXT, anchor="e").pack(side="right", padx=10)

        self.tree = create_treeview(lc,
            ("id","expense_type","amount","date","notes"),
            ("رقم","نوع المصروف","المبلغ (دج)","التاريخ","ملاحظة"),
            (50,180,140,130,260), height=15)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load_list(self):
        rows = ExpenseDB.get_all(self.search_var.get())
        values = [(r['id'], r['expense_type'], f"{r['amount']:,.0f}",
                   r['date'], r['notes']) for r in rows]
        insert_zebra(self.tree, values)

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        rid = self.tree.item(sel[0])['values'][0]
        self.selected_id = rid
        for r in ExpenseDB.get_all():
            if r['id'] == rid:
                self.vars["expense_type"].set(r['expense_type'])
                self.vars["amount"].set(str(r['amount']))
                self.vars["date"].set(r['date'])
                self.vars["notes"].set(r['notes'])
                break

    def _data(self):
        try: amt = float(self.vars["amount"].get() or 0)
        except ValueError: amt = 0
        return {"expense_type": self.vars["expense_type"].get().strip(),
                "amount": amt,
                "date": self.vars["date"].get().strip() or str(date.today()),
                "notes": self.vars["notes"].get().strip()}

    def _add(self):
        d = self._data()
        if not d["expense_type"]:
            show_error("يرجى إدخال نوع المصروف"); return
        if d["amount"] <= 0:
            show_error("يرجى إدخال مبلغ صحيح"); return
        ExpenseDB.add(d); self._clear(); self._load_list()
        show_info("تم إضافة المصروف بنجاح")

    def _update(self):
        if not self.selected_id:
            show_error("يرجى تحديد مصروف من القائمة"); return
        ExpenseDB.update(self.selected_id, self._data())
        self._load_list()
        show_info("تم تعديل المصروف")

    def _delete(self):
        if not self.selected_id:
            show_error("يرجى تحديد مصروف من القائمة"); return
        if confirm_delete("هذا المصروف"):
            ExpenseDB.delete(self.selected_id)
            self._clear(); self._load_list()
            show_info("تم حذف المصروف")

    def _clear(self):
        self.selected_id = None
        for v in self.vars.values(): v.set("")
        self.vars["date"].set(str(date.today()))


# ============================================================================
#  واجهة: التقارير
# ============================================================================

class ReportsFrame(tk.Frame):
    def __init__(self, parent, navigate_cb=None):
        super().__init__(parent, bg=COLOR_BG)
        self._navigate_cb = navigate_cb
        self._build()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text="📊  التقارير والإحصائيات",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=(0, 5))
        tk.Label(wrap, text="تقارير شهرية وسنوية مفصّلة",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(fill="x", pady=(0, 15))

        # شريط الفلتر
        fo, fc = make_card(wrap, padding=15); fo.pack(fill="x", pady=(0, 15))
        tk.Label(fc, text="السنة:", font=FONT_BOLD,
                 bg=COLOR_CARD, anchor="e").pack(side="right", padx=5)
        self.year_var = tk.StringVar(value=str(date.today().year))
        make_combo(fc, self.year_var,
                   [str(y) for y in range(date.today().year, 2019, -1)],
                   width=10).pack(side="right", padx=5, ipady=4)
        tk.Label(fc, text="الشهر:", font=FONT_BOLD,
                 bg=COLOR_CARD, anchor="e").pack(side="right", padx=5)
        self.month_var = tk.StringVar(value=f"{date.today().month:02d}")
        make_combo(fc, self.month_var,
                   [f"{m:02d}" for m in range(1, 13)],
                   width=8).pack(side="right", padx=5, ipady=4)
        ModernButton(fc, "تحديث التقارير", self._refresh, icon="📈",
                     color=COLOR_PRIMARY).pack(side="right", padx=15)

        # بطاقات إحصائية
        self.stats_row = tk.Frame(wrap, bg=COLOR_BG); self.stats_row.pack(fill="x", pady=(0, 15))

        # تفصيل شهري
        mo, mc = make_card(wrap, padding=10); mo.pack(fill="x", pady=(0, 12))
        section_title(mc, "تفصيل شهري للسنة المحددة", icon="📅")
        self.monthly_tree = create_treeview(mc,
            ("month","payments","expenses","profit"),
            ("الشهر","المدفوعات (دج)","المصاريف (دج)","الأرباح (دج)"),
            (140,180,180,180), height=8)

        # إحصائيات الامتحانات
        eo, ec = make_card(wrap, padding=10); eo.pack(fill="both", expand=True)
        section_title(ec, "إحصائيات نتائج الامتحانات", icon="🎓")
        self._exam_stats_row = tk.Frame(ec, bg=COLOR_CARD)
        self._exam_stats_row.pack(fill="x", pady=(0, 8))

        # -- مخطط شريطي شهري --
        chart_lbl = tk.Label(ec,
            text="مخطط النجاح الشهري  (🟦 نظري ناجح  |  🟩 تطبيقي ناجح  |  ◻ محاولات)",
            font=FONT_SMALL, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, anchor="e")
        chart_lbl.pack(anchor="e", pady=(0, 4))
        self._exam_chart = tk.Canvas(ec, bg=COLOR_CARD, height=160,
                                     highlightthickness=0)
        self._exam_chart.pack(fill="x", padx=4, pady=(0, 8))

        # -- جدول تفصيلي --
        self._exam_monthly_tree = create_treeview(ec,
            ("month", "nazari_total", "nazari_pass", "tatbiqi_total", "tatbiqi_pass"),
            ("الشهر", "نظري (محاولات)", "نظري (ناجح)", "تطبيقي (محاولات)", "تطبيقي (ناجح)"),
            (120, 140, 120, 160, 130), height=5)

        self._refresh()

    def _refresh(self):
        y = self.year_var.get(); m = self.month_var.get()
        tp = PaymentDB.get_total_by_year(y); te = ExpenseDB.get_total_by_year(y)
        prof = tp - te
        mp = PaymentDB.get_total_by_month(y, int(m))
        me = ExpenseDB.get_total_by_month(y, int(m))
        mpr = mp - me
        nc = len(CandidateDB.get_all()); ni = len(InstructorDB.get_all())

        # إعادة بناء البطاقات
        for w in self.stats_row.winfo_children(): w.destroy()
        nav = self._navigate_cb
        go_pay  = (lambda: nav(6)) if nav else None
        go_exp  = (lambda: nav(7)) if nav else None
        # بطاقتا الأرباح: تنتقل للتقارير ذاتها لعرض التفاصيل (index 8)
        go_rep  = (lambda: nav(8)) if nav else None
        stat_card(self.stats_row, f"مدفوعات {y}",  f"{tp:,.0f}", "💰", COLOR_SUCCESS,
                  command=go_pay)
        stat_card(self.stats_row, f"مصاريف {y}",   f"{te:,.0f}", "💸", COLOR_DANGER,
                  command=go_exp)
        stat_card(self.stats_row, f"أرباح {y}",    f"{prof:,.0f}", "💎",
                  COLOR_PRIMARY if prof >= 0 else COLOR_DANGER,
                  command=go_rep)
        mn = MONTHS_AR.get(m, m)
        stat_card(self.stats_row, f"أرباح {mn}", f"{mpr:,.0f}", "📅",
                  COLOR_PURPLE if mpr >= 0 else COLOR_DANGER,
                  command=go_rep)

        # تفصيل شهري — النقر المزدوج على صف ينتقل لقسم المدفوعات
        ap = {r['month']: r['total'] for r in PaymentDB.get_monthly_breakdown(y)}
        ae = {r['month']: r['total'] for r in ExpenseDB.get_monthly_breakdown(y)}
        rows = []
        for mm in range(1, 13):
            ms = f"{mm:02d}"; p = ap.get(ms, 0); e = ae.get(ms, 0)
            rows.append((MONTHS_AR.get(ms, ms), f"{p:,.0f}", f"{e:,.0f}", f"{p - e:,.0f}"))
        insert_zebra(self.monthly_tree, rows)

        # نقر مزدوج على صف التفصيل الشهري → ينتقل للمدفوعات
        def _on_month_dbl(e):
            if nav:
                nav(6)
        self.monthly_tree.bind("<Double-Button-1>", _on_month_dbl)
        self.monthly_tree.configure(cursor="hand2")

        # ── إحصائيات الامتحانات ──────────────────────────────────────────────
        for w in self._exam_stats_row.winfo_children():
            w.destroy()

        pass_data = ExamResultDB.get_pass_rate_by_type()
        total_all = sum(r['total'] for r in pass_data)
        passed_all = sum(r['passed'] for r in pass_data)
        overall_pct = int(passed_all / total_all * 100) if total_all else 0

        # بطاقة المعدل الكلي
        overall_color = COLOR_SUCCESS if overall_pct >= 50 else (COLOR_WARNING if total_all == 0 else COLOR_DANGER)
        stat_card(self._exam_stats_row,
                  "المعدل الكلي للنجاح",
                  f"{overall_pct}%",
                  "🎓", overall_color)

        # بطاقة لكل نوع
        for r in pass_data:
            total  = r['total']
            passed = r['passed']
            pct    = int(passed / total * 100) if total else 0
            color  = COLOR_SUCCESS if pct >= 50 else (COLOR_WARNING if total == 0 else COLOR_DANGER)
            stat_card(self._exam_stats_row,
                      f"نجاح {r['exam_type']}",
                      f"{pct}%  ({passed}/{total})",
                      "📝", color)

        # جدول التفصيل الشهري للامتحانات + المخطط الشريطي
        monthly_exam = ExamResultDB.get_monthly_breakdown(y)
        # بناء قاموس {شهر → {نوع → {total, passed}}}
        em = {}
        for r in monthly_exam:
            mo_ = r['month']
            em.setdefault(mo_, {})
            em[mo_][r['exam_type']] = {"total": r['total'], "passed": r['passed']}

        exam_rows = []
        for mm in range(1, 13):
            ms = f"{mm:02d}"
            naz  = em.get(ms, {}).get("نظري",    {"total": 0, "passed": 0})
            tat  = em.get(ms, {}).get("تطبيقي",  {"total": 0, "passed": 0})
            exam_rows.append((
                MONTHS_AR.get(ms, ms),
                str(naz['total'])  if naz['total']  else "—",
                str(naz['passed']) if naz['total']  else "—",
                str(tat['total'])  if tat['total']  else "—",
                str(tat['passed']) if tat['total']  else "—",
            ))
        insert_zebra(self._exam_monthly_tree, exam_rows)

        # ── رسم المخطط الشريطي الشهري ─────────────────────────────────────
        self._draw_exam_bar_chart(em)

    def _draw_exam_bar_chart(self, em):
        """يرسم مخططاً شريطياً شهرياً على Canvas يُظهر ناجحي نظري وتطبيقي."""
        canvas = self._exam_chart
        canvas.delete("all")
        canvas.update_idletasks()

        W = canvas.winfo_width() or 700
        H = 160
        pad_l, pad_r, pad_top, pad_bot = 30, 10, 14, 28

        months_abbr = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                        "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

        # حساب البيانات لـ12 شهر
        data = []
        for mm in range(1, 13):
            ms = f"{mm:02d}"
            naz = em.get(ms, {}).get("نظري",   {"total": 0, "passed": 0})
            tat = em.get(ms, {}).get("تطبيقي", {"total": 0, "passed": 0})
            data.append((naz['total'], naz['passed'], tat['total'], tat['passed']))

        max_val = max((max(d) for d in data), default=1) or 1
        chart_h = H - pad_top - pad_bot
        chart_w = W - pad_l - pad_r
        group_w = chart_w / 12
        bar_w   = max(3, int(group_w / 3) - 2)

        # خط قاعدة
        base_y = H - pad_bot
        canvas.create_line(pad_l, pad_top, pad_l, base_y,
                           fill=COLOR_BORDER, width=1)
        canvas.create_line(pad_l, base_y, W - pad_r, base_y,
                           fill=COLOR_BORDER, width=1)

        # خطوط دليل
        for fraction in (0.25, 0.5, 0.75, 1.0):
            gy = base_y - int(chart_h * fraction)
            canvas.create_line(pad_l, gy, W - pad_r, gy,
                               fill="#e2e8f0", dash=(4, 4))
            lbl_val = int(max_val * fraction)
            canvas.create_text(pad_l - 4, gy, text=str(lbl_val),
                                font=(FONT_FAMILY, 7), fill=COLOR_TEXT_LIGHT,
                                anchor="e")

        BLUE   = COLOR_PRIMARY    # نظري ناجح
        GREEN  = COLOR_SUCCESS    # تطبيقي ناجح
        GRAY   = "#CBD5E1"        # محاولات (مجموع)

        for i, (naz_tot, naz_pass, tat_tot, tat_pass) in enumerate(data):
            cx = pad_l + i * group_w + group_w / 2

            def bar(value, color, offset):
                if value <= 0:
                    return
                bh = max(2, int(chart_h * value / max_val))
                x0 = int(cx + offset - bar_w / 2)
                x1 = x0 + bar_w
                y0 = base_y - bh
                canvas.create_rectangle(x0, y0, x1, base_y,
                                        fill=color, outline="", width=0)

            bar(naz_tot,  GRAY,  -bar_w - 1)
            bar(naz_pass, BLUE,  -bar_w - 1)
            bar(tat_tot,  GRAY,   bar_w + 1)
            bar(tat_pass, GREEN,  bar_w + 1)

            # اسم الشهر (حروف مختصرة — أول 3 حروف)
            canvas.create_text(int(cx), base_y + 4,
                                text=months_abbr[i][:3],
                                font=(FONT_FAMILY, 7), fill=COLOR_TEXT_LIGHT,
                                anchor="n")

        # أعد رسم عند تغيير الحجم
        canvas.bind("<Configure>", lambda e: self._draw_exam_bar_chart(em))


# ============================================================================
#  واجهة: الوثائق (طباعة PDF بالعربية)
# ============================================================================

def _pdf_styles():
    """يبني أنماط فقرات تدعم العربية."""
    base = ParagraphStyle('base', fontName=ARABIC_FONT, fontSize=11, leading=18)
    return {
        "title":  ParagraphStyle('title',  parent=base, fontName=ARABIC_FONT_BOLD,
                                  fontSize=16, alignment=TA_CENTER, leading=22),
        "h2":     ParagraphStyle('h2',     parent=base, fontName=ARABIC_FONT_BOLD,
                                  fontSize=13, alignment=TA_RIGHT, leading=20),
        "right":  ParagraphStyle('right',  parent=base, alignment=TA_RIGHT, leading=20),
        "center": ParagraphStyle('center', parent=base, alignment=TA_CENTER, leading=20),
        "small_right": ParagraphStyle('sr', parent=base, alignment=TA_RIGHT,
                                       fontSize=10, leading=14),
    }


def _pdf_header(story, school, title):
    s = _pdf_styles()
    story.append(Paragraph(ar("الجمهورية الجزائرية الديمقراطية الشعبية"), s["small_right"]))
    if school.get('name'):
        story.append(Paragraph(ar(school['name']), s["h2"]))
    info_line = []
    if school.get('phone'):    info_line.append(f"الهاتف: {school['phone']}")
    if school.get('address'):  info_line.append(f"العنوان: {school['address']}")
    if info_line:
        story.append(Paragraph(ar(" | ".join(info_line)), s["small_right"]))
    if school.get('accreditation_number'):
        story.append(Paragraph(ar(f"رقم الاعتماد: {school['accreditation_number']}"),
                               s["small_right"]))
    story.append(Spacer(1, 0.4*cm))
    # خط فاصل
    line_table = Table([[""]], colWidths=[17*cm])
    line_table.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1.2, colors.HexColor('#2563eb'))]))
    story.append(line_table)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(ar(title), s["title"]))
    story.append(Spacer(1, 0.6*cm))


def _styled_table(data_rows, col_widths):
    """يصنع جدولاً منسقاً بنصوص عربية مُعالجة."""
    processed = [[ar(c) for c in row] for row in data_rows]
    t = Table(processed, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), ARABIC_FONT),
        ('FONTNAME', (0,0), (-1,0),  ARABIC_FONT_BOLD),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
            [colors.white, colors.HexColor('#f1f5f9')]),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    return t


# ============================================================================
#  نافذة إضافة / تعديل حصة تدريبية
# ============================================================================

class SessionDialog(tk.Toplevel):
    """نافذة Toplevel لإدخال بيانات حصة مع فحص تعارض الممرّن والمركبة."""

    def __init__(self, parent, session_id=None, on_save=None):
        super().__init__(parent)
        self.session_id = session_id
        self.on_save    = on_save
        self.title("تعديل حصة تدريبية" if session_id else "إضافة حصة جديدة")
        self.geometry("580x600")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=COLOR_BG)
        self._vars     = {}
        self._cand_map = {}   # display_name -> id
        self._inst_map = {}   # display_name -> id
        self._veh_map  = {}   # display_name -> id  (None = بدون مركبة)
        self._build()
        if session_id:
            self._load()

    # ──────────────────────────────────────────────────────────
    def _build(self):
        hdr = tk.Frame(self, bg=COLOR_PRIMARY, padx=16, pady=12)
        hdr.pack(fill="x")
        icon = "✏️" if self.session_id else "➕"
        tk.Label(hdr,
                 text=f"{icon}  {'تعديل حصة تدريبية' if self.session_id else 'إضافة حصة جديدة'}",
                 font=(FONT_FAMILY, 14, "bold"), bg=COLOR_PRIMARY, fg="white").pack(anchor="e")

        wrap = tk.Frame(self, bg=COLOR_BG, padx=24, pady=14)
        wrap.pack(fill="both", expand=True)

        cands = CandidateDB.get_all()
        insts = InstructorDB.get_all()
        vehs  = VehicleDB.get_all()

        self._cand_map = {f"{c['last_name']} {c['first_name']}": c['id'] for c in cands}
        self._inst_map = {f"{i['last_name']} {i['first_name']}": i['id'] for i in insts}
        # مركبات: "بلا مركبة" + كل مركبة
        self._veh_map  = {"بلا مركبة": None}
        for v in vehs:
            label = f"{v['model']} ({v.get('plate_number','') or '—'})"
            self._veh_map[label] = v['id']

        def lbl(text):
            tk.Label(wrap, text=text, font=FONT_BOLD,
                     bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")

        # المترشح
        lbl("المترشح *")
        self._vars['candidate'] = tk.StringVar()
        ttk.Combobox(wrap, textvariable=self._vars['candidate'],
                     values=list(self._cand_map.keys()),
                     state="readonly", font=FONT_MAIN,
                     justify="right").pack(fill="x", ipady=4, pady=(4, 10))

        # صف: الممرّن + المركبة
        im_row = tk.Frame(wrap, bg=COLOR_BG)
        im_row.pack(fill="x", pady=(0, 10))

        inst_col = tk.Frame(im_row, bg=COLOR_BG)
        inst_col.pack(side="right", fill="both", expand=True, padx=(6, 0))
        tk.Label(inst_col, text="الممرّن *", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._vars['instructor'] = tk.StringVar()
        ttk.Combobox(inst_col, textvariable=self._vars['instructor'],
                     values=list(self._inst_map.keys()),
                     state="readonly", font=FONT_MAIN,
                     justify="right").pack(fill="x", ipady=4)

        veh_col = tk.Frame(im_row, bg=COLOR_BG)
        veh_col.pack(side="left", fill="both", expand=True)
        tk.Label(veh_col, text="المركبة", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._vars['vehicle'] = tk.StringVar(value="بلا مركبة")
        ttk.Combobox(veh_col, textvariable=self._vars['vehicle'],
                     values=list(self._veh_map.keys()),
                     state="readonly", font=FONT_MAIN,
                     justify="right").pack(fill="x", ipady=4)

        # صف: التاريخ + الوقت
        dt_row = tk.Frame(wrap, bg=COLOR_BG)
        dt_row.pack(fill="x", pady=(0, 10))

        date_col = tk.Frame(dt_row, bg=COLOR_BG)
        date_col.pack(side="right", fill="both", expand=True, padx=(6, 0))
        tk.Label(date_col, text="التاريخ * (YYYY-MM-DD)", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._vars['session_date'] = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        tk.Entry(date_col, textvariable=self._vars['session_date'],
                 font=FONT_MAIN, justify="right",
                 relief="solid", bd=1).pack(fill="x", ipady=5)

        time_col = tk.Frame(dt_row, bg=COLOR_BG)
        time_col.pack(side="left", fill="both", expand=True)
        tk.Label(time_col, text="الوقت *", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._vars['session_time'] = tk.StringVar(value="08:00")
        ttk.Combobox(time_col, textvariable=self._vars['session_time'],
                     values=TIME_OPTIONS, font=FONT_MAIN,
                     justify="right").pack(fill="x", ipady=4)

        # صف: المدة + نوع الحصة
        dd_row = tk.Frame(wrap, bg=COLOR_BG)
        dd_row.pack(fill="x", pady=(0, 10))

        dur_col = tk.Frame(dd_row, bg=COLOR_BG)
        dur_col.pack(side="right", fill="both", expand=True, padx=(6, 0))
        tk.Label(dur_col, text="المدة (دقيقة) *", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._vars['duration'] = tk.StringVar(value="60")
        ttk.Combobox(dur_col, textvariable=self._vars['duration'],
                     values=DURATION_OPTIONS, font=FONT_MAIN,
                     justify="right").pack(fill="x", ipady=4)

        type_col = tk.Frame(dd_row, bg=COLOR_BG)
        type_col.pack(side="left", fill="both", expand=True)
        tk.Label(type_col, text="نوع الحصة", font=FONT_BOLD,
                 bg=COLOR_BG, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._vars['session_type'] = tk.StringVar(value=SESSION_TYPE_OPTIONS[0])
        ttk.Combobox(type_col, textvariable=self._vars['session_type'],
                     values=SESSION_TYPE_OPTIONS, state="readonly",
                     font=FONT_MAIN, justify="right").pack(fill="x", ipady=4)

        # ملاحظات
        lbl("ملاحظات")
        self._notes_txt = tk.Text(wrap, height=3, font=FONT_MAIN,
                                  relief="solid", bd=1)
        self._notes_txt.pack(fill="x", pady=(4, 0))

        # رسالة تعارض
        self._conflict_var = tk.StringVar()
        tk.Label(wrap, textvariable=self._conflict_var,
                 font=FONT_SMALL, bg=COLOR_BG, fg=COLOR_DANGER,
                 anchor="e", wraplength=540).pack(fill="x", pady=(6, 0))

        # أزرار
        bf = tk.Frame(self, bg=COLOR_BG, padx=24, pady=12)
        bf.pack(fill="x")
        ModernButton(bf, text="حفظ", icon="💾",
                     color=COLOR_SUCCESS, command=self._save).pack(side="right")
        ModernButton(bf, text="إلغاء", icon="✖",
                     color=COLOR_DANGER, command=self.destroy).pack(side="right", padx=(0, 8))

    # ──────────────────────────────────────────────────────────
    def _load(self):
        s = SessionDB.get(self.session_id)
        if not s:
            return
        cand = CandidateDB.get(s['candidate_id'])
        if cand:
            self._vars['candidate'].set(f"{cand['last_name']} {cand['first_name']}")
        inst = InstructorDB.get(s['instructor_id'])
        if inst:
            self._vars['instructor'].set(f"{inst['last_name']} {inst['first_name']}")
        # المركبة
        vid = s.get('vehicle_id')
        if vid:
            for label, lid in self._veh_map.items():
                if lid == vid:
                    self._vars['vehicle'].set(label)
                    break
        else:
            self._vars['vehicle'].set("بلا مركبة")
        self._vars['session_date'].set(s.get('session_date', ''))
        self._vars['session_time'].set(s.get('session_time', '08:00'))
        self._vars['duration'].set(str(s.get('duration', 60)))
        self._vars['session_type'].set(s.get('session_type', SESSION_TYPE_OPTIONS[0]))
        self._notes_txt.insert("1.0", s.get('notes', ''))

    # ──────────────────────────────────────────────────────────
    def _save(self):
        cand_name = self._vars['candidate'].get().strip()
        inst_name = self._vars['instructor'].get().strip()
        s_date    = self._vars['session_date'].get().strip()
        s_time    = self._vars['session_time'].get().strip()
        duration  = self._vars['duration'].get().strip()
        veh_name  = self._vars['vehicle'].get().strip()

        # ── التحقق من الحقول الإلزامية ──
        if not all([cand_name, inst_name, s_date, s_time, duration]):
            show_error("يرجى ملء جميع الحقول الإلزامية (*)"); return
        if cand_name not in self._cand_map:
            show_error("يرجى اختيار مترشح صحيح من القائمة"); return
        if inst_name not in self._inst_map:
            show_error("يرجى اختيار ممرّن صحيح من القائمة"); return

        # ── التحقق من صيغة التاريخ ──
        try:
            datetime.strptime(s_date, '%Y-%m-%d')
        except ValueError:
            show_error("صيغة التاريخ غير صحيحة، استخدم: YYYY-MM-DD"); return

        # ── التحقق من صيغة الوقت ──
        try:
            datetime.strptime(s_time, '%H:%M')
        except ValueError:
            show_error("صيغة الوقت غير صحيحة، اختر من القائمة (HH:MM)"); return

        # ── التحقق من المدة ──
        try:
            dur_int = int(duration)
            if dur_int <= 0 or dur_int > 480:
                raise ValueError
        except ValueError:
            show_error("المدة يجب أن تكون رقماً موجباً (دقائق) لا تتجاوز 480"); return

        inst_id = self._inst_map[inst_name]
        veh_id  = self._veh_map.get(veh_name)  # None إذا "بلا مركبة"

        # ── فحص تعارض الممرّن والمركبة ──
        inst_conflicts, veh_conflicts = SessionDB.check_conflict(
            inst_id, s_date, s_time, duration,
            vehicle_id=veh_id, exclude_id=self.session_id)

        conflict_msgs = []
        if inst_conflicts:
            c = inst_conflicts[0]
            conflict_msgs.append(
                f"الممرّن لديه حصة في {c['session_time']} (مدة {c['duration']} د.)")
        if veh_conflicts:
            c = veh_conflicts[0]
            conflict_msgs.append(
                f"المركبة مستخدمة في {c['session_time']} (مدة {c['duration']} د.)")

        if conflict_msgs:
            msg = "⚠️  تعارض في الجدول:\n" + "\n".join(conflict_msgs)
            self._conflict_var.set(msg)
            if not messagebox.askyesno("تعارض في الجدول",
                    msg + f"\nبتاريخ {s_date}.\nهل تريد الحفظ رغم التعارض؟"):
                return
        else:
            self._conflict_var.set("")

        d = {
            'candidate_id':  self._cand_map[cand_name],
            'instructor_id': inst_id,
            'vehicle_id':    veh_id,
            'session_date':  s_date,
            'session_time':  s_time,
            'duration':      dur_int,
            'session_type':  self._vars['session_type'].get(),
            'notes':         self._notes_txt.get("1.0", "end-1c").strip(),
        }
        if self.session_id:
            SessionDB.update(self.session_id, d)
        else:
            SessionDB.add(d)

        if self.on_save:
            self.on_save()
        self.destroy()


# ============================================================================
#  واجهة: الجدول الزمني للحصص
# ============================================================================

class ScheduleFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_id = None
        self._build()
        self._load()

    # ──────────────────────────────────────────────────────────
    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=16)
        wrap.pack(fill="both", expand=True)

        # ── العنوان ──
        tk.Label(wrap, text="📅  الجدول الزمني للحصص",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=(0, 4))
        tk.Label(wrap, text="إدارة وتنظيم حصص التدريب — عرض، إضافة، تعديل وحذف",
                 font=FONT_MAIN, bg=COLOR_BG,
                 fg=COLOR_TEXT_LIGHT, anchor="e").pack(fill="x", pady=(0, 14))

        # ── شريط الفلاتر والأزرار ──
        ctl = tk.Frame(wrap, bg=COLOR_BG)
        ctl.pack(fill="x", pady=(0, 10))

        # أزرار (يمين)
        btn_row = tk.Frame(ctl, bg=COLOR_BG)
        btn_row.pack(side="right")
        ModernButton(btn_row, text="إضافة حصة", icon="➕",
                     color=COLOR_SUCCESS,
                     command=self._add).pack(side="right")
        ModernButton(btn_row, text="تعديل", icon="✏️",
                     color=COLOR_PRIMARY,
                     command=self._edit).pack(side="right", padx=(0, 6))
        ModernButton(btn_row, text="حذف", icon="🗑",
                     color=COLOR_DANGER,
                     command=self._delete).pack(side="right", padx=(0, 6))

        # فلاتر (يسار)
        filter_row = tk.Frame(ctl, bg=COLOR_BG)
        filter_row.pack(side="left")

        tk.Label(filter_row, text="🔍", font=(FONT_FAMILY, 14),
                 bg=COLOR_BG).pack(side="left", padx=(0, 4))

        # فلتر التاريخ
        tk.Label(filter_row, text="التاريخ:", font=FONT_SMALL,
                 bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left")
        self._date_var = tk.StringVar()
        tk.Entry(filter_row, textvariable=self._date_var, width=12,
                 font=FONT_MAIN, relief="solid", bd=1,
                 justify="right").pack(side="left", padx=4)

        # فلتر الممرّن
        tk.Label(filter_row, text="الممرّن:", font=FONT_SMALL,
                 bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left", padx=(8, 0))
        self._inst_filter_var = tk.StringVar()
        insts = ["الكل"] + [f"{i['last_name']} {i['first_name']}"
                            for i in InstructorDB.get_all()]
        self._inst_combo = ttk.Combobox(filter_row,
                                         textvariable=self._inst_filter_var,
                                         values=insts, state="readonly",
                                         width=14, font=FONT_SMALL)
        self._inst_combo.current(0)
        self._inst_combo.pack(side="left", padx=4)

        # فلتر المترشح
        tk.Label(filter_row, text="المترشح:", font=FONT_SMALL,
                 bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left", padx=(8, 0))
        self._cand_filter_var = tk.StringVar()
        cands = ["الكل"] + [f"{c['last_name']} {c['first_name']}"
                             for c in CandidateDB.get_all()]
        self._cand_combo = ttk.Combobox(filter_row,
                                         textvariable=self._cand_filter_var,
                                         values=cands, state="readonly",
                                         width=14, font=FONT_SMALL)
        self._cand_combo.current(0)
        self._cand_combo.pack(side="left", padx=4)

        ModernButton(filter_row, text="تصفية", icon="🔎",
                     color=COLOR_INFO, size="small",
                     command=self._load).pack(side="left", padx=4)
        ModernButton(filter_row, text="كل الحصص", icon="↺",
                     color=COLOR_TEXT_LIGHT, size="small",
                     command=self._reset_filter).pack(side="left")

        # ── ملخص سريع للأسبوع ──
        self._week_lbl = tk.Label(wrap, text="",
                                   font=FONT_SMALL, bg=COLOR_BG,
                                   fg=COLOR_TEXT_LIGHT, anchor="e")
        self._week_lbl.pack(fill="x", pady=(0, 6))

        # ── الجدول ──
        tbl_outer, tbl_body = make_card(wrap)
        tbl_outer.pack(fill="both", expand=True)

        self.tree = create_treeview(tbl_body,
            ("date", "time", "dur", "type", "candidate", "instructor", "notes"),
            ("التاريخ", "الوقت", "مدة(د)", "النوع", "المترشح", "الممرّن", "ملاحظات"),
            (100, 70, 60, 100, 180, 160, 160), height=18)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-Button-1>", lambda e: self._edit())

    # ──────────────────────────────────────────────────────────
    def _reset_filter(self):
        self._date_var.set("")
        self._inst_filter_var.set("الكل")
        self._inst_combo.current(0)
        self._cand_filter_var.set("الكل")
        self._cand_combo.current(0)
        self._load()

    def _load(self):
        self.selected_id = None
        date_f = self._date_var.get().strip()

        # فلتر الممرّن
        inst_filter_name = self._inst_filter_var.get()
        inst_id = None
        if inst_filter_name and inst_filter_name != "الكل":
            for i in InstructorDB.get_all():
                if f"{i['last_name']} {i['first_name']}" == inst_filter_name:
                    inst_id = i['id']
                    break

        # فلتر المترشح
        cand_filter_name = self._cand_filter_var.get()
        cand_id = None
        if cand_filter_name and cand_filter_name != "الكل":
            for c in CandidateDB.get_all():
                if f"{c['last_name']} {c['first_name']}" == cand_filter_name:
                    cand_id = c['id']
                    break

        sessions = SessionDB.get_all(date_filter=date_f,
                                      instructor_id=inst_id,
                                      candidate_id=cand_id)

        rows = [(s['session_date'], s['session_time'], str(s['duration']),
                 s['session_type'], s['candidate_name'],
                 s['instructor_name'], s.get('notes', ''))
                for s in sessions]
        insert_zebra(self.tree, rows)

        # تلوين حصص اليوم
        today_str = date.today().strftime('%Y-%m-%d')
        for item in self.tree.get_children():
            vals = self.tree.item(item, 'values')
            if vals and vals[0] == today_str:
                self.tree.item(item, tags=("today",))
        self.tree.tag_configure("today", background="#dcfce7",
                                foreground="#166534")

        # ربط session_id بكل صف
        self._id_map = {}
        for item, s in zip(self.tree.get_children(), sessions):
            self._id_map[item] = s['id']

        # ملخص الأسبوع
        week = SessionDB.get_week()
        self._week_lbl.configure(
            text=f"حصص الأسبوع القادم: {len(week)}  |  حصص اليوم: {len(SessionDB.get_today())}"
        )

    def _on_select(self, event=None):
        sel = self.tree.selection()
        self.selected_id = self._id_map.get(sel[0]) if sel else None

    # ──────────────────────────────────────────────────────────
    def _add(self):
        SessionDialog(self, on_save=self._load)

    def _edit(self):
        if not self.selected_id:
            show_error("يرجى تحديد حصة من الجدول أولاً"); return
        SessionDialog(self, session_id=self.selected_id, on_save=self._load)

    def _delete(self):
        if not self.selected_id:
            show_error("يرجى تحديد حصة من الجدول أولاً"); return
        s = SessionDB.get(self.selected_id)
        if not s:
            return
        msg = (f"هل تريد حذف الحصة:\n"
               f"التاريخ: {s['session_date']}  الوقت: {s['session_time']}\n"
               f"هل أنت متأكد؟")
        if messagebox.askyesno("تأكيد الحذف", msg):
            SessionDB.delete(self.selected_id)
            self.selected_id = None
            self._load()
            show_info("تم حذف الحصة بنجاح")


# ============================================================================
#  واجهة: طباعة الوثائق
# ============================================================================

class DocumentsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.selected_candidate_id = None
        self._build(); self._load_candidates()

    def _build(self):
        wrap = tk.Frame(self, bg=COLOR_BG, padx=20, pady=15)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="🖨️  طباعة الوثائق بالعربية",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=COLOR_BG, fg=COLOR_HEADER, anchor="e").pack(fill="x", pady=(0, 5))
        tk.Label(wrap, text="إنتاج كل الوثائق الرسمية بصيغة PDF بنص عربي مُنسّق",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT,
                 anchor="e").pack(fill="x", pady=(0, 15))

        # رسائل تحذيرية
        if not HAS_REPORTLAB:
            warn = tk.Frame(wrap, bg="#fef3c7", padx=15, pady=10)
            warn.pack(fill="x", pady=(0, 10))
            tk.Label(warn, text="⚠️  مكتبة reportlab غير مثبتة. شغّل: pip install reportlab",
                     font=FONT_BOLD, bg="#fef3c7", fg="#92400e",
                     anchor="e").pack(anchor="e")
        elif not HAS_ARABIC_LIBS:
            warn = tk.Frame(wrap, bg="#fef3c7", padx=15, pady=10)
            warn.pack(fill="x", pady=(0, 10))
            tk.Label(warn, text="⚠️  مكتبتا arabic_reshaper و python-bidi غير مثبتتين.\nقد تظهر الحروف العربية متفرقة. شغّل:\n   pip install arabic_reshaper python-bidi",
                     font=FONT_BOLD, bg="#fef3c7", fg="#92400e",
                     justify="right", anchor="e").pack(anchor="e")
        else:
            ok = tk.Frame(wrap, bg="#d1fae5", padx=15, pady=10)
            ok.pack(fill="x", pady=(0, 10))
            tk.Label(ok, text=f"✓  دعم العربية مفعّل (الخط: {os.path.basename(ARABIC_FONT) if ARABIC_FONT != 'Helvetica' else 'النظامي'})",
                     font=FONT_BOLD, bg="#d1fae5", fg="#065f46",
                     anchor="e").pack(anchor="e")

        bottom = tk.Frame(wrap, bg=COLOR_BG); bottom.pack(fill="both", expand=True)

        # ===== يمين: قائمة الوثائق (قابلة للتمرير) =====
        right_outer = tk.Frame(bottom, bg=COLOR_BG, width=300)
        right_outer.pack(side="right", fill="y", padx=(8, 0))
        right_outer.pack_propagate(False)

        # إطار الكارد الخارجي
        right_card_outer = tk.Frame(right_outer, bg=COLOR_BORDER, padx=1, pady=1)
        right_card_outer.pack(fill="both", expand=True)

        # Canvas قابل للتمرير داخل الكارد
        docs_canvas = tk.Canvas(right_card_outer, bg=COLOR_CARD, highlightthickness=0)
        docs_vsb = ttk.Scrollbar(right_card_outer, orient="vertical",
                                  command=docs_canvas.yview)
        docs_inner = tk.Frame(docs_canvas, bg=COLOR_CARD, padx=10, pady=10)

        docs_inner.bind("<Configure>",
                        lambda e: docs_canvas.configure(
                            scrollregion=docs_canvas.bbox("all")))
        win_id = docs_canvas.create_window((0, 0), window=docs_inner, anchor="nw")
        docs_canvas.configure(yscrollcommand=docs_vsb.set)

        # تمرير بعجلة الماوس
        def _on_mousewheel(event):
            docs_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        docs_canvas.bind("<MouseWheel>", _on_mousewheel)
        docs_inner.bind("<MouseWheel>", _on_mousewheel)

        # ضبط عرض الـ inner عند تغيير حجم الـ canvas
        def _resize_inner(event):
            docs_canvas.itemconfig(win_id, width=event.width)
        docs_canvas.bind("<Configure>", _resize_inner)

        docs_vsb.pack(side="right", fill="y")
        docs_canvas.pack(side="left", fill="both", expand=True)

        rc = docs_inner  # الآن rc هو الإطار الداخلي القابل للتمرير

        section_title(rc, "وثائق فردية (للمترشح المحدد)", icon="📄")
        docs_individual = [
            ("جدول إرسال", "📋", self._doc_dispatch_table),
            ("استمارة اجتياز الامتحان", "📄", self._doc_exam_form),
            ("بطاقة التكوين", "📋", self._doc_training_card),
            ("عقد التكوين", "📜", self._doc_contract),
            ("شهادة إدارية", "🏛️", self._doc_certificate),
            ("وصل دفع", "🧾", self._doc_payment_receipt),
        ]
        for label, icon, cmd in docs_individual:
            ModernButton(rc, label, cmd, icon=icon, color=COLOR_PRIMARY).pack(fill="x", pady=2)

        tk.Frame(rc, bg=COLOR_BORDER, height=2).pack(fill="x", pady=8)

        section_title(rc, "وثائق جماعية", icon="📊")
        docs_group = [
            ("قائمة كل المترشحين", "📑", self._doc_candidates_list),
            ("قائمة الممرنين", "👥", self._doc_instructors_list),
            ("تقرير المصاريف", "💸", self._doc_expenses_report),
            ("تقرير المدفوعات", "💰", self._doc_payments_report),
        ]
        for label, icon, cmd in docs_group:
            ModernButton(rc, label, cmd, icon=icon, color=COLOR_PURPLE).pack(fill="x", pady=3)

        tk.Frame(rc, bg=COLOR_BORDER, height=2).pack(fill="x", pady=8)

        section_title(rc, "وثائق الامتحانات", icon="📝")
        ModernButton(rc, "قائمة المترشحين للامتحان", self._doc_exam_candidates_list,
                     icon="📋", color="#0369a1").pack(fill="x", pady=3)

        tip = tk.Frame(rc, bg=COLOR_PRIMARY_LIGHT, padx=10, pady=8)
        tip.pack(fill="x", pady=(12, 0))
        tk.Label(tip, text="💡 اختر مترشحاً ثم اضغط\nعلى نوع الوثيقة → PDF",
                 font=FONT_SMALL, bg=COLOR_PRIMARY_LIGHT,
                 fg=COLOR_PRIMARY_DARK, justify="right",
                 anchor="e").pack(anchor="e")

        # يسار: قائمة المترشحين
        left = tk.Frame(bottom, bg=COLOR_BG); left.pack(side="left", fill="both", expand=True)

        sb_o, sb = make_card(left, padding=10); sb_o.pack(fill="x", pady=(0, 10))
        tk.Label(sb, text="🔍", font=(FONT_FAMILY, 14),
                 bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(side="right", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_candidates())
        make_entry(sb, self.search_var, width=30).pack(side="right", fill="x",
                                                       expand=True, ipady=5)
        tk.Label(sb, text="ابحث عن مترشح:", font=FONT_BOLD,
                 bg=COLOR_CARD, fg=COLOR_TEXT, anchor="e").pack(side="right", padx=10)

        lo, lc = make_card(left, padding=10); lo.pack(fill="both", expand=True)
        section_title(lc, "اختر المترشح المطلوب", icon="👤")
        self.tree = create_treeview(lc,
            ("id","last_name","first_name","gender","license_type","registration_date"),
            ("رقم","اللقب","الاسم","الجنس","نوع الرخصة","تاريخ التسجيل"),
            (50,140,140,80,110,140), height=18)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load_candidates(self):
        rows = CandidateDB.get_all(self.search_var.get())
        values = [(r['id'], r['last_name'], r['first_name'], r['gender'],
                   r['license_type'], r['registration_date']) for r in rows]
        insert_zebra(self.tree, values)

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_candidate_id = self.tree.item(sel[0])['values'][0]

    def _check(self):
        if not HAS_REPORTLAB:
            show_error("مكتبة reportlab غير مثبتة.\nشغّل: pip install reportlab")
            return False
        return True

    def _get_candidate(self):
        if not self.selected_candidate_id:
            show_error("يرجى تحديد مترشح من القائمة أولاً"); return None
        return CandidateDB.get(self.selected_candidate_id)

    def _ask_save(self, default_name):
        return filedialog.asksaveasfilename(defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf"),("All Files","*.*")],
            initialfile=default_name)

    def _make_doc(self, path, **kwargs):
        defaults = dict(pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)
        defaults.update(kwargs)
        return SimpleDocTemplate(path, **defaults)

    def _trigger_print(self, path, title="الوثيقة"):
        """يعرض نافذة اختيار الطابعة ثم يرسل الملف للطباعة."""
        printers = self._get_printers()

        dlg = tk.Toplevel()
        dlg.title("اختيار الطابعة")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg=COLOR_BG)

        w, h = 440, 210
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() - w) // 2
        y = (dlg.winfo_screenheight() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(dlg, text=f"🖨️  طباعة: {title}",
                 font=FONT_BOLD, bg=COLOR_BG, fg=COLOR_HEADER,
                 anchor="e").pack(fill="x", padx=20, pady=(18, 4))

        tk.Label(dlg, text="اختر الطابعة:",
                 font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT,
                 anchor="e").pack(fill="x", padx=20)

        printer_var = tk.StringVar()
        if printers:
            printer_var.set(printers[0])

        cb = ttk.Combobox(dlg, textvariable=printer_var, values=printers,
                          font=FONT_MAIN, state="readonly",
                          style="Modern.TCombobox")
        cb.pack(fill="x", padx=20, pady=8)

        btn_frame = tk.Frame(dlg, bg=COLOR_BG)
        btn_frame.pack(fill="x", padx=20, pady=10)

        result = {"action": None}

        def do_print():
            result["action"] = "print"
            dlg.destroy()

        def do_open():
            result["action"] = "open"
            dlg.destroy()

        def do_cancel():
            result["action"] = "cancel"
            dlg.destroy()

        tk.Button(btn_frame, text="طباعة", font=FONT_BOLD,
                  bg=COLOR_PRIMARY, fg="white", relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=do_print).pack(side="right", padx=(6, 0))
        tk.Button(btn_frame, text="فتح الملف فقط", font=FONT_MAIN,
                  bg=COLOR_INFO, fg="white", relief="flat",
                  padx=12, pady=6, cursor="hand2",
                  command=do_open).pack(side="right", padx=6)
        tk.Button(btn_frame, text="إلغاء", font=FONT_MAIN,
                  bg=COLOR_BORDER, fg=COLOR_TEXT, relief="flat",
                  padx=12, pady=6, cursor="hand2",
                  command=do_cancel).pack(side="left")

        dlg.wait_window()

        if result["action"] == "print":
            selected = printer_var.get()
            self._send_to_printer(path, selected, title)
        elif result["action"] == "open":
            try:
                os.startfile(path)
            except Exception:
                try:
                    import subprocess, sys
                    if sys.platform == "darwin":
                        subprocess.run(["open", path])
                    else:
                        subprocess.run(["xdg-open", path])
                except Exception as e:
                    show_error(f"خطأ في فتح الملف: {e}")

    def _get_printers(self):
        """يجلب قائمة الطابعات المثبتة على النظام."""
        printers = []
        try:
            import sys
            if sys.platform == "win32":
                try:
                    import winreg
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SYSTEM\CurrentControlSet\Control\Print\Printers")
                    i = 0
                    while True:
                        try:
                            printers.append(winreg.EnumKey(key, i))
                            i += 1
                        except OSError:
                            break
                except Exception:
                    import subprocess
                    result = subprocess.run(
                        ["wmic", "printer", "get", "name"],
                        capture_output=True, text=True)
                    for line in result.stdout.splitlines():
                        line = line.strip()
                        if line and line.lower() != "name":
                            printers.append(line)
            else:
                import subprocess
                result = subprocess.run(
                    ["lpstat", "-a"], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    parts = line.split()
                    if parts:
                        printers.append(parts[0])
        except Exception:
            pass
        if not printers:
            printers = ["الطابعة الافتراضية"]
        return printers

    def _send_to_printer(self, path, printer_name, title):
        """يرسل ملف PDF إلى الطابعة المحددة."""
        import sys, subprocess
        try:
            if sys.platform == "win32":
                if printer_name and printer_name != "الطابعة الافتراضية":
                    try:
                        subprocess.run(
                            ["SumatraPDF", "-print-to", printer_name, path],
                            capture_output=True)
                        show_info(f"تم إرسال {title} للطابعة:\n{printer_name}")
                        return
                    except Exception:
                        pass
                os.startfile(path, 'print')
                show_info(f"تم إرسال {title} للطباعة.")
            else:
                cmd = ["lp", path]
                if printer_name and printer_name != "الطابعة الافتراضية":
                    cmd = ["lp", "-d", printer_name, path]
                subprocess.run(cmd)
                show_info(f"تم إرسال {title} للطابعة:\n{printer_name}")
        except Exception as e:
            show_error(f"خطأ في الطباعة:\n{e}\n\nسيتم فتح الملف بدلاً من ذلك.")
            try:
                os.startfile(path)
            except Exception:
                pass

    # --- وثائق فردية ----------------------------------------------------------


            
    def _doc_exam_form(self):
        if not self._check(): return
        cand = self._get_candidate()
        if not cand: return
        
        import tempfile, os
        from datetime import datetime
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        
        temp_dir = tempfile.gettempdir()
        path = os.path.join(temp_dir, f"exam_form_{cand['id']}_{int(datetime.now().timestamp())}.pdf")
        
        school = SchoolInfoDB.get()
        c = canvas.Canvas(path, pagesize=A4)
        
        def draw_text(x_cm, y_cm, text, font=ARABIC_FONT, size=11, align="right"):
            c.setFont(font, size)
            text_ar = ar(str(text))
            if align == "right":
                c.drawRightString(x_cm * cm, y_cm * cm, text_ar)
            elif align == "center":
                c.drawCentredString(x_cm * cm, y_cm * cm, text_ar)
            else:
                c.drawString(x_cm * cm, y_cm * cm, text_ar)
                
        def draw_line(x1, y1, x2, y2):
            c.line(x1 * cm, y1 * cm, x2 * cm, y2 * cm)
            
        def draw_dotted_line(x1, y1, x2, y2):
            c.saveState()
            c.setDash(1, 2)
            c.line(x1 * cm, y1 * cm, x2 * cm, y2 * cm)
            c.restoreState()
            
        def draw_rect(x, y, w, h):
            c.rect(x * cm, y * cm, w * cm, h * cm)

        # 1. الترويسة
        draw_text(10.5, 28.5, "الجمهورية الجزائرية الديمقراطية الشعبية", ARABIC_FONT_BOLD, 14, "center")
        draw_text(10.5, 27.8, "وزارة الداخلية والجماعات المحلية والتهيئة العمرانية", ARABIC_FONT_BOLD, 12, "center")
        draw_text(10.5, 27.1, "المندوبية الوطنية للأمن في الطرق", ARABIC_FONT_BOLD, 12, "center")
        
        wilaya = school.get('address', '').split(' ')[-1] if school.get('address') else '........'
        draw_text(19.5, 26.3, f"المندوبية الولائية للأمن في الطرق لولاية : {wilaya}", ARABIC_FONT_BOLD, 12, "right")
        
        # 2. المربعات العلوية (صورة، عنوان، ختم)
        c.setLineWidth(1.2)
        draw_rect(1.5, 24.0, 3.5, 4.5) # مربع الصورة
        draw_text(3.25, 26.2, "الصورة", ARABIC_FONT, 14, "center")
        
        # العنوان في الوسط
        c.setFont(ARABIC_FONT_BOLD, 20)
        c.drawCentredString(10.5 * cm, 25.5 * cm, ar("إستمارة الترشح لاجتياز امتحانات رخصة السياقة"))
        
        # الصنف المطلوب (تحت العنوان)
        draw_text(11.0, 24.5, "الصنف المطلوب :", ARABIC_FONT_BOLD, 14, "right")
        draw_rect(7.0, 24.2, 1.2, 0.8)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(7.6 * cm, 24.4 * cm, cand.get('license_type','B'))
        
        # مربع ختم المدرسة (يمين)
        c.setLineWidth(1.5)
        draw_rect(12.5, 20.8, 7.5, 3.2)
        draw_text(16.25, 23.2, "ختم مدرسة تعليم السياقة", ARABIC_FONT_BOLD, 11, "center")
        draw_text(16.25, 21.2, "في حالة مترشح حر يوضع ختم المندوبية الولائية للأمن في الطرق", ARABIC_FONT, 8, "center")
        
        # مربعات التاريخ ورقم الملف (يسار الختم)
        c.setLineWidth(1.0)
        draw_rect(5.0, 22.4, 4.5, 1.0)
        draw_text(12.0, 22.8, "تاريخ إيداع الملف", ARABIC_FONT, 11, "right")
        
        draw_rect(5.0, 21.0, 4.5, 1.0)
        draw_text(12.0, 21.4, "رقم الملف", ARABIC_FONT, 11, "right")
        
        # خط فاصل سميك
        c.setLineWidth(2.5)
        draw_line(1.5, 20.2, 20.0, 20.2)
        c.setLineWidth(1)
        
        # 3. معلومات المترشح
        draw_text(10.5, 19.4, "معلومات خاصة بالمترشح", ARABIC_FONT_BOLD, 14, "center")
        draw_line(8.0, 19.3, 13.0, 19.3)
        
        # رقم التعريف والفصيلة
        draw_text(20.0, 18.3, "رقم التعريف الوطني :", ARABIC_FONT_BOLD, 11, "right")
        c.setLineWidth(1.2)
        draw_rect(8.0, 18.0, 8.5, 0.8)
        draw_text(12.25, 18.2, cand.get('national_id','') or "", "Helvetica-Bold", 12, "center")
        
        draw_text(6.5, 18.3, "فصيلة الدم :", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(2.5, 18.0, 1.5, 0.8)
        draw_text(3.25, 18.2, cand.get('blood_type','') or "*", "Helvetica-Bold", 12, "center")
        
        # اللقب والاسم
        draw_text(20.0, 17.2, "اللقب :", ARABIC_FONT_BOLD, 11, "right")
        draw_text(16.5, 17.2, cand.get('last_name',''), ARABIC_FONT_BOLD, 11, "right")
        draw_dotted_line(13.0, 17.2, 17.5, 17.2)
        draw_text(1.5, 17.2, f"Nom:  {cand.get('last_name','')}", ARABIC_FONT, 10, "left")
        
        draw_text(20.0, 16.2, "الاسم :", ARABIC_FONT_BOLD, 11, "right")
        draw_text(16.5, 16.2, cand.get('first_name',''), ARABIC_FONT_BOLD, 11, "right")
        draw_dotted_line(13.0, 16.2, 17.5, 16.2)
        draw_text(1.5, 16.2, f"Prénom:  {cand.get('first_name','')}", ARABIC_FONT, 10, "left")
        
        # الجنس
        draw_text(20.0, 15.2, "الجنس :", ARABIC_FONT_BOLD, 11, "right")
        draw_text(18.0, 15.2, "ذكر", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(16.8, 15.2, 0.4, 0.4)
        if cand.get("gender") == "ذكر": draw_text(17.0, 15.35, "X", "Helvetica-Bold", 12, "center")
        draw_text(15.5, 15.2, "أنثى", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(14.3, 15.2, 0.4, 0.4)
        if cand.get("gender") == "أنثى": draw_text(14.5, 15.35, "X", "Helvetica-Bold", 12, "center")
        
        # تاريخ ومكان الميلاد
        draw_text(20.0, 14.2, "تاريخ و مكان الميلاد :", ARABIC_FONT_BOLD, 10, "right")
        draw_text(16.0, 14.2, cand.get('birth_date',''), "Helvetica-Bold", 10, "right")
        draw_text(13.5, 14.2, "بلدية :", ARABIC_FONT_BOLD, 10, "right")
        draw_text(11.0, 14.2, cand.get('birth_place_commune',''), ARABIC_FONT_BOLD, 10, "right")
        draw_text(7.5, 14.2, "ولاية :", ARABIC_FONT_BOLD, 10, "right")
        draw_text(5.0, 14.2, cand.get('birth_place_wilaya',''), ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(1.5, 14.2, 17.5, 14.2)
        
        # الوالدين
        draw_text(20.0, 13.2, "اسم الأب :", ARABIC_FONT_BOLD, 10, "right")
        draw_text(18.0, 13.2, cand.get('father_name',''), ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(12.5, 13.2, 18.0, 13.2)
        draw_text(12.0, 13.2, "اسم و لقب الأم :", ARABIC_FONT_BOLD, 10, "right")
        draw_text(9.0, 13.2, cand.get('mother_name',''), ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(1.5, 13.2, 9.0, 13.2)
        
        # العنوان
        draw_text(20.0, 12.2, "العنوان :", ARABIC_FONT_BOLD, 10, "right")
        draw_text(18.5, 12.2, cand.get('current_address',''), ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(13.0, 12.2, 18.5, 12.2)
        draw_text(12.5, 12.2, "بلدية :", ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(8.0, 12.2, 11.2, 12.2)
        draw_text(7.5, 12.2, "ولاية :", ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(1.5, 12.2, 6.0, 12.2)
        
        # الحالة العائلية
        draw_text(20.0, 11.2, "الحالة العائلية :", ARABIC_FONT_BOLD, 11, "right")
        ms = cand.get('marital_status', '')
        draw_text(17.0, 11.2, "أعزب / عزباء", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(14.3, 11.2, 0.4, 0.4)
        if ms == "أعزب": draw_text(14.5, 11.35, "X", "Helvetica-Bold", 12, "center")
        draw_text(13.5, 11.2, "متزوج (ة)", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(11.3, 11.2, 0.4, 0.4)
        if ms == "متزوج": draw_text(11.5, 11.35, "X", "Helvetica-Bold", 12, "center")
        draw_text(10.5, 11.2, "مطلق (ة)", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(8.3, 11.2, 0.4, 0.4)
        if ms == "مطلق": draw_text(8.5, 11.35, "X", "Helvetica-Bold", 12, "center")
        draw_text(7.5, 11.2, "أرمل (ة)", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(5.3, 11.2, 0.4, 0.4)
        if ms == "أرمل": draw_text(5.5, 11.35, "X", "Helvetica-Bold", 12, "center")
        
        # رقم الهاتف
        draw_text(11.5, 10.2, "رقم الهاتف :", ARABIC_FONT_BOLD, 11, "right")
        draw_rect(5.0, 10.0, 5.0, 0.7)
        draw_text(7.5, 10.15, cand.get('phone','') or "", "Helvetica-Bold", 12, "center")
        
        # الجنسية
        draw_text(20.0, 9.2, "الجنسية الأصلية :", ARABIC_FONT_BOLD, 11, "right")
        draw_text(17.5, 9.2, cand.get('nationality',''), ARABIC_FONT_BOLD, 11, "right")
        draw_dotted_line(11.5, 9.2, 17.5, 9.2)
        draw_text(11.0, 9.2, "الجنسية المكتسبة :", ARABIC_FONT_BOLD, 11, "right")
        draw_text(8.0, 9.2, cand.get('second_nationality',''), ARABIC_FONT_BOLD, 11, "right")
        draw_dotted_line(1.5, 9.2, 8.0, 9.2)
        
        # المولودين بالخارج
        draw_text(20.0, 8.2, "بالنسبة للأشخاص المولودين بالخارج / بلد الميلاد :", ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(10.0, 8.2, 13.0, 8.2)
        draw_text(9.5, 8.2, "سفارة أو قنصلية التسجيل :", ARABIC_FONT_BOLD, 10, "right")
        draw_dotted_line(1.5, 8.2, 5.5, 8.2)
        
        # 4. جدول الأصناف (مطور ومطابق للصورة)
        draw_text(10.5, 7.3, "الأصناف المتحصل عليها من قبل", ARABIC_FONT_BOLD, 12, "center")
        draw_line(8.0, 7.2, 13.0, 7.2)
        
        y_tab = 6.8; rh = 0.45; rows = 11
        y_bot = y_tab - (rh * (rows + 2))
        c.setLineWidth(1.2)
        draw_rect(1.5, y_bot, 18.5, y_tab - y_bot)
        
        # أعمدة رئيسية
        draw_line(7.0, y_bot, 7.0, y_tab)   # هيئة الإصدار
        draw_line(11.0, y_bot, 11.0, y_tab)  # التاريخ
        draw_line(14.5, y_bot, 14.5, y_tab)  # الرقم
        draw_line(16.0, y_bot, 16.0, y_tab)  # الصنف
        
        # تقسيم عمود الصنف إلى جديد وقديم
        draw_line(16.0, y_tab - rh, 20.0, y_tab - rh) # خط تحت "الصنف"
        draw_line(18.0, y_bot, 18.0, y_tab - rh)      # فاصل بين الجديد والقديم
        
        # تقسيم فرعي للرموز والأسماء
        draw_line(17.0, y_bot, 17.0, y_tab - 2*rh)    # فاصل في الجديد
        draw_line(19.0, y_bot, 19.0, y_tab - 2*rh)    # فاصل في القديم
        
        # خطوط أفقية
        draw_line(16.0, y_tab - 2*rh, 20.0, y_tab - 2*rh) # خط تحت "الجديد/القديم"
        c.setLineWidth(0.8)
        for i in range(1, rows + 1):
            y = y_tab - 2*rh - i*rh
            draw_line(1.5, y, 18.0, y) # الخطوط الأفقية حتى بداية "القديم" المدمج
            if i <= 6 or i == 11: # الخطوط في عمود "القديم" (باستثناء المدمج E)
                draw_line(18.0, y, 20.0, y)
        
        # عناوين الجدول
        yh1 = y_tab - rh/2 - 0.12
        yh2 = y_tab - 1.5*rh - 0.12
        draw_text(18.0, yh1, "الصنف", ARABIC_FONT_BOLD, 10, "center")
        draw_text(17.0, yh2, "الجديد", ARABIC_FONT_BOLD, 9, "center")
        draw_text(19.0, yh2, "القديم", ARABIC_FONT_BOLD, 9, "center")
        draw_text(15.25, y_tab - rh - 0.12, "الرقم", ARABIC_FONT_BOLD, 10, "center")
        draw_text(12.75, y_tab - rh - 0.12, "التاريخ", ARABIC_FONT_BOLD, 10, "center")
        draw_text(4.25, y_tab - rh - 0.12, "هيئة الإصدار", ARABIC_FONT_BOLD, 10, "center")
        
        # البيانات
        cats_new = [("A1","أ1"),("A","أ2"),("B","ب"),("D","د"),("C1","ج1"),("C","ج"),
                    ("BE","ب(هـ)"),("C1E","ج1(هـ)"),("CE","ج(هـ)"),("DE","د(هـ)"),("F","و")]
        cats_old = [("A1","أ1"),("A2","أ2"),("B","ب"),("D","د"),("C1","ج1"),("C2","ج2")]
        
        for i, (cn, co) in enumerate(cats_new):
            yt = y_tab - 2*rh - (i+1)*rh + 0.12
            draw_text(16.5, yt, cn, "Helvetica", 9, "center")
            draw_text(17.5, yt, co, ARABIC_FONT, 9, "center")
            if i < 6: # القديم المنفصل
                draw_text(18.5, yt, cats_old[i][0], "Helvetica", 9, "center")
                draw_text(19.5, yt, cats_old[i][1], ARABIC_FONT, 9, "center")
        
        # القديم المدمج (E / هـ) لـ BE حتى DE
        yt_merged = y_tab - 2*rh - 8.5*rh + 0.12
        draw_text(18.5, yt_merged, "E", "Helvetica-Bold", 11, "center")
        draw_text(19.5, yt_merged, "هـ", ARABIC_FONT_BOLD, 11, "center")
        
        # الصنف الأخير F
        yt_f = y_tab - 2*rh - 11*rh + 0.12
        draw_text(18.5, yt_f, "F", "Helvetica", 9, "center")
        draw_text(19.5, yt_f, "و", ARABIC_FONT, 9, "center")

        c.save()
        try:
            # محاولة الطباعة المباشرة
            os.startfile(path, 'print')
        except Exception:
            # في حال فشل الطباعة المباشرة، نكتفي بفتح الملف
            try: os.startfile(path)
            except Exception as e: show_error(f"خطأ: {e}")

    def _doc_training_card(self):
        if not self._check(): return
        cand = self._get_candidate()
        if not cand: return
        
        import tempfile, os
        from datetime import datetime
        temp_dir = tempfile.gettempdir()
        path = os.path.join(temp_dir, f"training_card_{cand['id']}_{int(datetime.now().timestamp())}.pdf")
        
        school = SchoolInfoDB.get()
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(path, pagesize=A4)
        
        def draw_text(x_cm, y_cm, text, font=ARABIC_FONT, size=11, align="right", bold=False):
            f = ARABIC_FONT_BOLD if bold else font
            c.setFont(f, size)
            text_ar = ar(str(text))
            if align == "right":
                c.drawRightString(x_cm * cm, y_cm * cm, text_ar)
            elif align == "center":
                c.drawCentredString(x_cm * cm, y_cm * cm, text_ar)
            else:
                c.drawString(x_cm * cm, y_cm * cm, text_ar)

        def draw_rect(x, y, w, h, lw=1):
            c.setLineWidth(lw)
            c.rect(x * cm, y * cm, w * cm, h * cm)

        def draw_line(x1, y1, x2, y2, lw=1):
            c.setLineWidth(lw)
            c.line(x1 * cm, y1 * cm, x2 * cm, y2 * cm)

        # 1. الترويسة
        draw_text(10.5, 28.7, "الجمهورية الجزائرية الديمقراطية الشعبية", ARABIC_FONT_BOLD, 12, "center")
        
        # جهة اليمين
        y_head = 27.8
        draw_text(20.0, y_head, "ولاية معسكر", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_head-0.6, "المركز الوطني لرخصة السياقة", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_head-1.2, "الفرع المحلي لولاية معسكر", ARABIC_FONT_BOLD, 11)
        
        # مربع الصورة/الختم يسار
        draw_rect(1.5, 25.5, 2.5, 3.5)
        
        # العنوان الرئيسي
        c.setLineWidth(1.5)
        c.rect(6.5*cm, 24.5*cm, 8.5*cm, 1.2*cm)
        draw_text(10.75, 25.1, "بطاقة التكوين (التقييم) المترشحين لرخصة السياقة", ARABIC_FONT_BOLD, 14, "center")
        draw_text(10.75, 24.0, "(مادة قانون المرور)", ARABIC_FONT_BOLD, 12, "center")
        
        # حقول عامة
        y_f = 22.5
        draw_text(20.0, y_f, f"مدرسة تعليم السياقة: {school.get('name','.................................')}", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_f-1.0, f"رقم التسجيل: {cand['id']} ..................... التاريخ: {date.today().strftime('%Y/%m/%d')}", ARABIC_FONT_BOLD, 11)
        
        # جدول الأصناف المستهدفة
        y_tab = 20.0
        cols = ["أ1","أ2","ب","ب(هـ)","ج1","ج1(هـ)","ج2","ج2(هـ)","د","د(هـ)","ج","و"]
        w_cell = 1.3
        h_cell = 0.8
        
        # تسمية العمود
        draw_rect(17.3, y_tab, 2.7, h_cell)
        draw_text(18.65, y_tab+0.25, "الصنف المستهدف", ARABIC_FONT_BOLD, 10, "center")
        
        for i, cat in enumerate(cols):
            x = 17.3 - (i+1)*w_cell
            draw_rect(x, y_tab, w_cell, h_cell)
            draw_text(x + w_cell/2, y_tab+0.25, cat, ARABIC_FONT_BOLD, 10, "center")
            
            # تحديد الصنف المطلوب (بناءً على license_type)
            mapping = ["A1","A2","B","BE","C1","C1E","C2","C2E","D","DE","CE","F"]
            if cand.get('license_type') == mapping[i]:
                draw_line(x, y_tab, x+w_cell, y_tab+h_cell, lw=1.5)
                draw_line(x, y_tab+h_cell, x+w_cell, y_tab, lw=1.5)

        # معلومات المترشح
        y_info = 18.0
        draw_text(20.0, y_info, f"الإسم و اللقب : {cand['last_name']} {cand['first_name']}", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_info-0.8, f"تاريخ الميلاد : {cand['birth_date']}", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_info-1.6, f"العنوان : {cand.get('current_address','')}", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_info-2.4, f"تاريخ التسجيل بمدرسة سياقة السيارة : {cand['registration_date']}", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_info-3.2, "تاريخ إيداع الملف بالمديرية : .........................", ARABIC_FONT_BOLD, 11)
        draw_text(20.0, y_info-4.0, "رقم التسجيل : .........................", ARABIC_FONT_BOLD, 11)
        
        # الجدول الرئيسي للحصص (01-13 و 14-25)
        y_grid = 12.5
        def draw_grid_block(x_start, num_start, num_end):
            cw = [0.8, 2.5, 2.0, 2.5] # الرقم، التاريخ، الساعات، الإمضاء
            tw = sum(cw)
            th = 0.55
            # Header
            curr_y = y_grid
            headers = ["الرقم", "تاريخ الدروس", "ساعات الدروس", "إمضاء المترشح"]
            cx = x_start
            for j, h in enumerate(headers):
                draw_rect(cx, curr_y, cw[j], th)
                draw_text(cx + cw[j]/2, curr_y+0.15, h, ARABIC_FONT_BOLD, 8, "center")
                cx += cw[j]
            
            # Rows
            for r in range(num_start, num_end + 1):
                curr_y -= th
                cx = x_start
                for j in range(4):
                    draw_rect(cx, curr_y, cw[j], th)
                    if j == 0:
                        draw_text(cx + cw[j]/2, curr_y+0.15, str(r), "Helvetica", 9, "center")
                    cx += cw[j]

        # بلوك اليمين (01-13)
        draw_grid_block(11.5, 1, 13)
        # بلوك اليسار (14-25)
        draw_grid_block(2.0, 14, 25)
        
        # التذييل
        draw_text(20.0, 3.5, "ختم وتوقيع مدرسة تعليم السياقة", ARABIC_FONT_BOLD, 11)
        draw_text(5.0, 3.5, "إمضاء المترشح", ARABIC_FONT_BOLD, 11)
        
        c.save()
        try:
            # محاولة الطباعة المباشرة
            os.startfile(path, 'print')
        except Exception:
            # في حال فشل الطباعة المباشرة، نكتفي بفتح الملف
            try: os.startfile(path)
            except Exception as e: show_error(f"خطأ: {e}")
        self._trigger_print(path, "بطاقة التكوين")

    def _doc_contract(self):
        if not self._check(): return
        cand = self._get_candidate()
        if not cand: return
        path = self._ask_save(f"عقد_تكوين_{cand['last_name']}.pdf")
        if not path: return
        school = SchoolInfoDB.get()
        doc = self._make_doc(path); s = _pdf_styles(); story = []
        _pdf_header(story, school, "عقد تكوين بين مدرسة تعليم السياقة والمترشح")
        
        txt = f"""
        بموجب هذا العقد، تلتزم مدرسة تعليم السياقة: <b>{school.get('name','....................')}</b>
        والكائن مقرها بـ: <b>{school.get('address','....................')}</b>
        
        بتكوين المترشح(ة): <b>{cand.get('last_name','')} {cand.get('first_name','')}</b>
        المولود(ة) بتاريخ: <b>{cand.get('birth_date','')}</b> بـ: <b>{cand.get('birth_place_commune','')}</b>
        للحصول على رخصة السياقة من الصنف: <b>{cand.get('license_type','B')}</b>
        
        <b>البند 1: التزامات المدرسة</b>
        تلتزم المدرسة بتقديم تكوين نظري (30 ساعة) وتكوين تطبيقي (30 ساعة) وفقاً للبرنامج الوطني المعمول به.
        
        <b>البند 2: التزامات المترشح</b>
        يلتزم المترشح بدفع مبلغ إجمالي قدره: <b>{cand.get('total_amount',0):,.0f} دج</b>، وباحترام مواعيد الدروس وقوانين المدرسة.
        
        <b>البند 3: مدة العقد</b>
        هذا العقد صالح لمدة ستة (06) أشهر من تاريخ التوقيع، قابلة للتجديد باتفاق الطرفين.
        
        حرر بـ: ............................ بتاريخ: <b>{date.today().strftime('%Y-%m-%d')}</b>
        """
        for line in txt.split('\n'):
            if line.strip():
                story.append(Paragraph(ar(line.strip()), s["right"]))
                story.append(Spacer(1, 0.2*cm))
        
        story.append(Spacer(1, 2*cm))
        # التوقيعات
        t_data = [[ar("توقيع المترشح (أو وليه)"), ar("ختم وتوقيع المدرسة")]]
        story.append(Table(t_data, colWidths=[8*cm, 8*cm]))
        
        doc.build(story)
        self._trigger_print(path, "عقد التكوين")



    def _doc_certificate(self):
        if not self._check(): return
        cand = self._get_candidate()
        if not cand: return
        path = self._ask_save(f"شهادة_إدارية_{cand['last_name']}.pdf")
        if not path: return

        school = SchoolInfoDB.get()
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        import tempfile, datetime

        # نبحث عن تاريخ نجاح امتحان الطريق
        stages = TrainingDB.get_by_candidate(cand['id'])
        circuit_stage = next((s for s in stages if s['stage_type'] == 'circuit'), None)
        exam_date = ""
        if circuit_stage and circuit_stage.get('end_date'):
            exam_date = circuit_stage['end_date']
        elif circuit_stage and circuit_stage.get('start_date'):
            exam_date = circuit_stage['start_date']

        page_w, page_h = A4
        c = rl_canvas.Canvas(path, pagesize=A4)

        def txt_right(text, y_cm, font=ARABIC_FONT, size=12):
            c.setFont(font, size)
            c.drawRightString((page_w - 2*cm), y_cm * cm, ar(str(text)))

        def txt_center(text, y_cm, font=ARABIC_FONT, size=12):
            c.setFont(font, size)
            c.drawCentredString(page_w / 2, y_cm * cm, ar(str(text)))

        # --- الرأس ---
        txt_center("الجمهورية الجزائرية الديمقراطية الشعبية",
                   27.5, font=ARABIC_FONT_BOLD, size=13)
        txt_center("المندوبية الوطنية للأمن في الطرق",
                   26.7, size=11)
        # نستخرج الولاية من عنوان المدرسة إن أمكن
        wilaya_school = school.get('address', '')
        txt_center(f"المندوبية الولائية للأمن في الطرق لولاية {wilaya_school}",
                   25.9, size=11)
        txt_center(f"مدرسة تعليم السياقة  {school.get('name', '')}",
                   25.1, size=11)

        # --- خط فاصل ---
        c.setLineWidth(1)
        c.line(2*cm, 24.7*cm, page_w - 2*cm, 24.7*cm)

        # --- عنوان الشهادة في إطار ---
        title_w = 7*cm
        title_x = (page_w - title_w) / 2
        title_y = 23.3*cm
        c.setLineWidth(1.2)
        c.rect(title_x, title_y, title_w, 1*cm)
        txt_center("شهادة ادارية", 23.6, font=ARABIC_FONT_BOLD, size=14)

        # --- نص الشهادة ---
        school_name = school.get('name', '........')
        school_city = school.get('address', '........')

        # السطر الأول
        line1 = f"يشهد السيد مدير مدرسة تعليم السياقة  {school_name}  التي مقرها ببلدية  {school_city}"
        txt_right(line1, 22.2, size=11)

        # السطر الثاني: اسم المترشح + تاريخ الميلاد
        full_name = f"{cand.get('last_name', '')} {cand.get('first_name', '')}"
        birth_date = cand.get('birth_date', '............')
        line2_right = f"أن السيد  {full_name}"
        line2_left  = f"المولود بتاريخ  {birth_date}  ..."
        txt_right(line2_right + "   " + line2_left, 21.2, size=11)

        # السطر الثالث: البلدية والولاية
        commune = cand.get('birth_place_commune', '............')
        wilaya  = cand.get('birth_place_wilaya',  '............')
        txt_right(f"بلدية  {commune}    ولاية  {wilaya}  ...", 20.2, size=11)

        # العنوان
        address = cand.get('current_address', '') or cand.get('birth_place_commune', '............')
        txt_right(f"العنوان  {address}  ...", 19.2, size=11)

        # رقم الملف والامتحان
        file_no = str(cand.get('id', '......'))
        lic_type = cand.get('license_type', 'ب')
        exam_day = exam_date if exam_date else "........"
        line_exam = (f"رقم الملف  {file_no}  المسجل لدى مدرستنا قد اجتاز بنجاح"
                     f"  امتحان نيل رخصة السياقة صنف  {lic_type}  يوم  {exam_day}  ...")
        txt_right(line_exam, 18.0, size=11)

        # فقرة التسليم (سطرين)
        txt_right("سلمة هذه الشهادة للمعني بالأمر من أجل تقديمها لمصلحة", 16.8, size=11)
        txt_right("رخصة السياقة البيمترية ببلدية الإقامة لسحب رخصة السياقة البيومترية", 15.9, size=11)

        # تنبيه عدم الصلاحية
        txt_center("هذه الشهادة غير صالحة لقيادة المركبات",
                   14.6, font=ARABIC_FONT_BOLD, size=12)

        # خط فاصل
        c.setLineWidth(0.5)
        c.line(2*cm, 14.0*cm, page_w - 2*cm, 14.0*cm)

        # التوقيع والختم
        txt_center("توقيع وختم", 13.2, font=ARABIC_FONT_BOLD, size=12)

        # تاريخ التحرير
        today_str = date.today().strftime('%Y-%m-%d')
        txt_right(f"حُرّر بتاريخ:  {today_str}", 7.5, size=10)

        c.save()
        self._trigger_print(path, "الشهادة الإدارية")

    def _doc_payment_receipt(self):
        if not self._check(): return
        cand = self._get_candidate()
        if not cand: return
        path = self._ask_save(f"وصل_دفع_{cand['last_name']}.pdf")
        if not path: return
        school = SchoolInfoDB.get()
        payments = PaymentDB.get_by_candidate(cand['id'])
        total_paid = sum(p['amount'] for p in payments)
        rem = cand['total_amount'] - total_paid

        doc = self._make_doc(path); s = _pdf_styles(); story = []
        _pdf_header(story, school, "وصل دفع")
        story.append(Paragraph(ar(f"المترشح: {cand.get('last_name','')} {cand.get('first_name','')}"), s["h2"]))
        story.append(Paragraph(ar(f"رقم الهاتف: {cand.get('phone','')}"), s["right"]))
        story.append(Spacer(1, 0.4*cm))
        rows = [["ملاحظة","طريقة الدفع","المبلغ (دج)","التاريخ","رقم"]]
        for i, p in enumerate(payments, 1):
            rows.append([p.get('notes','') or '-', p.get('payment_method',''),
                         f"{p['amount']:,.0f}", p.get('date',''), str(i)])
        story.append(_styled_table(rows, [4*cm, 3*cm, 3*cm, 3*cm, 1.5*cm]))
        story.append(Spacer(1, 0.6*cm))

        summary = [
            ["البند", "المبلغ"],
            ["المبلغ الإجمالي للتكوين", f"{cand['total_amount']:,.0f} دج"],
            ["مجموع المدفوعات",         f"{total_paid:,.0f} دج"],
            ["المبلغ المتبقي",          f"{rem:,.0f} دج"],
        ]
        story.append(_styled_table(summary, [9*cm, 8*cm]))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(ar(f"حُرّر بتاريخ: {date.today().strftime('%Y-%m-%d')}"), s["right"]))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(ar("ختم وتوقيع المسؤول: ___________________"), s["right"]))
        doc.build(story)
        self._trigger_print(path, "وصل الدفع")

    def _doc_dispatch_table(self):
        if not self._check(): return
        
        selected = self._get_candidate() if self.selected_candidate_id else None
        cands = [selected] if selected else CandidateDB.get_all()
        
        if not cands:
            show_error("لا يوجد مترشحون للطباعة"); return
            
        import tempfile, os
        from datetime import datetime
        temp_dir = tempfile.gettempdir()
        path = os.path.join(temp_dir, f"dispatch_table_{int(datetime.now().timestamp())}.pdf")
        
        school = SchoolInfoDB.get()
        doc = self._make_doc(path)
        s = _pdf_styles()
        story = []
        
        # Header - matching the image
        story.append(Paragraph(ar("الجمهورية الجزائرية الديمقراطية الشعبية"), s["center"]))
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph(ar("وزارة الداخلية والجماعات المحلية والتهيئة العمرانية"), s["center"]))
        story.append(Paragraph(ar("المندوبية الوطنية للأمن في الطرق"), s["center"]))
        
        # Extract wilaya from school address (last word usually)
        addr = school.get('address', '')
        wilaya = addr.split(' ')[-1] if addr else '.......'
        story.append(Paragraph(ar(f"المندوبية الولائية للأمن في الطرق لولاية {wilaya}"), s["center"]))
        
        story.append(Spacer(1, 1.2*cm))
        # Title: جدول ارسال (Underlined)
        story.append(Paragraph(f"<u><b>{ar('جدول ارسال')}</b></u>", s["title"]))
        story.append(Spacer(1, 1*cm))
        
        # Table
        rows = [["تاريخ الميلاد", "الاسم واللقب"]]
        for c in cands:
            rows.append([c.get('birth_date',''), f"{c.get('last_name','')} {c.get('first_name','')}"])
            
        processed = [[ar(c) for c in row] for row in rows]
        t = Table(processed, colWidths=[7*cm, 10*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), ARABIC_FONT),
            ('FONTNAME', (0,0), (-1,0),  ARABIC_FONT_BOLD),
            ('GRID', (0,0), (-1,-1), 0.8, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        
        story.append(Spacer(1, 1*cm))
        # Date and Location
        story.append(Paragraph(ar(f"{wilaya} يوم: {date.today().strftime('%Y/%m/%d')}"), s["right"]))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(ar("ختم وتوقيع مدرسة تعليم السياقة"), s["center"]))
        
        doc.build(story)
        try:
            os.startfile(path, 'print')
        except Exception:
            try: os.startfile(path)
            except Exception as e: show_error(f"خطأ في فتح الملف: {e}")

    # --- وثائق جماعية ---------------------------------------------------------

    def _doc_candidates_list(self):
        if not self._check(): return
        path = self._ask_save("قائمة_المترشحين.pdf")
        if not path: return
        school = SchoolInfoDB.get()
        cands = CandidateDB.get_all()
        doc = self._make_doc(path, rightMargin=1.5*cm, leftMargin=1.5*cm,
                             pagesize=A4); s = _pdf_styles(); story = []
        _pdf_header(story, school, "قائمة المترشحين")
        rows = [["رقم الهاتف","نوع الرخصة","الجنس","تاريخ الميلاد","الاسم الكامل","رقم"]]
        for i, c in enumerate(cands, 1):
            rows.append([c.get('phone',''), c.get('license_type',''),
                         c.get('gender',''), c.get('birth_date',''),
                         f"{c.get('last_name','')} {c.get('first_name','')}", str(i)])
        story.append(_styled_table(rows,
            [3.5*cm, 2.5*cm, 1.8*cm, 3*cm, 5.5*cm, 1.2*cm]))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(ar(f"المجموع: {len(cands)} مترشح"), s["h2"]))
        doc.build(story)
        self._trigger_print(path, "قائمة المترشحين")

    def _doc_instructors_list(self):
        if not self._check(): return
        path = self._ask_save("قائمة_الممرنين.pdf")
        if not path: return
        school = SchoolInfoDB.get()
        instructors = InstructorDB.get_all()
        doc = self._make_doc(path); s = _pdf_styles(); story = []
        _pdf_header(story, school, "قائمة الممرنين")
        rows = [["سنوات الخبرة","الأصناف","الهاتف","الجنس","الاسم الكامل","رقم"]]
        for i, ins in enumerate(instructors, 1):
            rows.append([str(ins.get('experience_years','')), ins.get('categories',''),
                         ins.get('phone',''), ins.get('gender',''),
                         f"{ins.get('last_name','')} {ins.get('first_name','')}", str(i)])
        story.append(_styled_table(rows,
            [2.5*cm, 2.5*cm, 3*cm, 2*cm, 5.5*cm, 1.5*cm]))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(ar(f"المجموع: {len(instructors)} ممرن"), s["h2"]))
        doc.build(story)
        self._trigger_print(path, "قائمة الممرنين")

    def _doc_expenses_report(self):
        if not self._check(): return
        path = self._ask_save("تقرير_المصاريف.pdf")
        if not path: return
        school = SchoolInfoDB.get()
        expenses = ExpenseDB.get_all()
        doc = self._make_doc(path); s = _pdf_styles(); story = []
        _pdf_header(story, school, "تقرير المصاريف")
        rows = [["ملاحظة","المبلغ (دج)","التاريخ","نوع المصروف","رقم"]]
        total = 0
        for i, e in enumerate(expenses, 1):
            total += e['amount']
            rows.append([e.get('notes','') or '-', f"{e['amount']:,.0f}",
                         e.get('date',''), e.get('expense_type',''), str(i)])
        story.append(_styled_table(rows, [4.5*cm, 3*cm, 3*cm, 4*cm, 1.5*cm]))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(ar(f"المجموع الكلي للمصاريف: {total:,.0f} دج"), s["h2"]))
        doc.build(story)
        self._trigger_print(path, "تقرير المصاريف")

    def _doc_payments_report(self):
        if not self._check(): return
        path = self._ask_save("تقرير_المدفوعات.pdf")
        if not path: return
        school = SchoolInfoDB.get()
        cands = CandidateDB.get_all()
        doc = self._make_doc(path); s = _pdf_styles(); story = []
        _pdf_header(story, school, "تقرير المدفوعات")
        rows = [["المتبقي","المدفوع","الإجمالي","الاسم الكامل","رقم"]]
        total_global = 0; paid_global = 0
        for i, c in enumerate(cands, 1):
            paid = PaymentDB.get_total_by_candidate(c['id'])
            rem = c['total_amount'] - paid
            total_global += c['total_amount']; paid_global += paid
            rows.append([f"{rem:,.0f}", f"{paid:,.0f}", f"{c['total_amount']:,.0f}",
                         f"{c.get('last_name','')} {c.get('first_name','')}", str(i)])
        story.append(_styled_table(rows, [3*cm, 3*cm, 3*cm, 5.5*cm, 1.5*cm]))
        story.append(Spacer(1, 0.5*cm))
        summary = [["البند", "المبلغ"],
                   ["المبلغ الإجمالي المتفق عليه", f"{total_global:,.0f} دج"],
                   ["إجمالي المدفوعات",            f"{paid_global:,.0f} دج"],
                   ["إجمالي المتبقي",              f"{total_global - paid_global:,.0f} دج"]]
        story.append(_styled_table(summary, [9*cm, 8*cm]))
        doc.build(story)
        self._trigger_print(path, "تقرير المدفوعات")


    def _doc_exam_candidates_list(self):
        """وثيقة: قائمة المترشحين لنيل رخصة السياقة - مع نافذة اختيار متقدمة."""
        if not self._check():
            return

        all_cands = CandidateDB.get_all()
        if not all_cands:
            show_error("لا يوجد مترشحون في القاعدة"); return

        school = SchoolInfoDB.get()

        # ========== نافذة الإعداد ==========
        dlg = tk.Toplevel(self)
        dlg.title("إعداد قائمة المترشحين للامتحان")
        dlg.geometry("820x680")
        dlg.configure(bg=COLOR_BG)
        dlg.transient(self); dlg.grab_set()

        # --- رأس النافذة ---
        head = tk.Frame(dlg, bg="#0369a1", pady=14, padx=20)
        head.pack(fill="x")
        tk.Label(head, text="📋  إعداد قائمة المترشحين لنيل رخصة السياقة",
                 font=(FONT_FAMILY, 14, "bold"), bg="#0369a1", fg="white",
                 anchor="e").pack(side="right")

        body = tk.Frame(dlg, bg=COLOR_BG); body.pack(fill="both", expand=True, padx=15, pady=10)

        # --- يمين: إعدادات الوثيقة ---
        right_col = tk.Frame(body, bg=COLOR_BG, width=240)
        right_col.pack(side="right", fill="y", padx=(10, 0))
        right_col.pack_propagate(False)

        ro, rc_frame = make_card(right_col)
        ro.pack(fill="both", expand=True)

        section_title(rc_frame, "بيانات الامتحان", icon="🗓️")

        opts_vars = {}

        def lbl_entry(parent, label, key, default=""):
            tk.Label(parent, text=label, font=FONT_BOLD, bg=COLOR_CARD,
                     fg=COLOR_TEXT, anchor="e").pack(fill="x", pady=(6, 1))
            v = tk.StringVar(value=default)
            opts_vars[key] = v
            make_entry(parent, v, width=26).pack(fill="x", ipady=4)

        lbl_entry(rc_frame, "تاريخ الامتحان", "exam_date",
                  date.today().strftime("%d/%m/%Y"))
        lbl_entry(rc_frame, "مركز الامتحان", "exam_center", "")
        lbl_entry(rc_frame, "رقم الوثيقة (ر.ت)", "doc_ref", "")
        lbl_entry(rc_frame, "الولاية", "wilaya",
                  school.get('address','').split()[-1] if school.get('address') else "")

        tk.Frame(rc_frame, bg=COLOR_BORDER, height=1).pack(fill="x", pady=10)
        section_title(rc_frame, "طبيعة الامتحان", icon="📝")

        stage_var = tk.StringVar(value="all")
        stages_opts = [
            ("كل الأنواع", "all"),
            ("قانون المرور (كود)", "code"),
            ("المناورات (كرينو)", "creneau"),
            ("السياقة (طريق)", "circuit"),
        ]
        for txt, val in stages_opts:
            tk.Radiobutton(rc_frame, text=txt, variable=stage_var, value=val,
                           font=FONT_MAIN, bg=COLOR_CARD, fg=COLOR_TEXT,
                           activebackground=COLOR_CARD,
                           selectcolor=COLOR_PRIMARY_LIGHT,
                           anchor="e", justify="right").pack(fill="x", pady=2)

        # --- يسار: قائمة المترشحين ---
        left_col = tk.Frame(body, bg=COLOR_BG)
        left_col.pack(side="left", fill="both", expand=True)

        # عنوان + شريط بحث
        top_bar = tk.Frame(left_col, bg=COLOR_CARD, padx=8, pady=6,
                           relief="flat", bd=0)
        top_bar.pack(fill="x")

        tk.Label(top_bar, text="👥  اختر المترشحين",
                 font=(FONT_FAMILY, 12, "bold"), bg=COLOR_CARD,
                 fg=COLOR_PRIMARY, anchor="e").pack(fill="x")

        sv = tk.StringVar()
        sr = tk.Frame(top_bar, bg=COLOR_CARD); sr.pack(fill="x", pady=(4, 0))
        tk.Label(sr, text="🔍", bg=COLOR_CARD, fg=COLOR_PRIMARY,
                 font=(FONT_FAMILY, 11)).pack(side="right", padx=(0, 4))
        make_entry(sr, sv, width=30).pack(side="right", fill="x", expand=True, ipady=3)

        # أزرار تحديد الكل / إلغاء الكل
        sel_row = tk.Frame(left_col, bg="#e0f2fe", padx=6, pady=5)
        sel_row.pack(fill="x")

        # مجموعة iids المحددة
        selected_set = set()

        def select_all():
            for c in all_cands: selected_set.add(c['id'])
            populate_tree(sv.get().strip())

        def deselect_all():
            selected_set.clear()
            populate_tree(sv.get().strip())

        tk.Button(sel_row, text="✓ تحديد الكل", font=FONT_SMALL,
                  bg=COLOR_SUCCESS, fg="white", relief="flat", padx=10, pady=4,
                  cursor="hand2", command=select_all).pack(side="right", padx=3)
        tk.Button(sel_row, text="✗ إلغاء الكل", font=FONT_SMALL,
                  bg="#94a3b8", fg="white", relief="flat", padx=10, pady=4,
                  cursor="hand2", command=deselect_all).pack(side="right", padx=3)
        tk.Label(sel_row,
                 text="اضغط على أي صف لتحديده / إلغاء تحديده",
                 font=FONT_TINY, bg="#e0f2fe", fg="#0369a1",
                 anchor="e").pack(side="right", padx=8)

        # حاوية الجدول
        tree_frame = tk.Frame(left_col, bg=COLOR_CARD)
        tree_frame.pack(fill="both", expand=True)

        # Treeview مع عمود ✓ للتحديد
        cand_tree = ttk.Treeview(tree_frame,
                                 columns=("sel", "num", "name", "lic", "birth"),
                                 show="headings",
                                 style="Modern.Treeview",
                                 selectmode="browse")
        cand_tree.heading("sel",   text="✓",             anchor="center")
        cand_tree.heading("num",   text="رقم",            anchor="center")
        cand_tree.heading("name",  text="اللقب والاسم",   anchor="center")
        cand_tree.heading("lic",   text="الصنف",          anchor="center")
        cand_tree.heading("birth", text="تاريخ الميلاد",  anchor="center")
        cand_tree.column("sel",   width=35,  anchor="center", stretch=False)
        cand_tree.column("num",   width=45,  anchor="center", stretch=False)
        cand_tree.column("name",  width=220, anchor="center")
        cand_tree.column("lic",   width=55,  anchor="center", stretch=False)
        cand_tree.column("birth", width=110, anchor="center")

        vsb_c = ttk.Scrollbar(tree_frame, orient="vertical", command=cand_tree.yview)
        cand_tree.configure(yscrollcommand=vsb_c.set)
        vsb_c.pack(side="right", fill="y")
        cand_tree.pack(side="left", fill="both", expand=True)

        # تحديد الكل مبدئياً
        for c in all_cands:
            selected_set.add(c['id'])

        def populate_tree(filter_text=""):
            for item in cand_tree.get_children():
                cand_tree.delete(item)
            idx = 0
            for cand in all_cands:
                full = f"{cand['last_name']} {cand['first_name']}"
                if filter_text and filter_text.lower() not in full.lower() \
                        and filter_text not in cand.get('phone', ''):
                    continue
                iid = str(cand['id'])
                chk = "✓" if cand['id'] in selected_set else "○"
                tag = "sel" if cand['id'] in selected_set else ("even" if idx % 2 == 0 else "odd")
                cand_tree.insert("", "end", iid=iid, tags=(tag,),
                                 values=(chk, idx + 1, full,
                                         cand.get('license_type', 'B'),
                                         cand.get('birth_date', '')))
                idx += 1
            cand_tree.tag_configure("sel",  background="#bfdbfe", foreground="#1e3a8a")
            cand_tree.tag_configure("even", background="#f8fafc",  foreground=COLOR_TEXT)
            cand_tree.tag_configure("odd",  background=COLOR_CARD, foreground=COLOR_TEXT)

        populate_tree()

        def toggle_item(event):
            item = cand_tree.identify_row(event.y)
            if not item:
                return
            cid = int(item)
            if cid in selected_set:
                selected_set.discard(cid)
            else:
                selected_set.add(cid)
            populate_tree(sv.get().strip())

        cand_tree.bind("<Button-1>", toggle_item)
        sv.trace("w", lambda *a: populate_tree(sv.get().strip()))

        # --- شريط الأزرار السفلي ---
        bf = tk.Frame(dlg, bg=COLOR_BG, pady=12); bf.pack(side="bottom", fill="x", padx=20)
        ModernButton(bf, "إلغاء", dlg.destroy, icon="✗",
                     color=COLOR_TEXT_LIGHT).pack(side="left", padx=5)

        def do_generate():
            selected_ids = list(selected_set)
            if not selected_ids:
                show_error("يرجى تحديد مترشح واحد على الأقل"); return

            selected_cands = [c for c in all_cands if c['id'] in selected_ids]
            exam_date  = opts_vars["exam_date"].get().strip()
            exam_center= opts_vars["exam_center"].get().strip() or "............"
            doc_ref    = opts_vars["doc_ref"].get().strip()
            wilaya_val = opts_vars["wilaya"].get().strip()
            stage_type = stage_var.get()

            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"قائمة_المترشحين_{exam_date.replace('/','_')}.pdf",
                parent=dlg)
            if not path:
                return

            dlg.destroy()
            self._generate_exam_list_pdf(
                path, selected_cands, school, exam_date,
                exam_center, doc_ref, wilaya_val, stage_type)

        ModernButton(bf, "توليد الوثيقة PDF", do_generate,
                     icon="📄", color="#0369a1").pack(side="right", padx=5)

    def _generate_exam_list_pdf(self, path, cands, school, exam_date,
                                 exam_center, doc_ref, wilaya_val, stage_type):
        """يولّد PDF قائمة المترشحين للامتحان مطابق للنموذج الرسمي."""
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        import tempfile, datetime

        page_w, page_h = A4
        c = rl_canvas.Canvas(path, pagesize=A4)

        def txt_right(text, y_cm, font=ARABIC_FONT, size=10, x_cm=None):
            c.setFont(font, size)
            x = (x_cm * cm) if x_cm else (page_w - 1.5*cm)
            c.drawRightString(x, y_cm * cm, ar(str(text)))

        def txt_left(text, y_cm, font=ARABIC_FONT, size=10, x_cm=1.5):
            c.setFont(font, size)
            c.drawString(x_cm * cm, y_cm * cm, ar(str(text)))

        def txt_center(text, y_cm, font=ARABIC_FONT, size=10):
            c.setFont(font, size)
            c.drawCentredString(page_w / 2, y_cm * cm, ar(str(text)))

        # ========== الترويسة الحكومية ==========
        y = 28.5
        txt_center("الجمهورية الجزائرية الديمقراطية الشعبية",
                   y, ARABIC_FONT_BOLD, 13)
        y -= 0.7
        txt_center("وزارة الداخلية والجماعات المحلية والتهيئة العمرانية",
                   y, ARABIC_FONT, 10)
        y -= 0.55
        txt_center("المندوبيـة الوطنيـة للأمن في الطرق", y, ARABIC_FONT, 10)
        y -= 0.55
        txt_center(f"المندوبية الولائية للأمن في الطرق لولاية {wilaya_val}",
                   y, ARABIC_FONT, 10)

        # خط فاصل
        y -= 0.4
        c.setLineWidth(1)
        c.line(1.5*cm, y*cm, (page_w - 1.5*cm), y*cm)

        # ========== عنوان الوثيقة ==========
        y -= 0.9
        txt_center("قائمة المترشحين لنيل رخصة السياقة",
                   y, ARABIC_FONT_BOLD, 15)

        # خط تحت العنوان
        title_w = 10*cm
        title_x = (page_w - title_w) / 2
        c.setLineWidth(1.2)
        c.line(title_x, (y - 0.15)*cm, title_x + title_w, (y - 0.15)*cm)

        # ========== بيانات المدرسة والامتحان ==========
        y -= 0.9
        school_name = school.get('name', '.....................')
        school_phone= school.get('phone', '')
        school_cr   = school.get('commercial_register', '')

        # سطر: اسم المدرسة
        txt_right(f"مدرسة تعليم السياقة:  {school_name}", y, ARABIC_FONT_BOLD, 10)

        y -= 0.55
        # السطر الثاني: اسم المدير
        txt_right(f"رقاش جمال الدين", y, ARABIC_FONT, 10)  # يمكن تخصيصه من school_info

        y -= 0.55
        # السطر الثالث: رقم السجل التجاري | رقم الوثيقة
        left_info  = f"ب.ر.ت {school_cr}" if school_cr else ""
        right_info = f"ر.ت {doc_ref}" if doc_ref else ""
        mid_info   = school_phone
        if right_info:
            txt_right(right_info, y, "Helvetica", 9)
        if mid_info:
            txt_center(mid_info, y, "Helvetica", 9)
        if left_info:
            txt_left(left_info, y, "Helvetica", 9)

        y -= 0.55
        # مركز الامتحان + التاريخ
        txt_right(f"مركز الامتحان: {exam_center}", y, ARABIC_FONT, 10)
        txt_left(f"تاريخ الامتحان: {exam_date}", y, ARABIC_FONT, 10)

        # ========== رأس الجدول ==========
        y -= 0.6

        # عرض الأعمدة (بالـ cm) من اليمين إلى اليسار
        col_widths = [1.2, 2.5, 5.0, 1.3, 1.2, 2.8, 3.5]  # إجمالي ~17.5
        col_headers = ["رقم", "رقم التسجيل", "اللقب و الاسم", "السن", "الصنف",
                        "طبيعة الامتحان", "ملاحظة"]
        row_h = 0.7   # ارتفاع الصف
        header_h = 0.9

        # حساب مواضع الأعمدة (x من اليسار)
        total_w = sum(col_widths)
        margin_l = (page_w/cm - total_w) / 2
        col_x = [margin_l]
        for w in col_widths[:-1]:
            col_x.append(col_x[-1] + w)

        def draw_header_row(y_top):
            c.setFillColorRGB(0.2, 0.4, 0.7)
            c.rect(margin_l*cm, (y_top - header_h)*cm, total_w*cm, header_h*cm, fill=1, stroke=1)
            c.setFillColorRGB(1, 1, 1)
            for i, (hdr, cw, cx) in enumerate(zip(col_headers, col_widths, col_x)):
                c.setFont(ARABIC_FONT_BOLD, 9)
                c.drawCentredString((cx + cw/2)*cm, (y_top - header_h*0.55)*cm, ar(hdr))
            c.setFillColorRGB(0, 0, 0)

        draw_header_row(y)
        y -= header_h

        # ========== صفوف البيانات ==========
        def calc_age(birth_str):
            try:
                parts = birth_str.replace("/", "-").split("-")
                if len(parts) == 3:
                    by = int(parts[0]) if len(parts[0]) == 4 else int(parts[2])
                    return str(date.today().year - by)
            except Exception:
                pass
            return ""

        stage_label_map = {
            "code": "قانون المرور",
            "creneau": "المناورات",
            "circuit": "السياقة",
            "all": "الكل",
        }

        # حساب الإحصائيات
        count_code = count_creneau = count_circuit = 0

        for idx, cand in enumerate(cands):
            # تحديد طبيعة الامتحان
            stages = TrainingDB.get_by_candidate(cand['id'])
            if stage_type == "all":
                # نعرض آخر مرحلة نشطة
                active_stage = None
                for st in reversed(STAGE_ORDER):
                    s = next((x for x in stages if x['stage_type'] == st), None)
                    if s and s['status'] not in ("لم يبدأ", "ناجح"):
                        active_stage = st
                        break
                if not active_stage:
                    # أخذ أول مرحلة لم يبدأ بها
                    for st in STAGE_ORDER:
                        s = next((x for x in stages if x['stage_type'] == st), None)
                        if s and s['status'] == "لم يبدأ":
                            active_stage = st
                            break
                if not active_stage:
                    active_stage = "code"
                exam_nature = stage_label_map.get(active_stage, "")
            else:
                exam_nature = stage_label_map.get(stage_type, "")

            if "مرور" in exam_nature or "code" in exam_nature:
                count_code += 1
            elif "مناور" in exam_nature:
                count_creneau += 1
            elif "سياقة" in exam_nature:
                count_circuit += 1

            row_num = idx + 1
            age_str = calc_age(cand.get('birth_date', ''))
            reg_num = str(cand.get('national_id', '') or cand.get('id', ''))
            full_name = f"{cand.get('last_name', '')} {cand.get('first_name', '')}"
            lic_type = cand.get('license_type', 'B')

            # تلوين الصفوف
            if idx % 2 == 0:
                c.setFillColorRGB(1, 1, 1)
            else:
                c.setFillColorRGB(0.95, 0.97, 1.0)
            c.rect(margin_l*cm, (y - row_h)*cm, total_w*cm, row_h*cm, fill=1, stroke=0)
            c.setFillColorRGB(0, 0, 0)

            # خطوط الشبكة
            c.setStrokeColorRGB(0.78, 0.82, 0.9)
            c.setLineWidth(0.4)
            c.rect(margin_l*cm, (y - row_h)*cm, total_w*cm, row_h*cm, fill=0, stroke=1)
            # خطوط عمودية
            for cx in col_x[1:]:
                c.line(cx*cm, (y - row_h)*cm, cx*cm, y*cm)
            c.setStrokeColorRGB(0, 0, 0)

            row_data = [str(row_num), reg_num, full_name, age_str, lic_type, exam_nature, ""]
            for i, (val, cw, cx) in enumerate(zip(row_data, col_widths, col_x)):
                c.setFont(ARABIC_FONT if i != 0 else "Helvetica", 9)
                c.drawCentredString((cx + cw/2)*cm, (y - row_h*0.58)*cm, ar(str(val)))

            y -= row_h

            # صفحة جديدة إذا اقتربنا من النهاية
            if y < 5.5:
                c.showPage()
                y = 27.0
                draw_header_row(y)
                y -= header_h

        # ========== ملخص الإحصائيات ==========
        y -= 0.6
        c.setLineWidth(0.8)
        c.line(margin_l*cm, y*cm, (margin_l + total_w)*cm, y*cm)

        y -= 0.55
        total_count = len(cands)
        txt_right(f"المترشحين المدعوين {total_count}", y, ARABIC_FONT_BOLD, 11)

        y -= 0.6
        # اليمين: قانون المرور
        txt_right(f"قانون المرور: {count_code:02d}", y, ARABIC_FONT, 10)
        # الوسط: المناورات
        txt_center(f"المناورات: {count_creneau:02d}", y, ARABIC_FONT, 10)
        # اليسار: السياقة
        txt_left(f"السياقة {count_circuit}", y, ARABIC_FONT, 10)

        y -= 0.9
        # خانات التوقيع
        txt_right("قانون المرور:", y, ARABIC_FONT, 10)
        y -= 0.4
        txt_right("د. المناورات:", y, ARABIC_FONT, 10)
        y -= 0.4
        txt_right("السياقة:", y, ARABIC_FONT, 10)

        # التوقيع والختم (يسار)
        txt_left(f"{wilaya_val} يوم: {exam_date}", y + 0.8, ARABIC_FONT, 10)
        txt_left("ختم وتوقيع مدرسة تعليم السياقة", y + 0.1, ARABIC_FONT_BOLD, 10)

        c.save()
        self._trigger_print(path, "قائمة المترشحين للامتحان")


# ============================================================================
#  شاشة تسجيل الدخول
# ============================================================================

# بيانات افتراضية (يمكن تغييرها لاحقاً عبر قاعدة البيانات)
_DEFAULT_USERS = {
    "admin": "1234",
    "مدير":  "0000",
}


class LoginWindow:
    """نافذة تسجيل دخول احترافية تُعرض قبل النافذة الرئيسية."""

    def __init__(self):
        init_db()
        upgrade_db()

        self.root = tk.Tk()
        self.root.title("برنامج ميدانيك — تسجيل الدخول")
        self.root.geometry("480x600")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_HEADER)
        # توسيط النافذة
        self.root.eval('tk::PlaceWindow . center')
        self._logged_user = None
        self._build()
        self.root.mainloop()

    # ──────────────────────────────────────────────────────────
    def _build(self):
        root = self.root

        # ── خلفية متدرجة (محاكاة بإطارات) ──
        top_band = tk.Frame(root, bg=COLOR_HEADER, height=260)
        top_band.pack(fill="x")
        top_band.pack_propagate(False)

        # ── اللوجو 150×150 ──
        logo_shown = False
        for lp in [
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "attached_assets",
                         "WhatsApp_Image_2026-05-01_at_18.32.38_1777665526194.jpeg"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "attached_assets",
                         "WhatsApp_Image_2026-05-01_at_18.32.38_1777660833359.jpeg"),
        ]:
            if HAS_PIL and os.path.exists(lp) and not logo_shown:
                try:
                    from PIL import ImageDraw
                    size = 150
                    img  = Image.open(lp).convert("RGBA").resize((size, size), Image.LANCZOS)
                    mask = Image.new("L", (size, size), 0)
                    ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
                    out  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    out.paste(img, mask=mask)
                    self._logo_img = ImageTk.PhotoImage(out)
                    tk.Label(top_band, image=self._logo_img,
                             bg=COLOR_HEADER).pack(pady=(28, 10))
                    logo_shown = True
                except Exception:
                    pass

        if not logo_shown:
            tk.Label(top_band, text="🚗", font=(FONT_FAMILY, 64),
                     bg=COLOR_HEADER, fg=COLOR_ACCENT).pack(pady=(20, 6))

        tk.Label(top_band, text="ميدانيك",
                 font=(FONT_FAMILY, 22, "bold"),
                 bg=COLOR_HEADER, fg="white").pack()
        tk.Label(top_band, text="نظام إدارة مدرسة تعليم السياقة",
                 font=(FONT_FAMILY, 11),
                 bg=COLOR_HEADER, fg="#94a3b8").pack(pady=(2, 0))

        # ── بطاقة الدخول ──
        card = tk.Frame(root, bg=COLOR_CARD, padx=36, pady=30)
        card.pack(fill="both", expand=True, padx=0, pady=0)

        tk.Label(card, text="تسجيل الدخول",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg=COLOR_CARD, fg=COLOR_HEADER).pack(anchor="e", pady=(0, 18))

        # حقل اسم المستخدم
        tk.Label(card, text="اسم المستخدم", font=FONT_BOLD,
                 bg=COLOR_CARD, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._user_var = tk.StringVar(value="admin")
        ue = tk.Entry(card, textvariable=self._user_var,
                      font=FONT_MAIN, relief="solid", bd=1,
                      justify="right", fg=COLOR_TEXT, bg="white",
                      insertbackground=COLOR_PRIMARY)
        ue.pack(fill="x", ipady=8, pady=(4, 14))

        # حقل كلمة المرور
        tk.Label(card, text="كلمة المرور", font=FONT_BOLD,
                 bg=COLOR_CARD, fg=COLOR_TEXT, anchor="e").pack(fill="x")
        self._pass_var = tk.StringVar()
        pe = tk.Entry(card, textvariable=self._pass_var, show="●",
                      font=FONT_MAIN, relief="solid", bd=1,
                      justify="right", fg=COLOR_TEXT, bg="white",
                      insertbackground=COLOR_PRIMARY)
        pe.pack(fill="x", ipady=8, pady=(4, 6))

        # تلميح كلمة المرور الافتراضية
        tk.Label(card, text="(الافتراضي: admin / 1234)",
                 font=(FONT_FAMILY, 8), bg=COLOR_CARD, fg="#94a3b8",
                 anchor="e").pack(fill="x", pady=(0, 20))

        # رسالة الخطأ
        self._err_var = tk.StringVar()
        self._err_lbl = tk.Label(card, textvariable=self._err_var,
                                 font=FONT_SMALL, bg=COLOR_CARD, fg="#ef4444",
                                 anchor="e")
        self._err_lbl.pack(fill="x", pady=(0, 10))

        # زر الدخول
        login_btn = tk.Frame(card, bg=COLOR_PRIMARY, cursor="hand2")
        login_btn.pack(fill="x")
        self._login_lbl = tk.Label(login_btn, text="دخول",
                                   font=(FONT_FAMILY, 13, "bold"),
                                   bg=COLOR_PRIMARY, fg="white", pady=11)
        self._login_lbl.pack(fill="x")

        def _do_login(e=None):
            u = self._user_var.get().strip()
            p = self._pass_var.get().strip()
            if u in _DEFAULT_USERS and _DEFAULT_USERS[u] == p:
                self._logged_user = u
                self.root.destroy()
                app = DrivingSchoolApp(logged_user=u)
            else:
                self._err_var.set("❌  اسم المستخدم أو كلمة المرور غير صحيحة")

        login_btn.bind("<Button-1>", _do_login)
        self._login_lbl.bind("<Button-1>", _do_login)
        pe.bind("<Return>", _do_login)
        ue.bind("<Return>", lambda e: pe.focus())

        def _btn_hover(e):
            login_btn.configure(bg=COLOR_PRIMARY_DARK)
            self._login_lbl.configure(bg=COLOR_PRIMARY_DARK)
        def _btn_leave(e):
            login_btn.configure(bg=COLOR_PRIMARY)
            self._login_lbl.configure(bg=COLOR_PRIMARY)
        login_btn.bind("<Enter>", _btn_hover)
        login_btn.bind("<Leave>", _btn_leave)
        self._login_lbl.bind("<Enter>", _btn_hover)
        self._login_lbl.bind("<Leave>", _btn_leave)

        # تركيز تلقائي
        pe.focus_set()


# ============================================================================
#  التطبيق الرئيسي
# ============================================================================

class DrivingSchoolApp:
    def __init__(self, logged_user: str = "مدير النظام"):
        seed_demo_data()
        self._logged_user = logged_user
        self.root = tk.Tk()
        self.root.title("برنامج ميدانيك — إدارة مدرسة تعليم السياقة")
        self.root.geometry("1280x800")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#f1f5f9")
        try:
            self.root.state('zoomed')
        except Exception:
            try:
                self.root.attributes('-zoomed', True)
            except Exception:
                pass

        self._nav_refs     = []
        self._current_idx  = -1
        self._page_frames  = []
        self._topbar_title = None

        self._setup_styles()
        self._build_layout()
        self._build_status_bar()
        self.root.mainloop()

    # ──────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Notebook (للنوافذ المنبثقة)
        style.configure("Modern.TNotebook", background=COLOR_CARD, borderwidth=0,
                        tabmargins=[2, 5, 2, 0])
        style.configure("Modern.TNotebook.Tab",
                        font=(FONT_FAMILY, 10, "bold"), padding=[14, 8],
                        background="#e2e8f0", foreground=COLOR_TEXT, borderwidth=0)
        style.map("Modern.TNotebook.Tab",
                  background=[("selected", COLOR_PRIMARY), ("active", "#cbd5e1")],
                  foreground=[("selected", "white")])

        # Treeview
        style.configure("Modern.Treeview", font=FONT_MAIN, rowheight=32,
                        background=COLOR_CARD, foreground=COLOR_TEXT,
                        fieldbackground=COLOR_CARD, borderwidth=0)
        style.configure("Modern.Treeview.Heading",
                        font=(FONT_FAMILY, 11, "bold"),
                        background=COLOR_HEADER, foreground="white",
                        relief="flat", borderwidth=0, padding=[8, 8])
        style.map("Modern.Treeview",
                  background=[("selected", COLOR_PRIMARY)],
                  foreground=[("selected", "white")])
        style.map("Modern.Treeview.Heading",
                  background=[("active", COLOR_PRIMARY_DARK)])

        # Combobox
        style.configure("Modern.TCombobox",
                        fieldbackground=COLOR_INPUT_BG,
                        background=COLOR_CARD, borderwidth=1,
                        relief="flat", padding=4)

        # ── أشرطة تمرير رفيعة وعصرية ──
        for orient in ("Vertical", "Horizontal"):
            style.configure(f"Thin.{orient}.TScrollbar",
                            background="#cbd5e1", troughcolor="#f1f5f9",
                            borderwidth=0, arrowsize=0, width=8, relief="flat")
            style.map(f"Thin.{orient}.TScrollbar",
                      background=[("active", "#94a3b8"),
                                  ("pressed", "#64748b"),
                                  ("disabled", "#e2e8f0")])

    # ──────────────────────────────────────────────────────────
    def _build_layout(self):
        """البنية الكاملة: شريط جانبي يسار 200px + منطقة محتوى يمين."""
        main = tk.Frame(self.root, bg="#f1f5f9")
        main.pack(fill="both", expand=True)

        # ── الشريط الجانبي (يسار — 200px) ──
        self.sidebar = tk.Frame(main, bg=COLOR_SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ── منطقة المحتوى (يمين — يملأ الباقي) ──
        content_wrapper = tk.Frame(main, bg="#f1f5f9")
        content_wrapper.pack(side="left", fill="both", expand=True)

        self._build_topbar(content_wrapper)

        self.content = tk.Frame(content_wrapper, bg="#f1f5f9")
        self.content.pack(fill="both", expand=True, padx=14, pady=(8, 12))

        self._build_frames()
        self._navigate(0)

    # ──────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = self.sidebar

        # ── قسم اللوجو ──
        logo_area = tk.Frame(sb, bg=COLOR_HEADER, padx=0, pady=16)
        logo_area.pack(fill="x")

        self._sidebar_logo = None
        logo_shown = False
        for lp in [
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "attached_assets",
                         "WhatsApp_Image_2026-05-01_at_18.32.38_1777665526194.jpeg"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "attached_assets",
                         "WhatsApp_Image_2026-05-01_at_18.32.38_1777660833359.jpeg"),
        ]:
            if HAS_PIL and os.path.exists(lp) and not logo_shown:
                try:
                    from PIL import ImageDraw
                    size = 88
                    img  = Image.open(lp).convert("RGBA").resize((size, size), Image.LANCZOS)
                    mask = Image.new("L", (size, size), 0)
                    ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
                    out  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    out.paste(img, (0, 0), mask=mask)
                    self._sidebar_logo = ImageTk.PhotoImage(out)
                    tk.Label(logo_area, image=self._sidebar_logo,
                             bg=COLOR_HEADER).pack(pady=(0, 6))
                    logo_shown = True
                except Exception:
                    pass

        if not logo_shown:
            tk.Label(logo_area, text="🚗", font=(FONT_FAMILY, 34),
                     bg=COLOR_HEADER, fg=COLOR_ACCENT).pack(pady=(0, 4))

        tk.Label(logo_area, text="ميدانيك",
                 font=(FONT_FAMILY, 17, "bold"),
                 bg=COLOR_HEADER, fg="white").pack()
        tk.Label(logo_area, text="إدارة مدرسة السياقة",
                 font=(FONT_FAMILY, 9),
                 bg=COLOR_HEADER, fg="#94a3b8").pack(pady=(2, 0))

        # فاصل
        tk.Frame(sb, bg="#334155", height=1).pack(fill="x", padx=14, pady=(0, 6))

        # ── عناصر التنقل ──
        nav_container = tk.Frame(sb, bg=COLOR_SIDEBAR)
        nav_container.pack(fill="both", expand=True)

        nav_defs = [
            ("🏠", "الرئيسية"),
            ("🏫", "معلومات المدرسة"),
            ("🧾", "المترشحون"),
            ("🚗", "الممرنون"),
            ("📚", "مراحل التكوين"),
            ("📅", "الجدول الزمني"),
            ("💰", "المدفوعات"),
            ("💸", "المصاريف"),
            ("📊", "التقارير"),
            ("🖨️", "طباعة الوثائق"),
        ]
        self._nav_refs = []
        for i, (icon, label) in enumerate(nav_defs):
            self._make_nav_item(nav_container, icon, label, i)

        # فاصل سفلي
        tk.Frame(sb, bg="#334155", height=1).pack(fill="x", padx=14, pady=6)

        # ── تذييل الشريط الجانبي: المستخدم + خروج ──
        tk.Frame(sb, bg="#334155", height=1).pack(fill="x", padx=10, pady=(6, 0))

        bot = tk.Frame(sb, bg=COLOR_HEADER, padx=12, pady=10)
        bot.pack(fill="x", side="bottom")

        # بيانات المستخدم
        user_row = tk.Frame(bot, bg=COLOR_HEADER)
        user_row.pack(fill="x", pady=(0, 8))
        tk.Label(user_row, text="👤", font=(FONT_FAMILY, 16),
                 bg=COLOR_HEADER, fg=COLOR_ACCENT).pack(side="left")
        ubox = tk.Frame(user_row, bg=COLOR_HEADER)
        ubox.pack(side="left", padx=(8, 0))
        tk.Label(ubox, text=getattr(self, "_logged_user", "مدير النظام"),
                 font=(FONT_FAMILY, 10, "bold"),
                 bg=COLOR_HEADER, fg="white", anchor="w").pack(anchor="w")
        tk.Label(ubox, text="مسؤول النظام",
                 font=(FONT_FAMILY, 8),
                 bg=COLOR_HEADER, fg="#64748b", anchor="w").pack(anchor="w")

        # زر تسجيل الخروج
        logout_btn = tk.Frame(bot, bg="#ef4444", cursor="hand2")
        logout_btn.pack(fill="x", pady=(4, 0))
        tk.Label(logout_btn, text="  ⏻  تسجيل الخروج",
                 font=(FONT_FAMILY, 10, "bold"),
                 bg="#ef4444", fg="white", pady=7, anchor="center").pack(fill="x")
        def _do_logout(e=None):
            if messagebox.askyesno("تسجيل الخروج", "هل تريد الخروج من البرنامج؟"):
                self.root.destroy()
        logout_btn.bind("<Button-1>", _do_logout)
        for ch in logout_btn.winfo_children():
            ch.bind("<Button-1>", _do_logout)
        def _logout_hover(e):
            logout_btn.configure(bg="#dc2626")
            for ch in logout_btn.winfo_children(): ch.configure(bg="#dc2626")
        def _logout_leave(e):
            logout_btn.configure(bg="#ef4444")
            for ch in logout_btn.winfo_children(): ch.configure(bg="#ef4444")
        logout_btn.bind("<Enter>", _logout_hover)
        logout_btn.bind("<Leave>", _logout_leave)

        # تاريخ وإصدار
        tk.Label(bot, text=f"📅 {date.today().strftime('%Y-%m-%d')}  |  v2.0  🇩🇿",
                 font=(FONT_FAMILY, 8), bg=COLOR_HEADER, fg="#475569",
                 anchor="w").pack(fill="x", pady=(8, 0))

    def _make_nav_item(self, parent, icon, label, index):
        outer = tk.Frame(parent, bg=COLOR_SIDEBAR, cursor="hand2")
        outer.pack(fill="x")

        # شريط اللون النشط (يسار — بجانب محتوى التطبيق)
        accent = tk.Frame(outer, bg=COLOR_SIDEBAR, width=4)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(outer, bg=COLOR_SIDEBAR, padx=12, pady=10)
        inner.pack(side="left", fill="both", expand=True)

        icon_lbl = tk.Label(inner, text=icon, font=(FONT_FAMILY, 13),
                            bg=COLOR_SIDEBAR, fg="#64748b")
        icon_lbl.pack(side="left", padx=(0, 8))

        text_lbl = tk.Label(inner, text=label, font=(FONT_FAMILY, 10, "bold"),
                            bg=COLOR_SIDEBAR, fg="#94a3b8", anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        ref = {"outer": outer, "inner": inner,
               "icon": icon_lbl, "text": text_lbl, "accent": accent}
        self._nav_refs.append(ref)

        for w in [outer, inner, icon_lbl, text_lbl]:
            w.bind("<Enter>",    lambda e, i=index: self._nav_hover(i))
            w.bind("<Leave>",    lambda e, i=index: self._nav_leave(i))
            w.bind("<Button-1>", lambda e, i=index: self._navigate(i))

    def _nav_hover(self, index):
        if index == self._current_idx:
            return
        r = self._nav_refs[index]
        for w in [r["outer"], r["inner"]]:
            w.configure(bg=COLOR_SIDEBAR_HOVER)
        r["icon"].configure(bg=COLOR_SIDEBAR_HOVER, fg="#cbd5e1")
        r["text"].configure(bg=COLOR_SIDEBAR_HOVER, fg="#e2e8f0")

    def _nav_leave(self, index):
        if index == self._current_idx:
            return
        r = self._nav_refs[index]
        for w in [r["outer"], r["inner"]]:
            w.configure(bg=COLOR_SIDEBAR)
        r["icon"].configure(bg=COLOR_SIDEBAR, fg="#64748b")
        r["text"].configure(bg=COLOR_SIDEBAR, fg="#94a3b8")

    def _navigate(self, index):
        # إلغاء تفعيل الصفحة الحالية
        if 0 <= self._current_idx < len(self._nav_refs):
            old = self._nav_refs[self._current_idx]
            for w in [old["outer"], old["inner"]]:
                w.configure(bg=COLOR_SIDEBAR)
            old["icon"].configure(bg=COLOR_SIDEBAR, fg="#64748b")
            old["text"].configure(bg=COLOR_SIDEBAR, fg="#94a3b8")
            old["accent"].configure(bg=COLOR_SIDEBAR)

        # إخفاء كل الصفحات
        for frame, _ in self._page_frames:
            frame.pack_forget()

        # تفعيل الصفحة الجديدة
        self._current_idx = index
        ref = self._nav_refs[index]
        for w in [ref["outer"], ref["inner"]]:
            w.configure(bg="#1e3a8a")
        ref["icon"].configure(bg="#1e3a8a", fg="white")
        ref["text"].configure(bg="#1e3a8a", fg="white")
        ref["accent"].configure(bg=COLOR_ACCENT)

        if 0 <= index < len(self._page_frames):
            frame, title = self._page_frames[index]
            frame.pack(fill="both", expand=True)
            if self._topbar_title:
                self._topbar_title.configure(text=title)

    # ──────────────────────────────────────────────────────────
    def _build_topbar(self, parent):
        topbar = tk.Frame(parent, bg=COLOR_CARD, padx=20, pady=0)
        topbar.pack(fill="x", side="top")
        tk.Frame(parent, bg=COLOR_BORDER, height=1).pack(fill="x")

        inner = tk.Frame(topbar, bg=COLOR_CARD, pady=11)
        inner.pack(fill="both")

        # يمين: عنوان الصفحة
        right_bar = tk.Frame(inner, bg=COLOR_CARD)
        right_bar.pack(side="right")
        self._topbar_title = tk.Label(right_bar, text="الرئيسية",
                                       font=(FONT_FAMILY, 17, "bold"),
                                       bg=COLOR_CARD, fg=COLOR_HEADER, anchor="e")
        self._topbar_title.pack(side="right")

        # يسار: التاريخ + التنبيهات
        left_bar = tk.Frame(inner, bg=COLOR_CARD)
        left_bar.pack(side="left")

        try:
            v_alerts = VehicleDB.get_alerts()
            cands    = CandidateDB.get_all()
            unpaid   = [c for c in cands
                        if sum(p["amount"] for p in PaymentDB.get_by_candidate(c["id"]))
                        < c["total_amount"]]
            ac = len(v_alerts) + (1 if unpaid else 0)
        except Exception:
            ac = 0

        bell_clr  = COLOR_DANGER if ac > 0 else COLOR_TEXT_LIGHT
        bell_text = f"🔔 {ac}" if ac > 0 else "🔔"
        tk.Label(left_bar, text=bell_text, font=(FONT_FAMILY, 13),
                 bg=COLOR_CARD, fg=bell_clr, cursor="hand2").pack(side="left", padx=(0, 14))

        today  = date.today()
        d_str  = f"{today.day} {MONTHS_AR.get(today.strftime('%m'), '')} {today.year}"
        tk.Label(left_bar, text=f"📅  {d_str}", font=(FONT_FAMILY, 11),
                 bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT).pack(side="left")

    # ──────────────────────────────────────────────────────────
    def _build_frames(self):
        nav_defs = [
            ("الرئيسية",          DashboardFrame),
            ("معلومات المدرسة",   SchoolInfoFrame),
            ("المترشحون",         CandidatesFrame),
            ("الممرنون",          InstructorsFrame),
            ("مراحل التكوين",     TrainingFrame),
            ("الجدول الزمني",     ScheduleFrame),
            ("المدفوعات",         PaymentsFrame),
            ("المصاريف",          ExpensesFrame),
            ("التقارير",          ReportsFrame),
            ("طباعة الوثائق",    DocumentsFrame),
        ]
        # يحتاج DashboardFrame وReportsFrame لـ callback للتنقل
        navigate_aware = (DashboardFrame, ReportsFrame)
        self._page_frames = []
        for title, FrameClass in nav_defs:
            if FrameClass in navigate_aware:
                f = FrameClass(self.content, navigate_cb=self._navigate)
            else:
                f = FrameClass(self.content)
            f.pack_forget()
            self._page_frames.append((f, title))

    # ──────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=COLOR_HEADER, padx=15, pady=5)
        bar.pack(fill="x", side="bottom")
        nc = len(CandidateDB.get_all())
        ni = len(InstructorDB.get_all())
        ar_s  = "العربية ✓" if HAS_ARABIC_LIBS  else "العربية ✗"
        pdf_s = "PDF ✓"     if HAS_REPORTLAB    else "PDF ✗"
        tk.Label(bar,
                 text=f"المترشحون: {nc}   |   الممرنون: {ni}   |   {pdf_s}   |   {ar_s}   |   قاعدة البيانات ✓",
                 font=FONT_SMALL, bg=COLOR_HEADER, fg="white").pack(side="right")
        tk.Label(bar, text="v2.0  |  برنامج ميدانيك  |  الجزائر",
                 font=FONT_SMALL, bg=COLOR_HEADER, fg="#94a3b8").pack(side="left")

    pass  # placeholder — الأساليب القديمة أُزيلت


if __name__ == "__main__":
    LoginWindow()