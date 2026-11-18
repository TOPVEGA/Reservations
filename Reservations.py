
# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025


import os
import json
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import string
import re

API_ID = 8186557
API_HASH = "efd77b34c69c164ce158037ff5a0d117"
BOT_TOKEN = " "
ADMIN_ID = 
VEGA = "TOPVEGA"

METHODS = {
    "phone": "📱 رقم الهاتف: +1234567890",
    "bank": "🏦 الحساب البنكي: IBAN: XX1234567890",
    "crypto": "💰 محفظة العملات الرقمية: 0x1234567890abcdef",
    "telegram_stars": f"⭐ نجوم تليجرام: @{VEGA}"
}

TUTX = {"start": 9, "end": 20}
SLOT = 30
DAYS = [0, 1, 2, 3, 4, 5, 6]

# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025

DATA_DB = "reservations.json"
_data_cache = {"data": None, "mtime": 0}

def load_data():
    if os.path.exists(DATA_DB):
        try:
            mtime = os.path.getmtime(DATA_DB)
            if _data_cache["data"] is not None and _data_cache["mtime"] == mtime:
                return _data_cache["data"]
            with open(DATA_DB, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "pending_reservations" not in data:
                    data["pending_reservations"] = []
                if "transactions" not in data:
                    data["transactions"] = []
                if "METHODS" not in data:
                    data["METHODS"] = METHODS
                if "services" not in data:
                    data["services"] = [
                        {"name": "طبية", "price": 100, "duration": 30},
                        {"name": "تجميل", "price": 80, "duration": 45},
                        {"name": "صيانة", "price": 150, "duration": 60},
                        {"name": "قانونية", "price": 200, "duration": 30},
                        {"name": "مالية", "price": 180, "duration": 45}
                    ]
                if "employees" not in data:
                    data["employees"] = [
                        {"id": 1, "name": "دكتور أحمد", "specialty": "أسنان", "available": True},
                        {"id": 2, "name": "دكتور سارة", "specialty": "جلدية", "available": True},
                        {"id": 3, "name": "دكتور خالد", "specialty": "عظام", "available": True}
                    ]
                if "settings" not in data:
                    data["settings"] = {
                        "working_hours": TUTX,
                        "slot_duration": SLOT,
                        "working_days": DAYS
                    }
                _data_cache["data"] = data
                _data_cache["mtime"] = mtime
                return data
        except Exception as e:
            print(f"خطأ في تحميل البيانات: {e}")
    
    return {
        "reservations": [],
        "pending_reservations": [],
        "next_id": 1,
        "employees": [
            {"id": 1, "name": "دكتور أحمد", "specialty": "أسنان", "available": True},
            {"id": 2, "name": "دكتور سارة", "specialty": "جلدية", "available": True},
            {"id": 3, "name": "دكتور خالد", "specialty": "عظام", "available": True}
        ],
        "reviews": [],
        "loyalty_points": {},
        "admin_ids": [ADMIN_ID],
        "holidays": [],
        "services": [
            {"name": "طبية", "price": 100, "duration": 30},
            {"name": "تجميل", "price": 80, "duration": 45},
            {"name": "صيانة", "price": 150, "duration": 60},
            {"name": "قانونية", "price": 200, "duration": 30},
            {"name": "مالية", "price": 180, "duration": 45}
        ],
        "settings": {
            "working_hours": TUTX,
            "slot_duration": SLOT,
            "working_days": DAYS
        },
        "METHODS": METHODS,
        "transactions": []
    }

def save_data(data):
    try:
        with open(DATA_DB, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        _data_cache["data"] = data
        _data_cache["mtime"] = os.path.getmtime(DATA_DB)
        return True
    except Exception as e:
        print(f"خطأ في حفظ البيانات: {e}")
        return False

def format_time_12h(time_str):
    try:
        hour, minute = map(int, time_str.split(':'))
        period = "ص" if hour < 12 else "م"
        hour = hour % 12
        if hour == 0:
            hour = 12
        return f"{hour}:{minute:02d} {period}"
    except:
        return time_str

def format_arabic_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
                     "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        return f"{days_ar[date_obj.weekday()]} {date_obj.day} {months_ar[date_obj.month-1]} {date_obj.year}"
    except:
        return date_str

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def get_available_slots(date, employee_id=None):
    data = load_data()
    settings = data.get("settings", {})
    working_hours = settings.get("working_hours", TUTX)
    slot_duration = settings.get("slot_duration", SLOT)
    working_days = settings.get("working_days", DAYS)
    
    try:
        day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()
    except:
        return []
    
    if day_of_week not in working_days:
        return []
    
    for holiday in data.get("holidays", []):
        if holiday == date:
            return []
    
    kim = []
    current_time = datetime.strptime(f"{date} {working_hours['start']:02d}:00", "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(f"{date} {working_hours['end']:02d}:00", "%Y-%m-%d %H:%M")
    
    while current_time < end_time:
        kim.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=slot_duration)
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    if date == today_str:
        kim = [s for s in kim if datetime.strptime(f"{date} {s}", "%Y-%m-%d %H:%M") > now]
    
    booked_slots = []
    for res in data["reservations"]:
        if res["date"] == date and res["status"] in ["confirmed", "pending"]:
            if employee_id is None or res.get("employee_id") == employee_id:
                booked_slots.append(res["time"])
    
    return [slot for slot in kim if slot not in booked_slots]

def get_next_available_days(days=7, employee_id=None):
    available_days = []
    today = datetime.now().date()
    for i in range(days):
        date = today + timedelta(days=i)
        slots = get_available_slots(date.strftime("%Y-%m-%d"), employee_id)
        if slots:
            available_days.append(date.strftime("%Y-%m-%d"))
    return available_days

def get_service_price(service_name):
    data = load_data()
    for service in data["services"]:
        if service["name"] == service_name:
            return service["price"]
    return 0

app = Client("reservation_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_sessions = {}
admin_sessions = {}

def get_main_keyboard(is_admin=False):
    keyboard = [
        [InlineKeyboardButton("📅 حجز موعد", callback_data="new_booking")],
        [InlineKeyboardButton("📋 حجوزاتي", callback_data="my_bookings")],
        [InlineKeyboardButton("⭐ تقييم الخدمة", callback_data="rate_service")],
        [InlineKeyboardButton("💰 نقاط الولاء", callback_data="loyalty_points")],
        [InlineKeyboardButton("❌ إلغاء حجز", callback_data="cancel_booking")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def get_days_keyboard(days, employee_id=None):
    keyboard = []
    for day in days:
        formatted = format_arabic_date(day)
        callback = f"day_{day}"
        if employee_id:
            callback += f"_{employee_id}"
        keyboard.append([InlineKeyboardButton(formatted, callback_data=callback)])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def get_slots_keyboard(slots, date, employee_id=None):
    keyboard = []
    row = []
    for slot in slots:
        time_12h = format_time_12h(slot)
        callback = f"time_{date}_{slot}"
        if employee_id:
            callback += f"_{employee_id}"
        row.append(InlineKeyboardButton(time_12h, callback_data=callback))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_days")])
    return InlineKeyboardMarkup(keyboard)

def get_services_keyboard():
    data = load_data()
    keyboard = []
    for service in data["services"]:
        keyboard.append([InlineKeyboardButton(
            f"🦷 {service['name']} - ${service['price']} ({service['duration']}د)",
            callback_data=f"service_{service['name']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def get_employees_keyboard(service=None):
    data = load_data()
    if not data.get("employees"):
        return None
    keyboard = []
    for emp in data["employees"]:
        if emp.get("available", True):
            callback = f"emp_{emp['id']}"
            if service:
                callback += f"_{service}"
            keyboard.append([InlineKeyboardButton(
                f"👨‍⚕️ {emp['name']} - {emp['specialty']}",
                callback_data=callback
            )])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_services")])
    return InlineKeyboardMarkup(keyboard)

def get_payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 دفع الآن عبر الإنترنت", callback_data="pay_now")],
        [InlineKeyboardButton("💰 دفع عند الموعد", callback_data="pay_later")],
        [InlineKeyboardButton(f"⭐ دفع عبر نجوم تليجرام @{VEGA}", callback_data="pay_stars")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])

def get_otp_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 أدخل رمز التحقق", callback_data="enter_otp")],
        [InlineKeyboardButton("🔄 إعادة إرسال الرمز", callback_data="resend_otp")],
        [InlineKeyboardButton("🔙 إلغاء", callback_data="back_main")]
    ])

def get_admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍⚕️ إدارة الموظفين", callback_data="admin_employees")],
        [InlineKeyboardButton("📅 إدارة المواعيد", callback_data="admin_slots")],
        [InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="admin_settings")],
        [InlineKeyboardButton("📊 الحجوزات المعلقة", callback_data="admin_pending")],
        [InlineKeyboardButton("📋 جميع الحجوزات", callback_data="admin_all_bookings")],
        [InlineKeyboardButton("💰 إدارة الدفع", callback_data="admin_payment")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])

def get_employee_management_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة موظف", callback_data="admin_add_employee")],
        [InlineKeyboardButton("✏️ تعديل موظف", callback_data="admin_edit_employee")],
        [InlineKeyboardButton("🗑️ حذف موظف", callback_data="admin_delete_employee")],
        [InlineKeyboardButton("👥 عرض الموظفين", callback_data="admin_view_employees")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ])

def get_settings_keyboard():
    data = load_data()
    settings = data.get("settings", {})
    working_hours = settings.get("working_hours", TUTX)
    working_days = settings.get("working_days", DAYS)
    slot_duration = settings.get("slot_duration", SLOT)
    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    days_text = ", ".join([days_ar[d] for d in working_days])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🕐 وقت البدء: {working_hours['start']}:00", callback_data="admin_set_start")],
        [InlineKeyboardButton(f"🕐 وقت الانتهاء: {working_hours['end']}:00", callback_data="admin_set_end")],
        [InlineKeyboardButton(f"⏱️ مدة الحجز: {slot_duration} دقيقة", callback_data="admin_set_duration")],
        [InlineKeyboardButton(f"📅 أيام العمل: {days_text}", callback_data="admin_set_days")],
        [InlineKeyboardButton("📅 إدارة الإجازات", callback_data="admin_holidays")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ])

def get_payment_management_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 تحديث رقم الهاتف", callback_data="admin_update_phone")],
        [InlineKeyboardButton("🏦 تحديث الحساب البنكي", callback_data="admin_update_bank")],
        [InlineKeyboardButton("💰 تحديث محفظة العملات", callback_data="admin_update_crypto")],
        [InlineKeyboardButton(f"⭐ تحديث نجوم تليجرام @{VEGA}", callback_data="admin_update_stars")],
        [InlineKeyboardButton("📊 عرض المعاملات", callback_data="admin_transactions")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ])

def get_my_bookings_keyboard(bookings):
    keyboard = []
    for booking in bookings:
        text = f"📅 {booking['date']} - {booking['time']} ({booking['service']})"
        if booking.get('employee_name'):
            text += f" - {booking['employee_name']}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"view_{booking['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def get_cancel_bookings_keyboard(bookings):
    keyboard = []
    for booking in bookings:
        text = f"📅 {booking['date']} - {booking['time']} ({booking['service']})"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"cancel_{booking['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def get_rating_keyboard(reservation_id):
    keyboard = []
    for i in range(1, 6):
        stars = "⭐" * i
        keyboard.append([InlineKeyboardButton(stars, callback_data=f"rate_{reservation_id}_{i}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

async def notify_admin(message, reply_markup=None, parse_mode=ParseMode.MARKDOWN):
    try:
        if reply_markup:
            await app.send_message(ADMIN_ID, message, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            await app.send_message(ADMIN_ID, message, parse_mode=parse_mode)
    except Exception as e:
        print(f"خطأ في إرسال إشعار للمالك: {e}")

async def send_pending_reservation_to_admin(reservation):
    formatted_date = format_arabic_date(reservation["date"])
    time_12h = format_time_12h(reservation["time"])
    price = get_service_price(reservation["service"])
    METHODS = {"now": "💳 دفع الآن", "later": "💰 دفع عند الموعد", "stars": f"⭐ نجوم تليجرام @{VEGA}"}
    text = f"""
📋 **طلب حجز جديد - في انتظار الموافقة**

📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {reservation['service']}
💰 السعر: ${price}
👤 المستخدم: {reservation['username']}
🆔 المستخدم: `{reservation['user_id']}`
{f'👨‍⚕️ الموظف: {reservation["employee_name"]}' if reservation.get("employee_name") else ''}
📋 رقم الطلب: #{reservation['id']}
💳 طريقة الدفع: {METHODS.get(reservation.get('payment_method', 'later'), 'لم يتم التحديد')}
⚠️ **يرجى الموافقة أو الرفض**
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ موافقة", callback_data=f"admin_approve_{reservation['id']}")],
        [InlineKeyboardButton("❌ رفض", callback_data=f"admin_reject_{reservation['id']}")]
    ])
    await notify_admin(text, keyboard)

async def send_payment_details(user_id, reservation_id, payment_method):
    data = load_data()
    METHODS = data.get("METHODS", METHODS)
    reservation = None
    for res in data["reservations"]:
        if res["id"] == reservation_id:
            reservation = res
            break
    if not reservation:
        return
    formatted_date = format_arabic_date(reservation["date"])
    time_12h = format_time_12h(reservation["time"])
    price = get_service_price(reservation["service"])
    try:
        if payment_method == "now":
            text = f"""
💳 **تفاصيل الدفع الإلكتروني**
📋 رقم الحجز: #{reservation_id}
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {reservation['service']}
💰 المبلغ: ${price}
📱 **طرق الدفع المتاحة:**
{METHODS.get('phone', '📱 رقم الهاتف: غير متوفر')}
🏦 **الحساب البنكي:**
{METHODS.get('bank', '🏦 غير متوفر')}
💰 **محفظة العملات الرقمية:**
{METHODS.get('crypto', '💰 غير متوفر')}
⭐ **نجوم تليجرام:**
{METHODS.get('telegram_stars', '⭐ غير متوفر')}
⚠️ **يرجى إرسال إثبات الدفع إلى الإدارة**
📱 تواصل معنا: @support
"""
            await app.send_message(user_id, text, parse_mode=ParseMode.MARKDOWN)
        elif payment_method == "later":
            text = f"""
💰 **سيتم الدفع عند الموعد**
📋 رقم الحجز: #{reservation_id}
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {reservation['service']}
💰 المبلغ: ${price}
✅ تم تأكيد حجزك وسيتم الدفع عند حضورك للموعد.
📱 **طرق الدفع المتاحة عند الحضور:**
• نقداً
• بطاقة ائتمان
• تحويل بنكي
شكراً لثقتك! 🤝
"""
            await app.send_message(user_id, text, parse_mode=ParseMode.MARKDOWN)
        elif payment_method == "stars":
            text = f"""
⭐ **الدفع عبر نجوم تليجرام**
📋 رقم الحجز: #{reservation_id}
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {reservation['service']}
💰 المبلغ: ${price}
📱 **كيفية الدفع عبر نجوم تليجرام:**
1. افتح حسابك على تليجرام
2. اذهب إلى الإعدادات > Telegram Stars
3. قم بشراء النجوم المطلوبة (${price} = {price * 10} نجمة تقريباً)
4. أرسل النجوم إلى: @{VEGA}
⚠️ **يرجى إرسال إثبات الدفع (صورة) إلى الإدارة**
📱 تواصل معنا: @support
💡 **ملاحظة:** سيتم إضافة 5 نقاط ولاء إضافية عند الدفع عبر نجوم تليجرام!
"""
            await app.send_message(user_id, text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"خطأ في إرسال تفاصيل الدفع: {e}")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    is_admin = user_id == ADMIN_ID
    welcome_text = """
🌟 **مرحباً بك في بوت حجز المواعيد المتقدم!** 🌟
يمكنك استخدام هذا البوت لحجز موعد مع خدماتنا بكل سهولة.
📌 **الخدمات المتاحة:**
• استشارات طبية
• صالون تجميل
• صيانة وإصلاح
• استشارات قانونية
• استشارات مالية
🕐 **أوقات العمل:** من 9 صباحاً إلى 8 مساءً
⏰ **مدة الحجز:** 30 دقيقة
🎁 **مميزات البوت:**
• نقاط ولاء وخصومات تصل إلى 20%
• تقييم الخدمات
• اختيار الموظف المناسب
• تذكير قبل الموعد بساعة
• دفع إلكتروني أو عند الموعد
• دفع عبر نجوم تليجرام
اختر الخدمة التي ترغب بها من الأزرار أدناه:
"""
    await message.reply_text(welcome_text, reply_markup=get_main_keyboard(is_admin), parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
ℹ️ **كيفية استخدام البوت:**
1️⃣ اضغط على "📅 حجز موعد"
2️⃣ اختر الخدمة المطلوبة
3️⃣ اختر الموظف المناسب (اختياري)
4️⃣ اختر اليوم المناسب
5️⃣ اختر الوقت المتاح
6️⃣ اختر طريقة الدفع
7️⃣ اضغط على "أدخل رمز التحقق"
8️⃣ أرسل الرمز الذي يظهر لك في رسالة للبوت
9️⃣ انتظر موافقة المالك على الحجز
🔟 سيتم تأكيد الحجز بعد الموافقة
"""
    await message.reply_text(help_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]), parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def handle_otp_input(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    if user_id not in user_sessions or user_sessions[user_id].get("state") != "waiting_otp":
        return
    session = user_sessions[user_id]
    expected_otp = session.get("otp")
    reservation_data = session.get("reservation_data")
    if not expected_otp or not reservation_data:
        await message.reply_text("❌ انتهت صلاحية الجلسة، يرجى المحاولة مرة أخرى.")
        return
    if text == expected_otp:
        data = load_data()
        for r in data["reservations"]:
            if (r["date"] == reservation_data["date"] and r["time"] == reservation_data["time"]
                    and r.get("employee_id") == reservation_data.get("employee_id")
                    and r["status"] in ["pending", "confirmed"]):
                await message.reply_text("❌ هذا الموعد تم حجزه للتو، يرجى اختيار موعد آخر.")
                del user_sessions[user_id]
                return
        reservation = {
            "id": data["next_id"],
            "user_id": user_id,
            "username": message.from_user.username or message.from_user.first_name,
            "date": reservation_data["date"],
            "time": reservation_data["time"],
            "service": reservation_data["service"],
            "employee_id": reservation_data.get("employee_id"),
            "employee_name": reservation_data.get("employee_name"),
            "status": "pending",
            "payment_method": reservation_data.get("payment_method", "later"),
            "payment_status": "pending",
            "price": get_service_price(reservation_data["service"]),
            "created_at": datetime.now().isoformat(),
            "notified": False,
            "reminded_hour": False
        }
        data["reservations"].append(reservation)
        if "pending_reservations" not in data:
            data["pending_reservations"] = []
        data["pending_reservations"].append(reservation["id"])
        data["next_id"] += 1
        if str(user_id) not in data["loyalty_points"]:
            data["loyalty_points"][str(user_id)] = {"points": 0, "total_bookings": 0}
        save_data(data)
        await send_payment_details(user_id, reservation["id"], reservation_data.get("payment_method", "later"))
        await send_pending_reservation_to_admin(reservation)
        del user_sessions[user_id]
        formatted_date = format_arabic_date(reservation_data["date"])
        time_12h = format_time_12h(reservation_data["time"])
        await message.reply_text(f"""
✅ **تم استلام رمز التحقق بنجاح!**
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {reservation_data['service']}
💰 السعر: ${reservation['price']}
{f'👨‍⚕️ الموظف: {reservation_data["employee_name"]}' if reservation_data.get("employee_name") else ''}
📋 رقم الطلب: #{reservation['id']}
⏳ **في انتظار موافقة الإدارة...**
ستتلقى رسالة تأكيد عند الموافقة على حجزك.
شكراً لثقتك! 🤝
""", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main")]]), parse_mode=ParseMode.MARKDOWN)
    else:
        remaining = session.get("otp_attempts", 3) - 1
        session["otp_attempts"] = remaining
        if remaining <= 0:
            del user_sessions[user_id]
            await message.reply_text("❌ لقد تجاوزت عدد المحاولات المسموح. يرجى بدء الحجز من جديد.")
        else:
            await message.reply_text(f"❌ رمز التحقق غير صحيح. تبقى {remaining} محاولات.")

@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    is_admin = user_id == ADMIN_ID

    if data == "back_main":
        await callback_query.message.edit_text("🌟 **القائمة الرئيسية** 🌟\nاختر الخدمة التي تريدها:", reply_markup=get_main_keyboard(is_admin), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "new_booking":
        await callback_query.message.edit_text("📌 **اختر الخدمة المطلوبة:**", reply_markup=get_services_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "back_services":
        await callback_query.message.edit_text("📌 **اختر الخدمة المطلوبة:**", reply_markup=get_services_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "back_days":
        employee_id = user_sessions.get(user_id, {}).get("employee_id")
        days = get_next_available_days(7, employee_id)
        if not days:
            await callback_query.answer("❌ لا توجد مواعيد متاحة في الأيام القادمة", show_alert=True)
            return
        await callback_query.message.edit_text("📅 **اختر اليوم المناسب:**", reply_markup=get_days_keyboard(days, employee_id), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("service_"):
        service = data.replace("service_", "")
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]["service"] = service
        DATA_DB = load_data()
        if DATA_DB.get("employees"):
            available_employees = [e for e in DATA_DB["employees"] if e.get("available", True)]
            if available_employees:
                await callback_query.message.edit_text(f"✅ تم اختيار الخدمة: **{service}**\n\n👨‍⚕️ **اختر الموظف المناسب:**", reply_markup=get_employees_keyboard(service), parse_mode=ParseMode.MARKDOWN)
            else:
                await callback_query.message.edit_text(f"✅ تم اختيار الخدمة: **{service}**\n\n📅 **اختر اليوم المناسب:**", reply_markup=get_days_keyboard(get_next_available_days()), parse_mode=ParseMode.MARKDOWN)
        else:
            await callback_query.message.edit_text(f"✅ تم اختيار الخدمة: **{service}**\n\n📅 **اختر اليوم المناسب:**", reply_markup=get_days_keyboard(get_next_available_days()), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("emp_"):
        parts = data.replace("emp_", "").split("_")
        emp_id = int(parts[0])
        service = parts[1] if len(parts) > 1 else user_sessions.get(user_id, {}).get("service")
        DATA_DB = load_data()
        employee = None
        for emp in DATA_DB["employees"]:
            if emp["id"] == emp_id:
                employee = emp
                break
        if employee:
            if user_id not in user_sessions:
                user_sessions[user_id] = {}
            user_sessions[user_id]["employee_id"] = emp_id
            user_sessions[user_id]["employee_name"] = employee["name"]
            days = get_next_available_days(7, emp_id)
            if not days:
                await callback_query.answer("❌ لا توجد مواعيد متاحة مع هذا الموظف", show_alert=True)
                return
            await callback_query.message.edit_text(f"✅ تم اختيار: **{employee['name']}**\n📌 التخصص: {employee['specialty']}\n📅 **اختر اليوم المناسب:**", reply_markup=get_days_keyboard(days, emp_id), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("day_"):
        parts = data.replace("day_", "").split("_")
        date = parts[0]
        employee_id = int(parts[1]) if len(parts) > 1 else user_sessions.get(user_id, {}).get("employee_id")
        slots = get_available_slots(date, employee_id)
        if not slots:
            await callback_query.answer("❌ لا توجد مواعيد متاحة في هذا اليوم", show_alert=True)
            return
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]["date"] = date
        formatted_date = format_arabic_date(date)
        await callback_query.message.edit_text(f"📅 **{formatted_date}**\n\n🕐 **اختر الوقت المناسب:**", reply_markup=get_slots_keyboard(slots, date, employee_id), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("time_"):
        parts = data.replace("time_", "").split("_")
        date = parts[0]
        time = parts[1]
        employee_id = int(parts[2]) if len(parts) > 2 else user_sessions.get(user_id, {}).get("employee_id")
        session = user_sessions.get(user_id, {})
        service = session.get("service", "استشارة")
        employee_name = session.get("employee_name")
        price = get_service_price(service)
        user_sessions[user_id]["reservation_data"] = {"date": date, "time": time, "service": service, "employee_id": employee_id, "employee_name": employee_name}
        formatted_date = format_arabic_date(date)
        time_12h = format_time_12h(time)
        await callback_query.message.edit_text(f"""
📝 **تأكيد الحجز**
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {service}
💰 السعر: ${price}
{f'👨‍⚕️ الموظف: {employee_name}' if employee_name else ''}
💳 **اختر طريقة الدفع:**
""", reply_markup=get_payment_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "pay_now" or data == "pay_later" or data == "pay_stars":
        session = user_sessions.get(user_id, {})
        if "reservation_data" not in session:
            await callback_query.answer("❌ حدث خطأ، يرجى المحاولة مرة أخرى", show_alert=True)
            return
        payment_method = "now" if data == "pay_now" else "later" if data == "pay_later" else "stars"
        session["reservation_data"]["payment_method"] = payment_method
        session["reservation_data"]["payment_status"] = "pending"
        otp = generate_otp()
        user_sessions[user_id]["state"] = "waiting_otp"
        user_sessions[user_id]["otp"] = otp
        user_sessions[user_id]["otp_attempts"] = 3
        extra_text = "\n⭐ **ميزة الدفع عبر نجوم تليجرام:**\n• سيتم إضافة 5 نقاط ولاء إضافية\n• الدفع سريع وآمن\n• يتم إرسال النجوم إلى: @{VEGA}\n" if data == "pay_stars" else ""
        await callback_query.message.edit_text(f"""
🔐 **رمز التحقق (OTP)**
📱 **رمز التحقق الخاص بك:**
`{otp}`
{extra_text}
⚠️ **كيفية إدخال الرمز:**
1. اضغط على زر "📱 أدخل رمز التحقق" أدناه
2. قم بنسخ الرمز وإرساله في رسالة للبوت
⏰ الرمز صالح لمدة 5 دقائق فقط
""", reply_markup=get_otp_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer("📱 تم إنشاء رمز التحقق", show_alert=True)
        return

    if data == "enter_otp":
        await callback_query.answer("📱 أرسل الرمز الذي يظهر لك في رسالة نصية للبوت", show_alert=True)
        return

    if data == "resend_otp":
        if user_id not in user_sessions or user_sessions[user_id].get("state") != "waiting_otp":
            await callback_query.answer("❌ لا توجد جلسة نشطة", show_alert=True)
            return
        new_otp = generate_otp()
        user_sessions[user_id]["otp"] = new_otp
        user_sessions[user_id]["otp_attempts"] = 3
        await callback_query.message.edit_text(f"""
🔐 **رمز تحقق جديد**
📱 **رمز التحقق الجديد:**
`{new_otp}`
⚠️ **كيفية إدخال الرمز:**
1. اضغط على زر "📱 أدخل رمز التحقق" أدناه
2. قم بنسخ الرمز وإرساله في رسالة للبوت
⏰ الرمز صالح لمدة 5 دقائق فقط
""", reply_markup=get_otp_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer("📱 تم إرسال رمز جديد", show_alert=True)
        return

    if data == "my_bookings":
        DATA_DB = load_data()
        user_bookings = [res for res in DATA_DB["reservations"] if res["user_id"] == user_id and res["status"] != "cancelled"]
        if not user_bookings:
            await callback_query.answer("📋 لا توجد حجوزات حالية", show_alert=True)
            return
        text = "📋 **حجوزاتي:**\n\n"
        for res in user_bookings:
            formatted_date = format_arabic_date(res["date"])
            time_12h = format_time_12h(res["time"])
            status = "✅ مؤكد" if res["status"] == "confirmed" else "⏳ قيد الانتظار" if res["status"] == "pending" else "❌ مرفوض"
            employee = f" - {res.get('employee_name', '')}" if res.get('employee_name') else ""
            text += f"#{res['id']} - {formatted_date} - {time_12h} - {res['service']}{employee} ({status})\n"
        await callback_query.message.edit_text(text, reply_markup=get_my_bookings_keyboard(user_bookings), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("view_"):
        res_id = int(data.replace("view_", ""))
        DATA_DB = load_data()
        for res in DATA_DB["reservations"]:
            if res["id"] == res_id:
                formatted_date = format_arabic_date(res["date"])
                time_12h = format_time_12h(res["time"])
                status = "✅ مؤكد" if res["status"] == "confirmed" else "⏳ قيد الانتظار" if res["status"] == "pending" else "❌ مرفوض"
                employee = f"\n👨‍⚕️ الموظف: {res.get('employee_name', 'غير محدد')}" if res.get('employee_name') else ""
                METHODS = {"now": "💳 دفع الآن", "later": "💰 دفع عند الموعد", "stars": f"⭐ نجوم تليجرام @{VEGA}"}
                payment = METHODS.get(res.get('payment_method', 'later'), 'غير محدد')
                text = f"""
📋 **تفاصيل الحجز #{res_id}**
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {res['service']}
💰 السعر: ${res.get('price', 0)}{employee}
💳 طريقة الدفع: {payment}
📊 الحالة: {status}
🎁 نقاط الولاء: يمكنك تقييم الخدمة للحصول على نقاط إضافية!
"""
                await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⭐ تقييم", callback_data=f"rate_{res_id}")], [InlineKeyboardButton("🔙 رجوع", callback_data="my_bookings")]]), parse_mode=ParseMode.MARKDOWN)
                break
        await callback_query.answer()
        return

    if data == "rate_service":
        DATA_DB = load_data()
        user_bookings = [res for res in DATA_DB["reservations"] if res["user_id"] == user_id and res["status"] == "confirmed"]
        if not user_bookings:
            await callback_query.answer("📋 لا توجد حجوزات مؤكدة لتقييمها", show_alert=True)
            return
        keyboard = []
        for res in user_bookings:
            keyboard.append([InlineKeyboardButton(f"#{res['id']} - {res['date']} - {res['service']}", callback_data=f"rate_{res['id']}")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
        await callback_query.message.edit_text("⭐ **اختر الحجز لتقييمه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("rate_") and len(data.split("_")) == 2:
        res_id = int(data.replace("rate_", ""))
        await callback_query.message.edit_text("⭐ **قيم الخدمة:**\n\nاختر عدد النجوم:", reply_markup=get_rating_keyboard(res_id), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("rate_") and len(data.split("_")) == 3:
        parts = data.split("_")
        res_id = int(parts[1])
        rating = int(parts[2])
        DATA_DB = load_data()
        if str(user_id) in DATA_DB["loyalty_points"]:
            DATA_DB["loyalty_points"][str(user_id)]["points"] += 5
        review = {"reservation_id": res_id, "user_id": user_id, "rating": rating, "created_at": datetime.now().isoformat()}
        DATA_DB["reviews"].append(review)
        save_data(DATA_DB)
        await callback_query.message.edit_text(f"⭐ **شكراً لتقييمك!**\n\nلقد حصلت على 5 نقاط إضافية!\n\nتقييمك: {'⭐' * rating}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer("✅ تم حفظ تقييمك!", show_alert=True)
        return

    if data == "loyalty_points":
        DATA_DB = load_data()
        user_points = DATA_DB["loyalty_points"].get(str(user_id), {"points": 0, "total_bookings": 0})
        discount = 20 if user_points["points"] >= 100 else 10 if user_points["points"] >= 50 else 5 if user_points["points"] >= 25 else 0
        text = f"""
💰 **نقاط الولاء**
👤 المستخدم: {callback_query.from_user.first_name}
⭐ النقاط الحالية: {user_points['points']}
📊 عدد الحجوزات: {user_points['total_bookings']}
🎁 الخصم المتاح: {discount}%
💡 **كيفية الحصول على نقاط:**
• حجز موعد: +10 نقاط
• تقييم الخدمة: +5 نقاط
• الدفع عبر نجوم تليجرام: +5 نقاط إضافية
🎯 **مستويات الخصم:**
• 25 نقطة → 5% خصم
• 50 نقطة → 10% خصم
• 100 نقطة → 20% خصم
"""
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎁 استخدم الخصم", callback_data="use_discount")], [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "use_discount":
        DATA_DB = load_data()
        user_points = DATA_DB["loyalty_points"].get(str(user_id), {"points": 0})
        discount = 20 if user_points["points"] >= 100 else 10 if user_points["points"] >= 50 else 5 if user_points["points"] >= 25 else 0
        if discount > 0:
            await callback_query.message.edit_text(f"🎁 **تم تطبيق الخصم!**\n\nلديك خصم {discount}% على حجزك القادم.\n\nسيتم خصم النقاط المستخدمة عند الحجز.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 حجز الآن", callback_data="new_booking")], [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]), parse_mode=ParseMode.MARKDOWN)
        else:
            await callback_query.answer("❌ ليس لديك نقاط كافية للخصم", show_alert=True)
        return

    if data == "cancel_booking":
        DATA_DB = load_data()
        user_bookings = [res for res in DATA_DB["reservations"] if res["user_id"] == user_id and res["status"] != "cancelled"]
        if not user_bookings:
            await callback_query.answer("📋 لا توجد حجوزات لإلغائها", show_alert=True)
            return
        await callback_query.message.edit_text("❌ **اختر الحجز الذي تريد إلغاءه:**", reply_markup=get_cancel_bookings_keyboard(user_bookings), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("cancel_"):
        res_id = int(data.replace("cancel_", ""))
        DATA_DB = load_data()
        for res in DATA_DB["reservations"]:
            if res["id"] == res_id and res["user_id"] == user_id:
                res["status"] = "cancelled"
                if str(user_id) in DATA_DB["loyalty_points"]:
                    DATA_DB["loyalty_points"][str(user_id)]["points"] = max(0, DATA_DB["loyalty_points"][str(user_id)]["points"] - 5)
                break
        save_data(DATA_DB)
        await callback_query.message.edit_text(f"❌ تم إلغاء الحجز #{res_id} بنجاح.\n\nتم خصم 5 نقاط ولاء.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main")]]))
        await callback_query.answer("❌ تم إلغاء الحجز", show_alert=True)
        return

    if data == "admin_panel":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("⚙️ **لوحة تحكم المالك**\n\nاختر الإدارة المطلوبة:", reply_markup=get_admin_panel_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_employees":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("👨‍⚕️ **إدارة الموظفين**\n\nاختر الإجراء المطلوب:", reply_markup=get_employee_management_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_view_employees":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        if not DATA_DB["employees"]:
            await callback_query.answer("📋 لا يوجد موظفين", show_alert=True)
            return
        text = "👥 **قائمة الموظفين:**\n\n"
        for emp in DATA_DB["employees"]:
            status = "🟢 متاح" if emp.get("available", True) else "🔴 غير متاح"
            text += f"🆔 {emp['id']} - {emp['name']} - {emp['specialty']} - {status}\n"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_employees")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_add_employee":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("➕ **إضافة موظف جديد**\n\nأرسل الاسم والتخصص بهذا الشكل:\n`اسم الموظف - التخصص`\n\nمثال: `دكتور محمد - أسنان`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_employees")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_edit_employee":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        if not DATA_DB["employees"]:
            await callback_query.answer("📋 لا يوجد موظفين للتعديل", show_alert=True)
            return
        text = "✏️ **تعديل موظف**\n\nاختر الموظف للتعديل:\n"
        keyboard = []
        for emp in DATA_DB["employees"]:
            keyboard.append([InlineKeyboardButton(f"{emp['name']} - {emp['specialty']}", callback_data=f"admin_edit_emp_{emp['id']}")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_employees")])
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("admin_edit_emp_"):
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        emp_id = int(data.replace("admin_edit_emp_", ""))
        DATA_DB = load_data()
        emp = None
        for e in DATA_DB["employees"]:
            if e["id"] == emp_id:
                emp = e
                break
        if not emp:
            await callback_query.answer("❌ الموظف غير موجود", show_alert=True)
            return
        await callback_query.message.edit_text(f"✏️ **تعديل موظف: {emp['name']}**\n\nأرسل البيانات الجديدة بهذا الشكل:\n`الاسم الجديد - التخصص الجديد - متاح/غير متاح`\n\nمثال: `دكتور محمد - أسنان - متاح`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_employees")]]), parse_mode=ParseMode.MARKDOWN)
        admin_sessions[user_id] = {"editing_employee": emp_id}
        await callback_query.answer()
        return

    if data == "admin_delete_employee":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        if not DATA_DB["employees"]:
            await callback_query.answer("📋 لا يوجد موظفين للحذف", show_alert=True)
            return
        text = "🗑️ **حذف موظف**\n\nاختر الموظف للحذف:\n"
        keyboard = []
        for emp in DATA_DB["employees"]:
            keyboard.append([InlineKeyboardButton(f"{emp['name']} - {emp['specialty']}", callback_data=f"admin_delete_emp_{emp['id']}")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_employees")])
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("admin_delete_emp_"):
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        emp_id = int(data.replace("admin_delete_emp_", ""))
        DATA_DB = load_data()
        emp_name = ""
        for emp in DATA_DB["employees"]:
            if emp["id"] == emp_id:
                emp_name = emp["name"]
                break
        DATA_DB["employees"] = [e for e in DATA_DB["employees"] if e["id"] != emp_id]
        save_data(DATA_DB)
        await callback_query.message.edit_text(f"✅ تم حذف الموظف: {emp_name}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_employees")]]))
        await callback_query.answer("✅ تم الحذف", show_alert=True)
        return

    if data == "admin_slots":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("📅 **إدارة المواعيد**\n\nاختر الإجراء المطلوب:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ إضافة موعد", callback_data="admin_add_slot")],
            [InlineKeyboardButton("❌ حذف موعد", callback_data="admin_delete_slot")],
            [InlineKeyboardButton("📋 عرض المواعيد", callback_data="admin_view_slots")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_view_slots":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        if not DATA_DB["reservations"]:
            await callback_query.answer("📋 لا توجد مواعيد", show_alert=True)
            return
        text = "📋 **المواعيد القادمة:**\n\n"
        today = datetime.now().date()
        upcoming = [res for res in DATA_DB["reservations"] if datetime.strptime(res["date"], "%Y-%m-%d").date() >= today and res["status"] in ["confirmed", "pending"]]
        for res in upcoming[:20]:
            formatted_date = format_arabic_date(res["date"])
            time_12h = format_time_12h(res["time"])
            status = "✅" if res["status"] == "confirmed" else "⏳"
            text += f"{status} #{res['id']} - {formatted_date} - {time_12h} - {res['service']}\n"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_slots")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_settings":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("⚙️ **إعدادات البوت**\n\nاختر الإعداد لتعديله:", reply_markup=get_settings_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_set_start":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("🕐 **تعديل وقت البدء**\n\nأرسل وقت البدء بصيغة 24 ساعة:\nمثال: `9` أو `10`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_settings")]]))
        admin_sessions[user_id] = {"setting": "start_hour"}
        await callback_query.answer()
        return

    if data == "admin_set_end":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("🕐 **تعديل وقت الانتهاء**\n\nأرسل وقت الانتهاء بصيغة 24 ساعة:\nمثال: `20` أو `22`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_settings")]]))
        admin_sessions[user_id] = {"setting": "end_hour"}
        await callback_query.answer()
        return

    if data == "admin_set_duration":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("⏱️ **تعديل مدة الحجز**\n\nأرسل المدة بالدقائق:\nمثال: `30` أو `45`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_settings")]]))
        admin_sessions[user_id] = {"setting": "slot_duration"}
        await callback_query.answer()
        return

    if data == "admin_set_days":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("📅 **تعديل أيام العمل**\n\nأرسل أرقام الأيام مفصولة بفاصلة:\n0=الاثنين, 1=الثلاثاء, 2=الأربعاء, 3=الخميس, 4=الجمعة, 5=السبت, 6=الأحد\n\nمثال: `0,1,2,3,4` (من الاثنين للجمعة)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_settings")]]))
        admin_sessions[user_id] = {"setting": "working_days"}
        await callback_query.answer()
        return

    if data == "admin_holidays":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        holidays = DATA_DB.get("holidays", [])
        text = "📅 **الإجازات:**\n\n"
        if holidays:
            for h in holidays:
                text += f"• {format_arabic_date(h)}\n"
        else:
            text += "لا توجد إجازات مسجلة\n"
        await callback_query.message.edit_text(text + "\nلإضافة إجازة أرسل التاريخ (YYYY-MM-DD)\nلحذف إجازة استخدم /remove_holiday", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_settings")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_pending":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        pending = DATA_DB.get("pending_reservations", [])
        if not pending:
            await callback_query.answer("📋 لا توجد حجوزات معلقة", show_alert=True)
            return
        text = "📊 **الحجوزات المعلقة:**\n\n"
        for res_id in pending:
            for res in DATA_DB["reservations"]:
                if res["id"] == res_id:
                    formatted_date = format_arabic_date(res["date"])
                    time_12h = format_time_12h(res["time"])
                    text += f"#{res['id']} - {formatted_date} - {time_12h} - {res['service']} - {res['username']}\n"
                    break
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_all_bookings":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        if not DATA_DB["reservations"]:
            await callback_query.answer("📋 لا توجد حجوزات", show_alert=True)
            return
        text = "📋 **جميع الحجوزات:**\n\n"
        for res in DATA_DB["reservations"][-20:]:
            formatted_date = format_arabic_date(res["date"])
            time_12h = format_time_12h(res["time"])
            status = "✅" if res["status"] == "confirmed" else "⏳" if res["status"] == "pending" else "❌"
            text += f"{status} #{res['id']} - {formatted_date} - {time_12h} - {res['service']} - {res['username']}\n"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_payment":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text(f"💰 **إدارة الدفع**\n\nحساب استقبال نجوم تليجرام: @{VEGA}\n\nاختر الإجراء المطلوب:", reply_markup=get_payment_management_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data == "admin_update_phone":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("📱 **تحديث رقم الهاتف**\n\nأرسل رقم الهاتف الجديد:\nمثال: `+1234567890`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_payment")]]))
        admin_sessions[user_id] = {"update_payment": "phone"}
        await callback_query.answer()
        return

    if data == "admin_update_bank":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("🏦 **تحديث الحساب البنكي**\n\nأرسل معلومات الحساب البنكي الجديد:\nمثال: `IBAN: XX1234567890`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_payment")]]))
        admin_sessions[user_id] = {"update_payment": "bank"}
        await callback_query.answer()
        return

    if data == "admin_update_crypto":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text("💰 **تحديث محفظة العملات**\n\nأرسل عنوان المحفظة الجديد:\nمثال: `0x1234567890abcdef`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_payment")]]))
        admin_sessions[user_id] = {"update_payment": "crypto"}
        await callback_query.answer()
        return

    if data == "admin_update_stars":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        await callback_query.message.edit_text(f"⭐ **تحديث حساب نجوم تليجرام**\n\nأرسل اسم المستخدم الجديد:\nمثال: `new_username`\n\nالحالي: @{VEGA}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_payment")]]))
        admin_sessions[user_id] = {"update_payment": "telegram_stars"}
        await callback_query.answer()
        return

    if data == "admin_transactions":
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        DATA_DB = load_data()
        transactions = DATA_DB.get("transactions", [])
        if not transactions:
            await callback_query.answer("📊 لا توجد معاملات", show_alert=True)
            return
        text = "📊 **المعاملات المالية:**\n\n"
        for t in transactions[-10:]:
            text += f"#{t.get('id', '')} - {t.get('user', '')} - ${t.get('amount', 0)} - {t.get('status', '')}\n"
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_payment")]]), parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer()
        return

    if data.startswith("admin_approve_"):
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        res_id = int(data.replace("admin_approve_", ""))
        DATA_DB = load_data()
        res = None
        for r in DATA_DB["reservations"]:
            if r["id"] == res_id:
                r["status"] = "confirmed"
                res = r
                if str(r["user_id"]) in DATA_DB["loyalty_points"]:
                    DATA_DB["loyalty_points"][str(r["user_id"])]["points"] += 10
                    DATA_DB["loyalty_points"][str(r["user_id"])]["total_bookings"] += 1
                if r.get("payment_method") == "stars":
                    DATA_DB["loyalty_points"][str(r["user_id"])]["points"] += 5
                break
        if res_id in DATA_DB["pending_reservations"]:
            DATA_DB["pending_reservations"].remove(res_id)
        save_data(DATA_DB)
        await callback_query.message.edit_text(f"✅ تمت الموافقة على الحجز #{res_id} بنجاح!")
        if res:
            formatted_date = format_arabic_date(res["date"])
            time_12h = format_time_12h(res["time"])
            try:
                await app.send_message(res["user_id"], f"""
✅ **تم تأكيد حجزك!**
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {res['service']}
{f'👨‍⚕️ الموظف: {res["employee_name"]}' if res.get("employee_name") else ''}
📋 رقم الحجز: #{res['id']}
🎁 تم إضافة 10 نقاط ولاء!
{f'⭐ تم إضافة 5 نقاط إضافية للدفع عبر نجوم تليجرام!' if res.get("payment_method") == "stars" else ''}
شكراً لثقتك! 🤝
""", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                print(f"خطأ في إرسال التأكيد للمستخدم: {e}")
        await callback_query.answer()
        return

    if data.startswith("admin_reject_"):
        if not is_admin:
            await callback_query.answer("❌ غير مصرح لك", show_alert=True)
            return
        res_id = int(data.replace("admin_reject_", ""))
        DATA_DB = load_data()
        res = None
        for r in DATA_DB["reservations"]:
            if r["id"] == res_id:
                r["status"] = "rejected"
                res = r
                break
        if res_id in DATA_DB["pending_reservations"]:
            DATA_DB["pending_reservations"].remove(res_id)
        save_data(DATA_DB)
        await callback_query.message.edit_text(f"❌ تم رفض الحجز #{res_id}.")
        if res:
            try:
                await app.send_message(res["user_id"], f"""
❌ **تم رفض حجزك**
📋 رقم الحجز: #{res['id']}
نأسف، لم يتم الموافقة على حجزك. يرجى المحاولة مرة أخرى أو الاتصال بنا للمزيد من المعلومات.
شكراً لتفهمك! 🤝
""", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                print(f"خطأ في إرسال الرفض للمستخدم: {e}")
        await callback_query.answer()
        return

    if data == "help":
        await help_command(client, callback_query.message)
        await callback_query.answer()
        return

@app.on_message(filters.text & filters.user(ADMIN_ID) & ~filters.command(["start", "help"]))
async def handle_admin_input(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id not in admin_sessions:
        return
    
    session = admin_sessions[user_id]
    
    if session.get("state") == "add_employee":
        try:
            if " - " not in text:
                await message.reply_text("❌ الصيغة غير صحيحة. استخدم: `الاسم - التخصص`")
                return
            name, specialty = text.split(" - ", 1)
            DATA_DB = load_data()
            new_id = max([e["id"] for e in DATA_DB["employees"]] + [0]) + 1
            DATA_DB["employees"].append({"id": new_id, "name": name.strip(), "specialty": specialty.strip(), "available": True})
            save_data(DATA_DB)
            await message.reply_text(f"✅ تم إضافة الموظف: {name.strip()} - {specialty.strip()}")
            del admin_sessions[user_id]
        except:
            await message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى")
        return
    
    if session.get("state") == "edit_employee":
        try:
            parts = text.split(" - ")
            if len(parts) < 2:
                await message.reply_text("❌ الصيغة غير صحيحة. استخدم: `الاسم - التخصص - متاح/غير متاح`")
                return
            name = parts[0].strip()
            specialty = parts[1].strip()
            available = True
            if len(parts) > 2:
                available = parts[2].strip() == "متاح"
            emp_id = session.get("editing_employee")
            if not emp_id:
                await message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى")
                return
            DATA_DB = load_data()
            for emp in DATA_DB["employees"]:
                if emp["id"] == emp_id:
                    emp["name"] = name
                    emp["specialty"] = specialty
                    emp["available"] = available
                    break
            save_data(DATA_DB)
            await message.reply_text(f"✅ تم تعديل الموظف: {name} - {specialty}")
            del admin_sessions[user_id]
        except:
            await message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى")
        return
    
    if session.get("setting"):
        setting = session["setting"]
        DATA_DB = load_data()
        settings = DATA_DB.get("settings", {})
        
        if setting == "start_hour":
            try:
                hour = int(text)
                if 0 <= hour <= 23:
                    settings["working_hours"]["start"] = hour
                    DATA_DB["settings"] = settings
                    save_data(DATA_DB)
                    await message.reply_text(f"✅ تم تعديل وقت البدء إلى: {hour}:00")
                else:
                    await message.reply_text("❌ يجب أن يكون الرقم بين 0 و 23")
            except:
                await message.reply_text("❌ يرجى إدخال رقم صحيح")
            del admin_sessions[user_id]
            return
        
        if setting == "end_hour":
            try:
                hour = int(text)
                if 0 <= hour <= 23:
                    settings["working_hours"]["end"] = hour
                    DATA_DB["settings"] = settings
                    save_data(DATA_DB)
                    await message.reply_text(f"✅ تم تعديل وقت الانتهاء إلى: {hour}:00")
                else:
                    await message.reply_text("❌ يجب أن يكون الرقم بين 0 و 23")
            except:
                await message.reply_text("❌ يرجى إدخال رقم صحيح")
            del admin_sessions[user_id]
            return
        
        if setting == "slot_duration":
            try:
                duration = int(text)
                if duration > 0:
                    settings["slot_duration"] = duration
                    DATA_DB["settings"] = settings
                    save_data(DATA_DB)
                    await message.reply_text(f"✅ تم تعديل مدة الحجز إلى: {duration} دقيقة")
                else:
                    await message.reply_text("❌ يجب أن يكون الرقم أكبر من 0")
            except:
                await message.reply_text("❌ يرجى إدخال رقم صحيح")
            del admin_sessions[user_id]
            return
        
        if setting == "working_days":
            try:
                days = [int(d.strip()) for d in text.split(",")]
                if all(0 <= d <= 6 for d in days):
                    settings["working_days"] = days
                    DATA_DB["settings"] = settings
                    save_data(DATA_DB)
                    days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
                    await message.reply_text(f"✅ تم تعديل أيام العمل إلى: {', '.join([days_ar[d] for d in days])}")
                else:
                    await message.reply_text("❌ الأيام يجب أن تكون بين 0 و 6")
            except:
                await message.reply_text("❌ يرجى إدخال أرقام مفصولة بفواصل")
            del admin_sessions[user_id]
            return
    
    if session.get("update_payment"):
        payment_key = session["update_payment"]
        DATA_DB = load_data()
        METHODS = DATA_DB.get("METHODS", METHODS)
        METHODS[payment_key] = text
        DATA_DB["METHODS"] = METHODS
        save_data(DATA_DB)
        
        labels = {"phone": "رقم الهاتف", "bank": "الحساب البنكي", "crypto": "محفظة العملات", "telegram_stars": "نجوم تليجرام"}
        await message.reply_text(f"✅ تم تحديث {labels.get(payment_key, payment_key)}")
        del admin_sessions[user_id]
        return

async def check_reservations_for_reminder():
    DATA_DB = load_data()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    current_date = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now()
    for res in DATA_DB["reservations"]:
        if res["date"] == tomorrow and res["status"] == "confirmed" and not res.get("notified", False):
            formatted_date = format_arabic_date(res["date"])
            time_12h = format_time_12h(res["time"])
            try:
                await app.send_message(res["user_id"], f"""
🔔 **تذكير بموعدك غداً!**
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {res['service']}
{f'👨‍⚕️ الموظف: {res["employee_name"]}' if res.get("employee_name") else ''}
📋 رقم الحجز: #{res['id']}
ننتظرك غداً في الموعد المحدد! 🤝
""", parse_mode=ParseMode.MARKDOWN)
                res["notified"] = True
            except:
                pass
        if res["date"] == current_date and res["status"] == "confirmed" and not res.get("reminded_hour", False):
            try:
                res_dt = datetime.strptime(f"{res['date']} {res['time']}", "%Y-%m-%d %H:%M")
                diff = (res_dt - now).total_seconds()
                if 0 < diff <= 3900:
                    formatted_date = format_arabic_date(res["date"])
                    time_12h = format_time_12h(res["time"])
                    await app.send_message(res["user_id"], f"""
⏰ **تذكير بموعدك بعد ساعة!**
📅 التاريخ: {formatted_date}
🕐 الوقت: {time_12h}
📌 الخدمة: {res['service']}
{f'👨‍⚕️ الموظف: {res["employee_name"]}' if res.get("employee_name") else ''}
🔔 استعد لحضور موعدك!
""", parse_mode=ParseMode.MARKDOWN)
                    res["reminded_hour"] = True
            except:
                pass
    save_data(DATA_DB)

async def main():
    if not os.path.exists(DATA_DB):
        data = {
            "reservations": [],
            "pending_reservations": [],
            "next_id": 1,
            "employees": [
                {"id": 1, "name": "دكتور أحمد", "specialty": "أسنان", "available": True},
                {"id": 2, "name": "دكتور سارة", "specialty": "جلدية", "available": True},
                {"id": 3, "name": "دكتور خالد", "specialty": "عظام", "available": True}
            ],
            "reviews": [],
            "loyalty_points": {},
            "admin_ids": [ADMIN_ID],
            "holidays": [],
            "services": [
                {"name": "طبية", "price": 100, "duration": 30},
                {"name": "تجميل", "price": 80, "duration": 45},
                {"name": "صيانة", "price": 150, "duration": 60},
                {"name": "قانونية", "price": 200, "duration": 30},
                {"name": "مالية", "price": 180, "duration": 45}
            ],
            "settings": {
                "working_hours": TUTX,
                "slot_duration": SLOT,
                "working_days": DAYS
            },
            "METHODS": METHODS,
            "transactions": []
        }
        save_data(data)
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_reservations_for_reminder, CronTrigger(minute="*/30"), id="reminder_job")
    scheduler.start()
    
    print("🤖 البوت يعمل الآن...")
    print("📅 سيتم إرسال التذكيرات كل 30 دقيقة")
    print("👨‍⚕️ عدد الموظفين: 3")
    print("⭐ نظام النقاط مفعل")
    print("🔐 نظام OTP مفعل")
    print("💳 نظام الدفع مفعل")
    print(f"⭐ حساب استقبال نجوم تليجرام: @{VEGA}")
    
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())