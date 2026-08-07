# -*- coding: utf-8 -*-
"""يولّد دليل الزبون لبرنامج ميدانيك — PDF عربي."""
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

def ar(t):
    return get_display(arabic_reshaper.reshape(t))

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
RIGHT  = PAGE_W - MARGIN

PRIMARY   = colors.HexColor("#1e40af")
ACCENT    = colors.HexColor("#0ea5e9")
DARK      = colors.HexColor("#0f172a")
GRAY      = colors.HexColor("#475569")
LIGHT_BG  = colors.HexColor("#f1f5f9")
GREEN_BG  = colors.HexColor("#dcfce7")
RED_BG    = colors.HexColor("#fee2e2")
YELLOW_BG = colors.HexColor("#fef3c7")
BLUE_BG   = colors.HexColor("#dbeafe")
GREEN_DARK= colors.HexColor("#16a34a")
RED_DARK  = colors.HexColor("#dc2626")
AMBER     = colors.HexColor("#d97706")


def draw_header(c, page_num, subtitle="دليل الاستخدام"):
    c.setFillColor(PRIMARY)
    c.rect(0, PAGE_H - 2.2*cm, PAGE_W, 2.2*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("AR-B", 17)
    c.drawRightString(RIGHT, PAGE_H - 1.35*cm,
                      ar(f"برنامج ميدانيك  —  {subtitle}"))
    c.setFont("AR", 9)
    c.drawString(MARGIN, PAGE_H - 1.35*cm, f"Page {page_num}")

def draw_footer(c):
    c.setFillColor(GRAY)
    c.setFont("AR", 9)
    c.drawCentredString(PAGE_W/2, 1.6*cm,
                        ar("للدعم الفني — تواصل معنا:"))
    c.setFont("AR", 10)
    c.drawCentredString(PAGE_W/2, 1.05*cm,
                        "Tel / WhatsApp:  +213 540 772 807    |    contact@midanic.com")
    c.setFont("AR", 8)
    c.drawCentredString(PAGE_W/2, 0.5*cm,
                        ar("ميدانيك © 2026 — جميع الحقوق محفوظة"))

def section_title(c, y, title):
    c.setFillColor(PRIMARY)
    c.setFont("AR-B", 14)
    c.drawRightString(RIGHT, y, ar(title))
    y -= 0.3*cm
    c.setStrokeColor(ACCENT); c.setLineWidth(1.5)
    c.line(RIGHT, y, RIGHT - 7*cm, y)
    return y - 0.55*cm

def step_box(c, y, num, title, lines, bg=LIGHT_BG, badge=PRIMARY):
    box_h = 1.1*cm + len(lines)*0.6*cm
    c.setFillColor(bg)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2*MARGIN, box_h, 8, fill=1, stroke=0)
    c.setFillColor(badge)
    c.circle(MARGIN + 0.65*cm, y - 0.62*cm, 0.42*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("AR-B", 13)
    c.drawCentredString(MARGIN + 0.65*cm, y - 0.78*cm, str(num))
    c.setFillColor(DARK)
    c.setFont("AR-B", 12)
    c.drawRightString(RIGHT - 0.3*cm, y - 0.78*cm, ar(title))
    ty = y - 1.38*cm
    for line in lines:
        c.setFont("AR", 10.5); c.setFillColor(DARK)
        c.drawRightString(RIGHT - 0.5*cm, ty, ar(line))
        ty -= 0.6*cm
    return y - box_h - 0.32*cm

def info_box(c, y, title, lines, bg, border):
    box_h = 0.9*cm + len(lines)*0.56*cm
    c.setFillColor(bg)
    c.setStrokeColor(border); c.setLineWidth(1.5)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2*MARGIN, box_h, 6, fill=1, stroke=1)
    c.setFillColor(border)
    c.setFont("AR-B", 11)
    c.drawRightString(RIGHT - 0.4*cm, y - 0.62*cm, ar(title))
    c.setFillColor(DARK); c.setFont("AR", 10)
    ty = y - 1.25*cm
    for line in lines:
        c.drawRightString(RIGHT - 0.6*cm, ty, ar(line))
        ty -= 0.56*cm
    return y - box_h - 0.28*cm


# ══════════════════════════════════════════════════════════════════════════
c = canvas.Canvas("Medanic_Client_Guide.pdf", pagesize=A4)


# ════════════════ الصفحة 1 — التثبيت وأول تشغيل ════════════════
draw_header(c, 1, "دليل الاستخدام")
y = PAGE_H - 2.8*cm

# غلاف
c.setFillColor(PRIMARY)
c.setFont("AR-B", 21)
c.drawRightString(RIGHT, y, ar("أهلاً بك في برنامج ميدانيك"))
y -= 0.4*cm
c.setStrokeColor(ACCENT); c.setLineWidth(2)
c.line(RIGHT, y, MARGIN, y)
y -= 0.5*cm
c.setFillColor(GRAY); c.setFont("AR", 11)
c.drawRightString(RIGHT, y, ar("نظام إدارة مدرسة تعليم السياقة — الجزائر"))
y -= 0.8*cm

y = section_title(c, y, "تثبيت البرنامج وإنشاء الاختصار")

y = step_box(c, y, 1, "ضع ملف Medanic.exe في مجلد ثابت", [
    "أنشئ مجلداً على سطح المكتب أو في C:\\ اسمه: Medanic",
    "انقل Medanic.exe إلى داخل هذا المجلد",
    "⚠  لا تشغّل البرنامج مباشرةً من USB أو مجلد مؤقت",
])
y = step_box(c, y, 2, "شغّل CLIENT_INSTALL.bat لإنشاء الاختصار", [
    "انقل CLIENT_INSTALL.bat إلى نفس مجلد Medanic.exe",
    "انقر مرتين على CLIENT_INSTALL.bat",
    "ستظهر أيقونة ميدانيك على سطح المكتب مباشرةً",
], bg=GREEN_BG, badge=GREEN_DARK)
y = step_box(c, y, 3, "افتح البرنامج من أيقونة سطح المكتب", [
    "انقر مرتين على أيقونة ميدانيك",
    "في أول تشغيل: يعمل البرنامج مجاناً لمدة 30 يوماً (فترة التجربة)",
    "يظهر في عنوان النافذة:  ⏳ التجربة: 30ي 00س 00د متبقية",
])

y -= 0.1*cm
y = info_box(c, y, "✅  البرنامج جاهز للاستخدام الفوري", [
    "لا تحتاج تثبيت Python أو أي برنامج آخر",
    "قاعدة البيانات تُحفظ تلقائياً في AppData\\Local\\Medanic",
], bg=GREEN_BG, border=GREEN_DARK)

draw_footer(c)
c.showPage()


# ════════════════ الصفحة 2 — التفعيل ════════════════
draw_header(c, 2, "تفعيل البرنامج")
y = PAGE_H - 2.8*cm

y = info_box(c, y, "⏳  فترة التجربة المجانية — 30 يوماً", [
    "يعمل البرنامج بكامل مميزاته خلال فترة التجربة",
    "العداد يظهر في عنوان النافذة ويتحدّث كل دقيقة",
    "بعد 30 يوماً تظهر نافذة التفعيل — لا تُغلقها قبل القراءة",
], bg=YELLOW_BG, border=AMBER)

y -= 0.2*cm
y = section_title(c, y, "خطوات التفعيل الدائم")

y = step_box(c, y, 1, "انسخ رمز HWID من نافذة التفعيل", [
    "عند انتهاء 30 يوماً تظهر نافذة تفعيل تلقائياً",
    "ستجد رمزاً مكوّناً من 16 حرف — هذا هو (معرّف جهازك)",
    "اضغط زر (نسخ HWID) لنسخه بشكل صحيح",
])
y = step_box(c, y, 2, "أرسل رمز HWID للمطوّر عبر WhatsApp", [
    "أرسل الرمز على الرقم:  +213 540 772 807",
    "أو عبر الإيميل:  contact@midanic.com",
    "مثال: HWID: A3F7C2D1B8E04591",
], bg=BLUE_BG, badge=ACCENT)
y = step_box(c, y, 3, "استلم مفتاح التفعيل وأدخله", [
    "ستستلم مفتاحاً بصيغة:  XXXXX-XXXXX-XXXXX-XXXXX",
    "الصقه في خانة (مفتاح التفعيل) في النافذة",
    "اضغط زر (تفعيل) ← البرنامج يفتح مباشرةً",
], bg=GREEN_BG, badge=GREEN_DARK)

y -= 0.1*cm
y = info_box(c, y, "🔒  المفتاح مرتبط بجهازك", [
    "المفتاح يعمل للأبد على هذا الجهاز — لا تحتاج تجديد",
    "إذا غيّرت جهازاً جديداً → تواصل معنا للحصول على مفتاح جديد",
    "لا تنسخ البرنامج لجهاز آخر — المفتاح لن يعمل",
], bg=YELLOW_BG, border=AMBER)

draw_footer(c)
c.showPage()


# ════════════════ الصفحة 3 — النسخ الاحتياطي والاستعادة ════════════════
draw_header(c, 3, "النسخ الاحتياطي والاستعادة")
y = PAGE_H - 2.8*cm

y = info_box(c, y, "💡  لماذا النسخ الاحتياطي مهم؟", [
    "قاعدة بياناتك تحتوي على كل معلومات مدرستك",
    "عطل في الجهاز أو فيروس قد يمسح كل شيء",
    "احرص على نسخة احتياطية أسبوعية على USB أو Google Drive",
], bg=BLUE_BG, border=ACCENT)

y -= 0.2*cm
y = section_title(c, y, "نسخ احتياطي — BACKUP.bat")

y = step_box(c, y, 1, "شغّل BACKUP.bat", [
    "انقر مرتين على ملف BACKUP.bat في مجلد البرنامج",
    "تأكد أن البرنامج (Medanic) مغلق أولاً",
    "ستظهر نافذة سوداء وتنتهي خلال ثوانٍ",
])
y = step_box(c, y, 2, "النسخة محفوظة تلقائياً", [
    "النسخ تُحفظ في مجلد: Backups\\ داخل مجلد البرنامج",
    "كل نسخة باسم يحتوي التاريخ والوقت تلقائياً",
    "مثال: driving_school_2026-05-17_14h30.db",
], bg=GREEN_BG, badge=GREEN_DARK)
y = step_box(c, y, 3, "انقل النسخة لمكان آمن", [
    "انسخ مجلد Backups\\ إلى USB أو Google Drive",
    "هذا يضمن بقاء بياناتك حتى لو تعطّل الجهاز",
])

y -= 0.3*cm
y = section_title(c, y, "استعادة البيانات — RESTORE.bat")

y = step_box(c, y, 1, "شغّل RESTORE.bat", [
    "انقر مرتين على RESTORE.bat (البرنامج يجب أن يكون مغلقاً)",
    "ستظهر قائمة بكل النسخ الاحتياطية المتوفرة",
])
y = step_box(c, y, 2, "اختر النسخة المطلوبة", [
    "اكتب اسم النسخة كاملاً كما يظهر في القائمة",
    "مثال:  driving_school_2026-05-17_14h30.db",
    "اضغط Enter ← ستتم الاستعادة تلقائياً",
], bg=YELLOW_BG, badge=AMBER)
y = info_box(c, y, "⚠  تنبيه قبل الاستعادة", [
    "الاستعادة ستستبدل البيانات الحالية بالنسخة القديمة",
    "تأكد من اختيار النسخة الصحيحة قبل المتابعة",
    "البرنامج يحفظ نسخة من الوضع الحالي تلقائياً قبل الاستعادة",
], bg=RED_BG, border=RED_DARK)

draw_footer(c)
c.showPage()


# ════════════════ الصفحة 4 — المشاكل الشائعة ════════════════
draw_header(c, 4, "حل المشاكل الشائعة")
y = PAGE_H - 2.8*cm

y = info_box(c, y, "❌  البرنامج لا يفتح — خطأ في النظام (DLL)", [
    "السبب: نقص مكتبات النظام (VC++ Runtime)",
    "الحل:",
    "  1. شغّل FIX_WIN7.bat (انقر يمين ← تشغيل كمسؤول)",
    "  2. انتظر دقيقتين للتحميل التلقائي",
    "  3. أغلق النافذة وافتح ميدانيك مجدداً",
    "  ⚠  يحتاج اتصال بالإنترنت",
], bg=RED_BG, border=RED_DARK)

y = info_box(c, y, "❌  البرنامج يفتح لكن البيانات غير موجودة", [
    "قاعدة البيانات موجودة في: %LOCALAPPDATA%\\Medanic\\driving_school.db",
    "لا حاجة لنقل قاعدة البيانات عند تحديث Medanic.exe",
    "إذا فقدت البيانات → استخدم RESTORE.bat لاسترجاع نسخة احتياطية",
], bg=YELLOW_BG, border=AMBER)

y = info_box(c, y, "❌  أيقونة سطح المكتب لا تعمل", [
    "شغّل CLIENT_INSTALL.bat مرة أخرى من مجلد البرنامج",
    "تأكد أن Medanic.exe موجود في نفس المجلد",
], bg=LIGHT_BG, border=GRAY)

y = info_box(c, y, "❌  نسيت كلمة مرور الدخول", [
    "تواصل مع المطوّر على الرقم:  +213 540 772 807",
    "سيتم إعادة تعيين كلمة المرور خلال دقائق",
], bg=LIGHT_BG, border=GRAY)

# بطاقة الدعم
y -= 0.3*cm
c.setFillColor(PRIMARY)
c.roundRect(MARGIN, y - 3.2*cm, PAGE_W - 2*MARGIN, 3.2*cm, 10, fill=1, stroke=0)
c.setFillColor(colors.white)
c.setFont("AR-B", 15)
c.drawCentredString(PAGE_W/2, y - 0.7*cm,  ar("📞  الدعم الفني — ميدانيك"))
c.setFont("AR", 11)
c.drawCentredString(PAGE_W/2, y - 1.35*cm, ar("نحن هنا لمساعدتك في أي وقت"))
c.setFont("AR-B", 13)
c.drawCentredString(PAGE_W/2, y - 2.0*cm,  "WhatsApp:  +213 540 772 807")
c.setFont("AR", 11)
c.drawCentredString(PAGE_W/2, y - 2.65*cm, "Email:  contact@midanic.com")

draw_footer(c)
c.showPage()

c.save()
print("OK: Medanic_Client_Guide.pdf")
