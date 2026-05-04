"""يولّد دليل النسخ والنقل في ملف PDF عربي."""
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("AR", FONT_REG))
pdfmetrics.registerFont(TTFont("AR-B", FONT_BOLD))


def ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
RIGHT = PAGE_W - MARGIN

PRIMARY = colors.HexColor("#1e40af")
ACCENT = colors.HexColor("#0ea5e9")
DARK = colors.HexColor("#0f172a")
GRAY = colors.HexColor("#475569")
LIGHT_BG = colors.HexColor("#f1f5f9")
GREEN_BG = colors.HexColor("#dcfce7")
RED_BG = colors.HexColor("#fee2e2")
YELLOW_BG = colors.HexColor("#fef3c7")


def draw_header(c, page_num):
    c.setFillColor(PRIMARY)
    c.rect(0, PAGE_H - 2.2 * cm, PAGE_W, 2.2 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("AR-B", 18)
    c.drawRightString(RIGHT, PAGE_H - 1.4 * cm, ar("برنامج ميدانيك  —  دليل النسخ والنقل"))
    c.setFont("AR", 9)
    c.drawString(MARGIN, PAGE_H - 1.4 * cm, f"Page {page_num}")


def draw_footer(c):
    c.setFillColor(GRAY)
    c.setFont("AR", 9)
    c.drawCentredString(PAGE_W / 2, 1.6 * cm,
                        ar("للدعم والتفعيل — اتصل بنا:"))
    c.setFont("AR", 10)
    c.drawCentredString(PAGE_W / 2, 1.05 * cm,
                        "Tel / WhatsApp:  +213 540 77 28 07")
    c.setFont("AR", 8)
    c.drawCentredString(PAGE_W / 2, 0.5 * cm,
                        ar("ميدانيك © 2026 — جميع الحقوق محفوظة"))


def step_box(c, y, num, title, lines, bg=LIGHT_BG, badge=PRIMARY):
    box_h = 1.2 * cm + len(lines) * 0.65 * cm
    c.setFillColor(bg)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2 * MARGIN, box_h, 8, fill=1, stroke=0)

    c.setFillColor(badge)
    c.circle(MARGIN + 0.7 * cm, y - 0.7 * cm, 0.45 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("AR-B", 14)
    c.drawCentredString(MARGIN + 0.7 * cm, y - 0.85 * cm, str(num))

    c.setFillColor(DARK)
    c.setFont("AR-B", 13)
    c.drawRightString(RIGHT - 0.3 * cm, y - 0.85 * cm, ar(title))

    c.setFont("AR", 11)
    c.setFillColor(DARK)
    ty = y - 1.55 * cm
    for line in lines:
        if line.startswith("CODE:"):
            txt = line[5:]
            c.setFillColor(colors.HexColor("#0f172a"))
            c.setFont("Courier-Bold", 10)
            c.drawRightString(RIGHT - 0.5 * cm, ty, txt)
            c.setFont("AR", 11)
            c.setFillColor(DARK)
        else:
            c.drawRightString(RIGHT - 0.5 * cm, ty, ar(line))
        ty -= 0.65 * cm
    return y - box_h - 0.4 * cm


def info_box(c, y, title, lines, bg, border):
    box_h = 1.0 * cm + len(lines) * 0.6 * cm
    c.setFillColor(bg)
    c.setStrokeColor(border)
    c.setLineWidth(1.5)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2 * MARGIN, box_h, 6, fill=1, stroke=1)
    c.setFillColor(border)
    c.setFont("AR-B", 12)
    c.drawRightString(RIGHT - 0.4 * cm, y - 0.7 * cm, ar(title))
    c.setFillColor(DARK)
    c.setFont("AR", 10.5)
    ty = y - 1.4 * cm
    for line in lines:
        c.drawRightString(RIGHT - 0.6 * cm, ty, ar(line))
        ty -= 0.6 * cm
    return y - box_h - 0.3 * cm


# ── إنشاء الـ PDF ─────────────────────────────────────────────
c = canvas.Canvas("Medanic_Transfer_Guide.pdf", pagesize=A4)

# ═══════════════════ الصفحة 1 ═══════════════════
draw_header(c, 1)
y = PAGE_H - 3.0 * cm

c.setFillColor(PRIMARY)
c.setFont("AR-B", 16)
c.drawRightString(RIGHT, y, ar("نسخ البرنامج لجهاز العميل"))
y -= 0.4 * cm
c.setStrokeColor(ACCENT)
c.setLineWidth(2)
c.line(RIGHT, y, RIGHT - 8 * cm, y)
y -= 0.8 * cm

# الخطوة 1
y = step_box(c, y, 1, "على جهازك — افتح المجلد", [
    "افتح المجلد التالي:",
    "CODE:C:\\Users\\DELL\\Desktop\\midanic_driving_school\\",
])

# الخطوة 2
y = step_box(c, y, 2, "اختر هذه الملفات السبعة فقط", [
    "✓  driving_school_single.py",
    "✓  license_guard.py",
    "✓  medanic_icon.ico",
    "✓  medanic_logo.png",
    "✓  INSTALL.bat",
    "✓  BACKUP.bat",
    "✓  RESTORE.bat",
], bg=GREEN_BG, badge=colors.HexColor("#16a34a"))

# تحذير
y = info_box(c, y, "⚠  لا تنسخ هذه الملفات أبداً للعميل:", [
    "✗  keygen_tool.py     ← هذا لك أنت فقط (مولّد المفاتيح)",
    "✗  مجلد Backups       ← يخصّك",
    "✗  مجلد __pycache__   ← غير ضروري",
    "✗  driving_school.db  ← قاعدة بياناتك الشخصية",
], bg=RED_BG, border=colors.HexColor("#dc2626"))

# الخطوة 3
y = step_box(c, y, 3, "ضع الملفات في مجلد جديد واضغطها", [
    "1. أنشئ مجلد جديد على سطح المكتب اسمه: Medanic_Setup",
    "2. الصق الملفات السبعة بداخله",
    "3. انقر يمين على المجلد ← Envoyer vers ← Dossier compressé",
    "4. سيُنشأ ملف: Medanic_Setup.zip  (حوالي 600 KB)",
])

draw_footer(c)
c.showPage()

# ═══════════════════ الصفحة 2 ═══════════════════
draw_header(c, 2)
y = PAGE_H - 3.0 * cm

c.setFillColor(PRIMARY)
c.setFont("AR-B", 16)
c.drawRightString(RIGHT, y, ar("نقل الملف وتثبيته عند العميل"))
y -= 0.4 * cm
c.setStrokeColor(ACCENT)
c.setLineWidth(2)
c.line(RIGHT, y, RIGHT - 8 * cm, y)
y -= 0.8 * cm

# الخطوة 4
y = step_box(c, y, 4, "انقل الملف للعميل (اختر طريقة)", [
    "💾  USB         : انسخ Medanic_Setup.zip إلى مفتاح ذاكرة",
    "📧  Email       : أرسله بالبريد الإلكتروني (الحجم 600 KB)",
    "☁  Google Drive : ارفعه وأرسل الرابط للعميل",
])

# الخطوة 5
y = step_box(c, y, 5, "على جهاز العميل — التثبيت", [
    "1. استخراج Medanic_Setup.zip على سطح المكتب",
    "2. النقر مرتين على ملف: INSTALL.bat",
    "3. الموافقة على رسالة الأمان (Exécuter)",
    "4. الانتظار دقيقة حتى ينتهي التثبيت",
    "5. ستظهر نافذة التفعيل مع HWID مكوّن من 16 حرف",
    "6. العميل يُرسلك HWID عبر WhatsApp",
], bg=colors.HexColor("#dbeafe"), badge=ACCENT)

# الخطوة 6
y = step_box(c, y, 6, "على جهازك — توليد المفتاح", [
    "افتح Command Prompt واكتب:",
    "CODE:cd C:\\Users\\DELL\\Desktop\\midanic_driving_school",
    "CODE:python keygen_tool.py",
    "ستفتح نافذة — الصق HWID العميل واضغط (توليد)",
    "انسخ المفتاح وأرسله للعميل عبر WhatsApp",
])

# الخطوة 7
y = step_box(c, y, 7, "العميل يُدخل المفتاح ويبدأ العمل ✓", [
    "العميل يُلصق المفتاح في خانة (مفتاح التفعيل)",
    "يضغط زر (تفعيل) — البرنامج يفتح مباشرة",
    "المفتاح يعمل للأبد على جهاز العميل",
], bg=GREEN_BG, badge=colors.HexColor("#16a34a"))

draw_footer(c)
c.showPage()

# ═══════════════════ الصفحة 3 — ملاحظات ═══════════════════
draw_header(c, 3)
y = PAGE_H - 3.0 * cm

c.setFillColor(PRIMARY)
c.setFont("AR-B", 16)
c.drawRightString(RIGHT, y, ar("ملاحظات مهمة"))
y -= 0.4 * cm
c.setStrokeColor(ACCENT)
c.setLineWidth(2)
c.line(RIGHT, y, RIGHT - 5 * cm, y)
y -= 0.8 * cm

y = info_box(c, y, "🔒 الأمان", [
    "• كل جهاز له HWID مختلف — المفتاح لا يعمل على جهاز آخر",
    "• إذا غيّر العميل جهازه أو أعاد تنصيب Windows → يحتاج مفتاحاً جديداً",
    "• ملف keygen_tool.py لا يُسلَّم لأي عميل أبداً",
], bg=YELLOW_BG, border=colors.HexColor("#ca8a04"))

y = info_box(c, y, "📋 سجّل عملاءك في Excel", [
    "احفظ لكل عميل: التاريخ، الاسم، المدرسة، الولاية، HWID، المفتاح، المبلغ",
    "هذا يساعدك على إعادة توليد المفتاح إذا فقده العميل",
], bg=colors.HexColor("#e0f2fe"), border=ACCENT)

y = info_box(c, y, "💾 النسخ الاحتياطي عند العميل", [
    "علّم العميل أن يضغط BACKUP.bat كل أسبوع",
    "النسخ تُحفظ تلقائياً في مجلد: Backups\\",
    "اطلب منه نسخها إلى USB أو Google Drive",
], bg=GREEN_BG, border=colors.HexColor("#16a34a"))

y = info_box(c, y, "🆘 الدعم الفني", [
    "خصّص رقم WhatsApp للعملاء فقط",
    "وقت الاستجابة المقترح: خلال 24 ساعة",
    "إذا أراد العميل تثبيت على جهاز جديد → ولّد له مفتاحاً جديداً",
    "إذا ظهر خطأ DLL → اطلب منه تشغيل ملف: FIX_WIN7.bat",
], bg=colors.HexColor("#fce7f3"), border=colors.HexColor("#db2777"))

# خلاصة
y -= 0.3 * cm
c.setFillColor(PRIMARY)
c.roundRect(MARGIN, y - 2.2 * cm, PAGE_W - 2 * MARGIN, 2.2 * cm, 10, fill=1, stroke=0)
c.setFillColor(colors.white)
c.setFont("AR-B", 14)
c.drawCentredString(PAGE_W / 2, y - 0.8 * cm, ar("✓  انتهى — هذه كل العملية"))
c.setFont("AR", 11)
c.drawCentredString(PAGE_W / 2, y - 1.5 * cm, ar("7 ملفات → ZIP → نقل → INSTALL → HWID → مفتاح → تفعيل"))

draw_footer(c)
c.showPage()

# ═══════════════════ الصفحة 4 — حل مشكلة DLL ═══════════════════
draw_header(c, 4)
y = PAGE_H - 3.0 * cm

c.setFillColor(colors.HexColor("#dc2626"))
c.rect(0, y - 0.5*cm, PAGE_W, 2.2*cm, fill=1, stroke=0)
c.setFillColor(colors.white)
c.setFont("AR-B", 16)
c.drawRightString(RIGHT, y + 1.2*cm, ar("⚠  حل مشكلة: البرنامج لا يفتح — خطأ DLL"))
c.setFont("AR", 11)
c.drawRightString(RIGHT, y + 0.5*cm, ar("Erreur système — api-ms-win-core-path-l1-1-0.dll"))
y -= 1.5*cm

# وصف المشكلة
y = info_box(c, y, "ما هي المشكلة؟", [
    "تظهر رسالة: 'Impossible de démarrer le programme car il manque",
    "api-ms-win-core-path-l1-1-0.dll'",
    "السبب: جهاز العميل يعمل على Windows 7 أو Windows 10 قديم",
    "بدون تحديثات مايكروسوفت المطلوبة",
], bg=RED_BG, border=colors.HexColor("#dc2626"))

# الحل الأول
y = step_box(c, y, 1, "الحل السريع — تشغيل FIX_WIN7.bat (يحتاج إنترنت)", [
    "1. ابحث عن ملف  FIX_WIN7.bat  داخل مجلد Medanic",
    "2. انقر يمين عليه ← Exécuter en tant qu'administrateur",
    "3. اضغط Exécuter عند رسالة الأمان",
    "4. انتظر دقيقتين حتى ينتهي التحميل والتثبيت",
    "5. أغلق النافذة وافتح برنامج Medanic مجدداً",
], bg=GREEN_BG, badge=colors.HexColor("#16a34a"))

# الحل الثاني
y = step_box(c, y, 2, "الحل البديل — تحديث Windows يدوياً", [
    "1. اذهب إلى: Démarrer ← Paramètres ← Windows Update",
    "2. اضغط: Rechercher des mises à jour",
    "3. ثبّت جميع التحديثات المتاحة وأعد تشغيل الجهاز",
    "4. بعد التحديث افتح Medanic مجدداً",
], bg=colors.HexColor("#dbeafe"), badge=ACCENT)

# تحذير
y -= 0.3*cm
c.setFillColor(colors.HexColor("#fef3c7"))
c.setStrokeColor(colors.HexColor("#d97706"))
c.setLineWidth(1.5)
c.roundRect(MARGIN, y - 1.8*cm, PAGE_W - 2*MARGIN, 1.8*cm, 8, fill=1, stroke=1)
c.setFillColor(colors.HexColor("#92400e"))
c.setFont("AR-B", 11)
c.drawRightString(RIGHT - 0.3*cm, y - 0.6*cm, ar("إذا لم تنجح الحلول — تواصل معنا:"))
c.setFont("AR-B", 13)
c.drawCentredString(PAGE_W / 2, y - 1.3*cm, "WhatsApp:  +213 540 77 28 07")

draw_footer(c)
c.save()
print("✓ Created Medanic_Transfer_Guide.pdf")
