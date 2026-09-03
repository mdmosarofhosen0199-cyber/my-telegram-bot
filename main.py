import os
import requests
from flask import Flask, request, jsonify
from telebot import TeleBot, types

# ==========================================
# কনফিগারেশন (আপনার তথ্য দিয়ে সরাসরি বসানো)
# ==========================================
TELEGRAM_BOT_TOKEN = "8866015274:AAGBzT3Jgmwuoeme41Zy3uxUh_xjkeFabZI"
ADMIN_ID = "6688928171"

PAYMENT_NUMBER = "01948248391"      # Bkash & Nagad Personal
BINANCE_PAY_ID = "802479401"        # Binance Pay ID
WHATSAPP_LINK = "https://wa.me/8801948248391"
OTP_PRICE_USD = 0.40

app = Flask(__name__)
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# ==========================================
# ডেটাবেজ / ইন-মেমোরি স্টোরেজ
# ==========================================
users = {}          # {chat_id: {'lang': 'bn', 'balance': 0.0}}
numbers_stock = []  # ["+8801700000000", ...]
fb_ids_stock = []   # ["email:pass:2fa", ...]

# ==========================================
# ভাষা সাপোর্ট (English & বাংলা)
# ==========================================
TEXTS = {
    'bn': {
        'welcome': "👋 স্বাগতম! আমাদের ওটিপি এবং ডিজিটাল প্রোডাক্ট সার্ভিস বটে। নিচের মেনু থেকে আপনার সার্ভিস নির্বাচন করুন।",
        'buy_num': "📱 নাম্বার কিনুন (Buy Number) - $0.40",
        'buy_fb': "👤 ফেসবুক আইডি কিনুন (Buy USA FB ID)",
        'recharge': "💳 ব্যালেন্স রিচার্জ (Rearge)",
        'profile': "👤 আমার প্রোফাইল (My Profile)",
        'support': "💬 লাইভ সাপোর্ট (Live Support)",
        'lang_set': "🌐 ভাষা পরিবর্তন (Language)",
        'no_stock': "❌ দুঃখিত! বর্তমানে স্টক ফাঁকা রয়েছে। অনুগ্রহ করে পরে চেষ্টা করুন অথবা এডমিনকে জানান।",
        'purchased_num': "✅ আপনার অর্জিত নাম্বার: `{}`\n⏱ ওটিপির জন্য অপেক্ষা করুন...",
        'purchased_fb': "✅ আপনার ইউএসএ ফেসবুক আইডি তথ্য:\n`{}`",
        'recharge_info': f"💳 *ব্যালেন্স রিচার্জ করার পদ্ধতি:*\n\n🇧🇩 **বিকাশ / নগদ (Personal):** `{PAYMENT_NUMBER}`\n🌐 **Binance Pay ID:** `{BINANCE_PAY_ID}`\n\nপেমেন্ট করার পর আপনার **TrxID / Transaction ID** এবং **টাকার পরিমাণ** নিচের লাইভ সাপোর্টে মেসেজ দিন। এডমিন ম্যানুয়ালি আপনার ব্যালেন্স যুক্ত করে দেবে।",
        'profile_info': "👤 *আপনার তথ্য:*\n\n🆔 আইডি: `{}`\n💵 বর্তমান ব্যালেন্স: `${:.2f}`\n🌐 ভাষা: বাংলা",
        'support_btn': "📲 হোয়াটসঅ্যাপে যোগাযোগ করুন"
    },
    'en': {
        'welcome': "👋 Welcome to OTP & Digital Products Service Bot! Please choose an option below.",
        'buy_num': "📱 Buy Number - $0.40",
        'buy_fb': "👤 Buy USA FB ID",
        'recharge': "💳 Recharge Balance",
        'profile': "👤 My Profile",
        'support': "💬 Live Support",
        'lang_set': "🌐 Change Language",
        'no_stock': "❌ Sorry! Currently out of stock. Please try again later or contact support.",
        'purchased_num': "✅ Your Number: `{}`\n⏱ Waiting for OTP...",
        'purchased_fb': "✅ Your USA FB Account Details:\n`{}`",
        'recharge_info': f"💳 *Balance Recharge Method:*\n\n🇧🇩 **Bkash / Nagad (Personal):** `{PAYMENT_NUMBER}`\n🌐 **Binance Pay ID:** `{BINANCE_PAY_ID}`\n\nAfter payment, please send your **TrxID** and **Amount** to our Live Support. Admin will update your balance manually.",
        'profile_info': "👤 *Your Account Profile:*\n\n🆔 ID: `{}`\n💵 Balance: `${:.2f}`\n🌐 Language: English",
        'support_btn': "📲 Contact on WhatsApp"
    }
}

def get_user_lang(chat_id):
    return users.get(chat_id, {}).get('lang', 'bn')

def get_user_balance(chat_id):
    return users.get(chat_id, {}).get('balance', 0.0)

def main_menu_keyboard(chat_id):
    lang = get_user_lang(chat_id)
    t = TEXTS[lang]
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton(t['buy_num'])
    btn2 = types.KeyboardButton(t['buy_fb'])
    btn3 = types.KeyboardButton(t['recharge'])
    btn4 = types.KeyboardButton(t['profile'])
    btn5 = types.KeyboardButton(t['support'])
    btn6 = types.KeyboardButton(t['lang_set'])
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in users:
        users[chat_id] = {'lang': 'bn', 'balance': 0.0}
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_bn = types.InlineKeyboardButton("🇧🇩 বাংলা", callback_data="set_lang_bn")
    btn_en = types.InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
    markup.add(btn_bn, btn_en)
    bot.send_message(chat_id, "Please select your language / ভাষা নির্বাচন করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang_'))
def callback_set_lang(call):
    chat_id = call.message.chat.id
    lang = 'bn' if call.data == 'set_lang_bn' else 'en'
    if chat_id not in users:
        users[chat_id] = {'balance': 0.0}
    users[chat_id]['lang'] = lang
    bot.answer_callback_query(call.id, "Language set successfully!")
    t = TEXTS[lang]
    bot.send_message(chat_id, t['welcome'], reply_markup=main_menu_keyboard(chat_id))

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text
    lang = get_user_lang(chat_id)
    t = TEXTS[lang]

    if chat_id not in users:
        users[chat_id] = {'lang': 'bn', 'balance': 0.0}

    # নাম্বার কেনা
    if text == t['buy_num'] or "Buy Number" in text or "নাম্বার কিনুন" in text:
        balance = get_user_balance(chat_id)
        if balance < OTP_PRICE_USD:
            bot.reply_to(message, f"❌ পর্যাপ্ত ব্যালেন্স নেই! নাম্বারের মূল্য ${OTP_PRICE_USD:.2f}। আপনার ব্যালেন্স আছে ${balance:.2f}। অনুগ্রহ করে রিচার্জ করুন।", parse_mode="Markdown")
            return
        if not numbers_stock:
            bot.reply_to(message, t['no_stock'])
            return
        number = numbers_stock.pop(0)
        users[chat_id]['balance'] -= OTP_PRICE_USD
        bot.reply_to(message, t['purchased_num'].format(number), parse_mode="Markdown")

    # ফেসবুক আইডি কেনা
    elif text == t['buy_fb'] or "Buy USA FB" in text or "ফেসবুক আইডি" in text:
        fb_price = 1.00
        balance = get_user_balance(chat_id)
        if balance < fb_price:
            bot.reply_to(message, f"❌ পর্যাপ্ত ব্যালেন্স নেই! ফেসবুক আইডির মূল্য ${fb_price:.2f}। আপনার ব্যালেন্স আছে ${balance:.2f}।", parse_mode="Markdown")
            return
        if not fb_ids_stock:
            bot.reply_to(message, t['no_stock'])
            return
        fb_account = fb_ids_stock.pop(0)
        users[chat_id]['balance'] -= fb_price
        bot.reply_to(message, t['purchased_fb'].format(fb_account), parse_mode="Markdown")

    # রিচার্জ অপশন
    elif text == t['recharge'] or "Recharge" in text or "রিচার্জ" in text:
        bot.reply_to(message, t['recharge_info'], parse_mode="Markdown")

    # প্রোফাইল
    elif text == t['profile'] or "Profile" in text or "প্রোফাইল" in text:
        bal = get_user_balance(chat_id)
        bot.reply_to(message, t['profile_info'].format(chat_id, bal), parse_mode="Markdown")

    # লাইভ সাপোর্ট
    elif text == t['support'] or "Support" in text or "সাপোর্ট" in text:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(t['support_btn'], url=WHATSAPP_LINK)
        markup.add(btn)
        bot.reply_to(message, f"💬 আমাদের সাথে সরাসরি কথা বলতে নিচের বোতামে চাপ দিন:\n\n📱 WhatsApp: {PAYMENT_NUMBER}", reply_markup=markup)

    # ভাষা পরিবর্তন
    elif text == t['lang_set'] or "Language" in text or "ভাষা" in text:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_bn = types.InlineKeyboardButton("🇧🇩 বাংলা", callback_data="set_lang_bn")
        btn_en = types.InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
        markup.add(btn_bn, btn_en)
        bot.send_message(chat_id, "Select Language / ভাষা বেছে নিন:", reply_markup=markup)

    # এডমিন কমান্ড
    elif text.startswith('/addbalance') and str(chat_id) == str(ADMIN_ID):
        try:
            _, target_user, amount = text.split()
            target_user = int(target_user)
            amount = float(amount)
            if target_user not in users:
                users[target_user] = {'lang': 'bn', 'balance': 0.0}
            users[target_user]['balance'] += amount
            bot.reply_to(message, f"✅ User `{target_user}` balance updated. Added: ${amount:.2f}")
            bot.send_message(target_user, f"🎉 আপনার অ্যাকাউন্টে ${amount:.2f} ব্যালেন্স যোগ করা হয়েছে!")
        except Exception as e:
            bot.reply_to(message, "❌ ব্যবহার পদ্ধতি: `/addbalance USER_ID AMOUNT`")

    elif text.startswith('/addnumber') and str(chat_id) == str(ADMIN_ID):
        try:
            _, num = text.split()
            numbers_stock.append(num)
            bot.reply_to(message, f"✅ নাম্বার স্টকে যোগ হয়েছে: `{num}` (মোট স্টক: {len(numbers_stock)})")
        except:
            bot.reply_to(message, "❌ ব্যবহার পদ্ধতি: `/addnumber NUMBER`")

    elif text.startswith('/addfb') and str(chat_id) == str(ADMIN_ID):
        try:
            _, acc = text.split()
            fb_ids_stock.append(acc)
            bot.reply_to(message, f"✅ ফেসবুক আইডি স্টকে যোগ হয়েছে। (মোট স্টক: {len(fb_ids_stock)})")
        except:
            bot.reply_to(message, "❌ ব্যবহার পদ্ধতি: `/addfb details`")

@app.route('/', methods=['GET'])
def home():
    return "✅ OTP & Digital Product Bot Server Active!", 200

@app.route('/sms', methods=['POST'])
def receive_sms():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    sender = data.get('from') or data.get('sender') or 'Unknown'
    msg_text = data.get('content') or data.get('text') or 'No content'
    alert = f"📩 *New Live SMS Received!*\n\n📱 *From:* `{sender}`\n💬 *Message:*\n`{msg_text}`"
    bot.send_message(ADMIN_ID, alert, parse_mode="Markdown")
    return jsonify({"status": "success"}), 200

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Unauthorized', 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
