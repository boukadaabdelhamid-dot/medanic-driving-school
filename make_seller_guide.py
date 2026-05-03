#!/usr/bin/env python3
"""Generate Arabic seller guide PDF for Medanic distribution."""
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

GOLD = HexColor("#D4A574")
DARK = HexColor("#1A1A2E")
BLUE = HexColor("#16213E")
LIGHT = HexColor("#F5F5F5")
GREEN = HexColor("#27AE60")
RED = HexColor("#E74C3C")

def ar(txt):
    return get_display(arabic_reshaper.reshape(txt))

W, H = A4

def draw_header(c, page_num, total, title):
    c.setFillColor(DARK)
    c.rect(0, H - 2.5*cm, W, 2.5*cm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("DejaVu-Bold", 18)
    c.drawRightString(W - 1*cm, H - 1.2*cm, ar("دليل البائع — برنامج ميدانيك"))
    c.setFillColor(white)
    c.setFont("DejaVu", 11)
    c.drawRightString(W - 1*cm, H - 2*cm, ar(title))
    c.setFont("DejaVu", 9)
    c.drawString(1*cm, H - 2*cm, f"Page {page_num} / {total}")

def draw_footer(c):
    c.setFillColor(GOLD)
    c.rect(0, 0, W, 0.6*cm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("DejaVu-Bold", 9)
    c.drawCentredString(W/2, 0.2*cm, ar("ميدانيك © 2026 - سري - للبائع فقط"))

def section(c, y, num, txt, color=BLUE):
    c.setFillColor(color)
    c.roundRect(1*cm, y - 0.6*cm, W - 2*cm, 1*cm, 0.2*cm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("DejaVu-Bold", 13)
    c.drawRightString(W - 1.3*cm, y - 0.3*cm, ar(f"{num}. {txt}"))
    return y - 1.5*cm

def line(c, y, txt, size=11, bold=False, color=black, indent=1.5):
    c.setFillColor(color)
    c.setFont("DejaVu-Bold" if bold else "DejaVu", size)
    c.drawRightString(W - indent*cm, y, ar(txt))
    return y - 0.55*cm

def bullet(c, y, txt, color=black):
    c.setFillColor(GOLD)
    c.setFont("DejaVu-Bold", 11)
    c.drawRightString(W - 1.5*cm, y, "◆")
    c.setFillColor(color)
    c.setFont("DejaVu", 10.5)
    c.drawRightString(W - 2*cm, y, ar(txt))
    return y - 0.5*cm

def warn_box(c, y, lines, color=RED):
    h = 0.5*cm + len(lines)*0.55*cm
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.roundRect(1*cm, y - h, W - 2*cm, h, 0.15*cm, fill=0, stroke=1)
    c.setFillColor(color)
    c.rect(W - 1.3*cm, y - h, 0.3*cm, h, fill=1, stroke=0)
    yy = y - 0.4*cm
    for ln in lines:
        c.setFillColor(color)
        c.setFont("DejaVu-Bold" if ln.startswith("!") else "DejaVu", 10.5)
        c.drawRightString(W - 1.7*cm, yy, ar(ln.lstrip("! ")))
        yy -= 0.55*cm
    return y - h - 0.3*cm

def good_box(c, y, lines):
    return warn_box(c, y, lines, color=GREEN)

# =========================================
TOTAL = 4
c = canvas.Canvas("Medanic_Seller_Guide.pdf", pagesize=A4)

# === PAGE 1: COVER ===
c.setFillColor(DARK)
c.rect(0, 0, W, H, fill=1, stroke=0)

c.setFillColor(GOLD)
c.rect(0, H/2 + 4*cm, W, 0.15*cm, fill=1, stroke=0)
c.rect(0, H/2 - 5*cm, W, 0.15*cm, fill=1, stroke=0)

c.setFillColor(GOLD)
c.setFont("DejaVu-Bold", 36)
c.drawCentredString(W/2, H/2 + 2.5*cm, ar("ميدانيك"))
c.setFillColor(white)
c.setFont("DejaVu", 18)
c.drawCentredString(W/2, H/2 + 1.5*cm, "MEDANIC")

c.setFillColor(GOLD)
c.setFont("DejaVu-Bold", 22)
c.drawCentredString(W/2, H/2 - 0.5*cm, ar("دليل البائع الرسمي"))
c.setFillColor(white)
c.setFont("DejaVu", 14)
c.drawCentredString(W/2, H/2 - 1.5*cm, ar("كيف تبني وتبيع البرنامج لمدارس تعليم السياقة"))

c.setFillColor(GOLD)
c.setFont("DejaVu", 12)
c.drawCentredString(W/2, H/2 - 6*cm, ar("⚠ مستند سري — للبائع فقط — لا توزّعه على العملاء"))

c.setFillColor(white)
c.setFont("DejaVu", 10)
c.drawCentredString(W/2, 2*cm, ar("الإصدار 1.0 — 2026"))
c.showPage()

# === PAGE 2: BUILD ===
draw_header(c, 2, TOTAL, "بناء ملف EXE")
y = H - 3.5*cm

y = section(c, y, "1", "بناء البرنامج (مرة واحدة فقط)")
y = line(c, y, "في مجلد البرنامج على جهازك:", bold=True)
y -= 0.2*cm
y = bullet(c, y, "C:\\Users\\DELL\\Desktop\\midanic_driving_school\\")
y -= 0.3*cm

y = line(c, y, "ضع الملفات التالية:", bold=True, color=BLUE)
y = bullet(c, y, "BUILD_EXE.bat  (سكريبت البناء)")
y = bullet(c, y, "driving_school_single.py  (الكود الرئيسي)")
y = bullet(c, y, "license_guard.py  (نظام الحماية)")
y = bullet(c, y, "medanic_icon.ico + medanic_logo.png  (الشعار)")
y -= 0.3*cm

y = line(c, y, "الخطوات:", bold=True, color=BLUE)
y = bullet(c, y, "1) انقر مرتين على BUILD_EXE.bat")
y = bullet(c, y, "2) اضغط Enter عند كل توقف")
y = bullet(c, y, "3) انتظر 5-7 دقائق")
y = bullet(c, y, "4) ستجد الملف في:  dist\\Medanic.exe")
y -= 0.4*cm

y = good_box(c, y, [
    "! النتيجة:",
    "ملف Medanic.exe جاهز (حوالي 35 MB)",
    "محمي بالكامل — لا يكشف الكود المصدري",
    "لا يحتاج Python على جهاز العميل",
])

draw_footer(c)
c.showPage()

# === PAGE 3: PACKAGE FOR CLIENT ===
draw_header(c, 3, TOTAL, "تجهيز نسخة العميل")
y = H - 3.5*cm

y = section(c, y, "2", "تحضير الحزمة للعميل")
y = line(c, y, "أنشئ مجلداً جديداً باسم:  Medanic_Client", bold=True)
y -= 0.2*cm

y = line(c, y, "ضع بداخله هذه الملفات فقط:", bold=True, color=GREEN)
y = bullet(c, y, "Medanic.exe  (من مجلد dist)", color=GREEN)
y = bullet(c, y, "CLIENT_INSTALL.bat  (لإنشاء اختصار سطح المكتب)", color=GREEN)
y = bullet(c, y, "BACKUP.bat  (للنسخ الاحتياطي)", color=GREEN)
y = bullet(c, y, "RESTORE.bat  (لاستعادة النسخ)", color=GREEN)
y = bullet(c, y, "Medanic_Transfer_Guide.pdf  (دليل العميل)", color=GREEN)
y -= 0.3*cm

y = warn_box(c, y, [
    "! ⚠ ممنوع منعاً باتاً إرسال هذه الملفات للعميل:",
    "✗ keygen_tool.py  →  سري! يولّد المفاتيح",
    "✗ license_guard.py  →  يكشف نظام الحماية",
    "✗ driving_school_single.py  →  الكود المصدري",
    "✗ BUILD_EXE.bat  →  خاص بك فقط",
])
y -= 0.3*cm

y = section(c, y, "3", "ضغط وإرسال")
y = bullet(c, y, "انقر يمين على المجلد ← Envoyer vers ← Dossier compressé")
y = bullet(c, y, "ستحصل على Medanic_Client.zip")
y = bullet(c, y, "أرسلها للعميل عبر WhatsApp / Email / Google Drive")

draw_footer(c)
c.showPage()

# === PAGE 4: ACTIVATION & SALES ===
draw_header(c, 4, TOTAL, "التفعيل والبيع")
y = H - 3.5*cm

y = section(c, y, "4", "خطوات التفعيل (مع العميل)")

y = line(c, y, "العميل يقوم بـ:", bold=True, color=BLUE)
y = bullet(c, y, "1) فك ضغط Medanic_Client.zip")
y = bullet(c, y, "2) تشغيل CLIENT_INSTALL.bat (اختصار سطح المكتب)")
y = bullet(c, y, "3) فتح البرنامج → سيظهر له HWID فريد لجهازه")
y = bullet(c, y, "4) إرسال HWID لك + إثبات الدفع 💰")
y -= 0.3*cm

y = line(c, y, "أنت تقوم بـ:", bold=True, color=GREEN)
y = bullet(c, y, "1) فتح keygen_tool.py على جهازك", color=GREEN)
y = bullet(c, y, "2) إدخال HWID الذي أرسله العميل", color=GREEN)
y = bullet(c, y, "3) نسخ المفتاح المُولَّد (XXXXX-XXXXX-XXXXX-XXXXX)", color=GREEN)
y = bullet(c, y, "4) إرسال المفتاح للعميل", color=GREEN)
y -= 0.2*cm

y = good_box(c, y, [
    "! ✓ الحماية المضمونة:",
    "المفتاح يعمل على جهاز العميل فقط",
    "لو نسخ البرنامج لجهاز آخر → يطلب مفتاح جديد",
    "لا يمكن تخمين المفاتيح أو توليدها بدون السر",
])
y -= 0.3*cm

y = section(c, y, "5", "نصائح للبيع التجاري", color=GOLD)
y = bullet(c, y, "احتفظ بسجل: اسم العميل + HWID + المفتاح + التاريخ + المبلغ")
y = bullet(c, y, "اطلب الدفع كاملاً قبل إرسال المفتاح")
y = bullet(c, y, "لا تشارك keygen_tool.py مع أي شخص أبداً")
y = bullet(c, y, "اعمل نسخة احتياطية من keygen_tool.py على USB آمن")

draw_footer(c)
c.showPage()

c.save()
print("OK: Medanic_Seller_Guide.pdf")
