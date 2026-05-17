# -*- coding: utf-8 -*-
"""يولّد دليل المطوّر لبرنامج ميدانيك — PDF عربي."""
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("AR",   FONT_REG))
pdfmetrics.registerFont(TTFont("AR-B", FONT_BOLD))

def ar(text):
    return get_display(arabic_reshaper.reshape(text))

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
RIGHT  = PAGE_W - MARGIN

PRIMARY    = colors.HexColor("#1e40af")
ACCENT     = colors.HexColor("#0ea5e9")
DARK       = colors.HexColor("#0f172a")
GRAY       = colors.HexColor("#475569")
LIGHT_BG   = colors.HexColor("#f1f5f9")
GREEN_BG   = colors.HexColor("#dcfce7")
RED_BG     = colors.HexColor("#fee2e2")
YELLOW_BG  = colors.HexColor("#fef3c7")
BLUE_BG    = colors.HexColor("#dbeafe")


# ── مساعدات الرسم ─────────────────────────────────────────────────────────

def draw_header(c, page_num, subtitle="دليل المطوّر"):
    c.setFillColor(PRIMARY)
    c.rect(0, PAGE_H - 2.2*cm, PAGE_W, 2.2*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("AR-B", 17)
    c.drawRightString(RIGHT, PAGE_H - 1.35*cm, ar(f"برنامج ميدانيك  —  {subtitle}"))
    c.setFont("AR", 9)
    c.drawString(MARGIN, PAGE_H - 1.35*cm, f"Page {page_num}")

def draw_footer(c):
    c.setFillColor(GRAY)
    c.setFont("AR", 9)
    c.drawCentredString(PAGE_W/2, 1.6*cm, ar("للدعم والتفعيل — تواصل معنا:"))
    c.setFont("AR", 10)
    c.drawCentredString(PAGE_W/2, 1.05*cm, "Tel / WhatsApp:  +213 540 772 807    |    contact@midanic.com")
    c.setFont("AR", 8)
    c.drawCentredString(PAGE_W/2, 0.5*cm, ar("ميدانيك © 2026 — جميع الحقوق محفوظة"))

def section_title(c, y, title):
    c.setFillColor(PRIMARY)
    c.setFont("AR-B", 14)
    c.drawRightString(RIGHT, y, ar(title))
    y -= 0.3*cm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line(RIGHT, y, RIGHT - 7*cm, y)
    return y - 0.5*cm

def step_box(c, y, num, title, lines, bg=LIGHT_BG, badge=PRIMARY):
    box_h = 1.15*cm + len(lines)*0.62*cm
    c.setFillColor(bg)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2*MARGIN, box_h, 8, fill=1, stroke=0)
    c.setFillColor(badge)
    c.circle(MARGIN + 0.65*cm, y - 0.65*cm, 0.42*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("AR-B", 13)
    c.drawCentredString(MARGIN + 0.65*cm, y - 0.8*cm, str(num))
    c.setFillColor(DARK)
    c.setFont("AR-B", 12)
    c.drawRightString(RIGHT - 0.3*cm, y - 0.8*cm, ar(title))
    ty = y - 1.45*cm
    for line in lines:
        if line.startswith("CODE:"):
            c.setFont("Courier-Bold", 9)
            c.setFillColor(colors.HexColor("#0f172a"))
            c.drawRightString(RIGHT - 0.5*cm, ty, line[5:])
            c.setFont("AR", 10.5)
            c.setFillColor(DARK)
        else:
            c.setFont("AR", 10.5)
            c.setFillColor(DARK)
            c.drawRightString(RIGHT - 0.5*cm, ty, ar(line))
        ty -= 0.62*cm
    return y - box_h - 0.35*cm

def info_box(c, y, title, lines, bg, border):
    box_h = 0.95*cm + len(lines)*0.57*cm
    c.setFillColor(bg)
    c.setStrokeColor(border)
    c.setLineWidth(1.5)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2*MARGIN, box_h, 6, fill=1, stroke=1)
    c.setFillColor(border)
    c.setFont("AR-B", 11)
    c.drawRightString(RIGHT - 0.4*cm, y - 0.65*cm, ar(title))
    c.setFillColor(DARK)
    c.setFont("AR", 10)
    ty = y - 1.3*cm
    for line in lines:
        c.drawRightString(RIGHT - 0.6*cm, ty, ar(line))
        ty -= 0.57*cm
    return y - box_h - 0.3*cm

def file_row(c, y, name, role, color_dot=PRIMARY):
    c.setFillColor(color_dot)
    c.circle(RIGHT - 0.3*cm, y + 0.15*cm, 0.13*cm, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Courier-Bold", 9)
    c.drawRightString(RIGHT - 0.6*cm, y, name)
    c.setFillColor(GRAY)
    c.setFont("AR", 10)
    c.drawRightString(RIGHT - 0.6*cm - 4.5*cm, y, ar(role))
    return y - 0.55*cm


# ══════════════════════════════════════════════════════════════════════════
#  إنشاء الـ PDF
# ══════════════════════════════════════════════════════════════════════════
c = canvas.Canvas("Medanic_Dev_Guide.pdf", pagesize=A4)


# ════════════════ الصفحة 1 — الملفات + بناء الـ EXE ════════════════
draw_header(c, 1)
y = PAGE_H - 2.8*cm

# غلاف
c.setFillColor(PRIMARY)
c.setFont("AR-B", 20)
c.drawRightString(RIGHT, y, ar("دليل المطوّر — برنامج ميدانيك"))
y -= 0.45*cm
c.setStrokeColor(ACCENT); c.setLineWidth(2)
c.line(RIGHT, y, MARGIN, y)
y -= 0.7*cm

# --- قسم الملفات ---
y = section_title(c, y, "الملفات وأدوارها")

# ملفات البناء
c.setFillColor(GRAY); c.setFont("AR-B", 10)
c.drawRightString(RIGHT, y, ar("للبناء (أنت فقط):"))
y -= 0.5*cm
for name, role, dot in [
    ("driving_school_single.py", "الكود الرئيسي للبرنامج", PRIMARY),
    ("license_guard.py",          "نظام التجربة والتفعيل",  PRIMARY),
    ("BUILD_EXE.bat",             "يبني Medanic.exe جاهزاً للتوزيع", PRIMARY),
    ("PATCH_DB_FIX.bat",          "يصلح مشكلة عدم حفظ البيانات في EXE", colors.HexColor("#d97706")),
    ("medanic_icon.ico",          "أيقونة البرنامج", GRAY),
    ("medanic_logo.png",          "شعار البرنامج",   GRAY),
    ("keygen_tool.py",            "مولّد مفاتيح التفعيل (لك أنت فقط — لا ترسله)", colors.HexColor("#dc2626")),
]:
    y = file_row(c, y, name, role, dot)

y -= 0.3*cm
c.setFillColor(GRAY); c.setFont("AR-B", 10)
c.drawRightString(RIGHT, y, ar("للزبون بعد التثبيت:"))
y -= 0.5*cm
for name, role, dot in [
    ("Medanic.exe",         "البرنامج المُجمَّع الوحيد الذي يُرسَل",   colors.HexColor("#16a34a")),
    ("CLIENT_INSTALL.bat",  "ينشئ اختصار سطح المكتب (أول مرة فقط)",   colors.HexColor("#16a34a")),
    ("BACKUP.bat",          "نسخ احتياطي لقاعدة البيانات",             colors.HexColor("#16a34a")),
    ("RESTORE.bat",         "استعادة من نسخة احتياطية",               colors.HexColor("#16a34a")),
    ("FIX_WIN7.bat",        "إصلاح خطأ DLL (عند الحاجة فقط)",         colors.HexColor("#d97706")),
]:
    y = file_row(c, y, name, role, dot)

y -= 0.5*cm

# --- قسم البناء ---
y = section_title(c, y, "بناء الـ EXE — خطوة بخطوة")

y = step_box(c, y, 1, "استخرج Medanic_Update.zip في مجلد فارغ", [
    "انقر يمين على الملف ← استخراج هنا",
    "تأكد أن جميع الملفات في نفس المجلد",
])
y = step_box(c, y, 2, "شغّل BUILD_EXE.bat", [
    "انقر مرتين على BUILD_EXE.bat",
    "الانتظار 3-5 دقائق (تثبيت PyInstaller والبناء)",
    "ستجد الناتج في:  dist\\Medanic.exe",
], bg=GREEN_BG, badge=colors.HexColor("#16a34a"))
y = step_box(c, y, 3, "أرسل للزبون هذه الملفات فقط", [
    "✓  dist\\Medanic.exe",
    "✓  CLIENT_INSTALL.bat  +  BACKUP.bat  +  RESTORE.bat",
    "✗  لا ترسل أي ملف .py أو keygen_tool.py أبداً",
], bg=YELLOW_BG, badge=colors.HexColor("#d97706"))

draw_footer(c)
c.showPage()


# ════════════════ الصفحة 2 — التجربة والتفعيل ════════════════
draw_header(c, 2, "التجربة والتفعيل")
y = PAGE_H - 2.8*cm

y = section_title(c, y, "آلية فترة التجربة المجانية (48 ساعة)")

y = info_box(c, y, "كيف تعمل التجربة؟", [
    "• أول تشغيل: يعمل البرنامج مجاناً لمدة 48 ساعة",
    "• العداد يظهر في عنوان النافذة:  ⏳ التجربة: 48س 00د متبقية",
    "• بعد 48 ساعة: تظهر نافذة التفعيل مع HWID + رقم هاتفك",
    "• الزبون يتواصل معك → توليد مفتاح → تفعيل دائم",
], bg=BLUE_BG, border=ACCENT)

y -= 0.2*cm
y = section_title(c, y, "توليد مفتاح التفعيل")

y = step_box(c, y, 1, "الزبون يرسل لك رمز HWID", [
    "بعد انتهاء 48 ساعة تظهر نافذة التفعيل",
    "الزبون يضغط (نسخ HWID) ويرسله لك عبر WhatsApp",
    "الـ HWID: 16 حرفاً مثل:  A3F7C2D1B8E04591",
])
y = step_box(c, y, 2, "شغّل أداة توليد المفتاح", [
    "افتح Command Prompt في مجلد الملفات واكتب:",
    "CODE:python keygen_tool.py",
    "الصق HWID الزبون واضغط (توليد المفتاح)",
    "انسخ المفتاح بصيغة:  XXXXX-XXXXX-XXXXX-XXXXX",
], bg=BLUE_BG, badge=ACCENT)
y = step_box(c, y, 3, "الزبون يُدخل المفتاح ← التفعيل الدائم ✓", [
    "الزبون يُلصق المفتاح في خانة (مفتاح التفعيل)",
    "يضغط زر (تفعيل) — البرنامج يفتح دون قيود",
    "المفتاح يعمل للأبد على نفس الجهاز",
], bg=GREEN_BG, badge=colors.HexColor("#16a34a"))

y -= 0.2*cm
y = info_box(c, y, "⚠  انتبه — الترخيص مرتبط بالجهاز", [
    "• كل جهاز له HWID مختلف — المفتاح لا ينقل لجهاز آخر",
    "• إذا غيّر الزبون جهازه أو أعاد تنصيب Windows → مفتاح جديد",
    "• احتفظ بسجل Excel: الاسم، HWID، المفتاح، التاريخ، المبلغ",
], bg=YELLOW_BG, border=colors.HexColor("#d97706"))

draw_footer(c)
c.showPage()


# ════════════════ الصفحة 3 — المشاكل الشائعة ════════════════
draw_header(c, 3, "المشاكل الشائعة وحلولها")
y = PAGE_H - 2.8*cm

# مشكلة 1
y = info_box(c, y, "❌  البيانات لا تُحفظ بعد بناء EXE", [
    "السبب: مسار قاعدة البيانات يشير للمجلد الخاطئ",
    "الحل:",
    "  1. شغّل PATCH_DB_FIX.bat (يُصلح الكود تلقائياً)",
    "  2. شغّل BUILD_EXE.bat من جديد",
    "  3. أرسل Medanic.exe الجديد للزبون",
], bg=RED_BG, border=colors.HexColor("#dc2626"))

# مشكلة 2
y = info_box(c, y, "❌  خطأ DLL / البرنامج لا يفتح عند الزبون", [
    "السبب: Windows قديم بدون VC++ Runtime",
    "الحل:",
    "  1. أرسل FIX_WIN7.bat للزبون",
    "  2. ينقر يمين ← تشغيل كمسؤول (Run as Administrator)",
    "  3. ينتظر دقيقتين للتحميل والتثبيت",
    "  4. يفتح Medanic مجدداً",
], bg=RED_BG, border=colors.HexColor("#dc2626"))

# مشكلة 3
y = info_box(c, y, "❌  الزبون فقد بياناته", [
    "الحل:",
    "  1. أرسل RESTORE.bat للزبون (إذا لم يكن لديه)",
    "  2. ينقر مرتين عليه",
    "  3. يختار اسم النسخة الاحتياطية من القائمة",
    "  4. تتم الاستعادة تلقائياً",
    "النصيحة: علّم الزبون تشغيل BACKUP.bat كل أسبوع",
], bg=YELLOW_BG, border=colors.HexColor("#d97706"))

# مشكلة 4
y = info_box(c, y, "❌  الزبون ينسى مفتاح التفعيل", [
    "المفتاح محفوظ تلقائياً في الجهاز — لا يحتاج إعادة إدخال",
    "إذا أعاد تنصيب Windows أو غيّر جهازه:",
    "  → ولّد مفتاحاً جديداً بـ HWID الجديد",
    "لهذا احتفظ دائماً بسجل عملائك في Excel",
], bg=BLUE_BG, border=ACCENT)

# مشكلة 5
y = info_box(c, y, "❌  اختصار سطح المكتب لا يعمل", [
    "الحل: شغّل CLIENT_INSTALL.bat مجدداً",
    "تأكد أن Medanic.exe في نفس المجلد",
], bg=LIGHT_BG, border=GRAY)

# خلاصة
y -= 0.3*cm
c.setFillColor(PRIMARY)
c.roundRect(MARGIN, y - 2.0*cm, PAGE_W - 2*MARGIN, 2.0*cm, 10, fill=1, stroke=0)
c.setFillColor(colors.white)
c.setFont("AR-B", 13)
c.drawCentredString(PAGE_W/2, y - 0.75*cm, ar("معلومات الاتصال المُضمَّنة في البرنامج"))
c.setFont("AR", 11)
c.drawCentredString(PAGE_W/2, y - 1.4*cm,
    ar("هاتف: +213 540 772 807    |    إيميل: contact@midanic.com"))

draw_footer(c)
c.showPage()

c.save()
print("OK: Medanic_Dev_Guide.pdf")
