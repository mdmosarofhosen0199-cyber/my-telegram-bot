import os
import telebot
from telebot import types
from flask import Flask, request, jsonify

TOKEN = os.environ.get('BOT_TOKEN', '8903753705:AAGECTwArgyk6TNgVkTWnARBTnn_V5YUM-U')
ADMIN_ID = "6688928171"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

users_balance = {}
whatsapp_stock = []

@app.route('/', methods=['GET'])
def home():
    return "OTP & US WhatsApp Bot Server Active!", 200

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    @app.route('/telegram', methods=['POST'])
def telegram_webhook():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return jsonify({"status": "ok"}), 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    if chat_id not in users_balance:
        users_balance[chat_id] = 0.00

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyword=True)
    btn1 = types.KeyboardButton("🇺🇸 US WhatsApp নম্বর কিনুন ($0.40)")
    btn2 = types.KeyboardButton("👤 ফেসবুক আইডি কিনুন ($0.25)")
    btn3 = types.KeyboardButton("💳 ব্যালেন্স রিচার্জ")
    btn4 = types.KeyboardButton("👤 আমার প্রোফাইল")
    btn5 = types.KeyboardButton("💬 লাইভ সাপোর্ট")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(
        message.chat.id, 
        "👋 স্বাগতম! আমাদের ওটিপি এবং ইউএস হোয়াটসঅ্যাপ নম্বর অটো সেল বটে।\n\n"
        "🇺🇸 **US WhatsApp Number Price:** `$0.40` প্রতি পিস।\n"
        "💳 **Minimum Deposit:** `$0.40`", 
        parse_mode="Markdown", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "👤 আমার প্রোফাইল")
def user_profile(message):
    chat_id = str(message.chat.id)
    balance = users_balance.get(chat_id, 0.00)
    profile_text = (
        "👤 **Your Profile:**\n\n"
        f"🆔 **User ID:** `{chat_id}`\n"
        f"💰 **Current Balance:** `${balance:.2f}`\n\n"
        "নম্বর কিনতে পর্যাপ্ত ব্যালেন্স না থাকলে '💳 ব্যালেন্স রিচার্জ' অপশনে যান।"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💳 ব্যালেন্স রিচার্জ")
def recharge_balance(message):
    payment_info = (
        "💳 **Balance Recharge & Payment Methods:**\n\n"
        "📌 **Minimum Deposit:** `$0.40`\n\n"
        "দয়া করে নিচের মাধ্যমে পেমেন্ট সম্পন্ন করুন:\n"
        "🔹 **bKash / Nagad / Rocket:** `01948248391`\n"
        "🔹 **Binance Pay ID:** `802479401`\n\n"
        "টাকা পাঠানোর পর TrxID বা স্ক্রিনশট সহ অ্যাডমিনের সাথে যোগাযোগ করুন।"
    )
    bot.send_message(message.chat.id, payment_info, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💬 লাইভ সাপোর্ট")
def live_support(message):
    support_info = (
        "💬 **Live Support & Contact:**\n\n"
        "যেকোনো সমস্যা বা সহায়তার জন্য সরাসরি যোগাযোগ করুন:\n\n"
        "📞 **WhatsApp:** `01948248391`"
    )
    bot.send_message(message.chat.id, support_info, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🇺🇸 US WhatsApp নম্বর কিনুন ($0.40)")
def buy_whatsapp_number(message):
    chat_id = str(message.chat.id)
    balance = users_balance.get(chat_id, 0.00)
    price = 0.40

    if balance < price:
        bot.send_message(
            message.chat.id, 
            f"❌ আপনার পর্যাপ্ত ব্যালেন্স নেই!\n\nবর্তমান ব্যালেন্স: `${balance:.2f}`\nপ্রয়োজনীয় ব্যালেন্স: `$0.40`\n\nনম্বর কিনতে দয়া করে আগে ব্যালেন্স রিচার্জ করুন."
        )
        return

    if len(whatsapp_stock) == 0:
        bot.send_message(message.chat.id, "❌ দুঃখিত, বর্তমানে কোনো ইউএস হোয়াটসঅ্যাপ নম্বর স্টকে নেই। অনুগ্রহ করে কিছুক্ষণ পর চেষ্টা করুন অথবা সাপোর্টে যোগাযোগ করুন।")
        return

    assigned_number = whatsapp_stock.pop(0)
    users_balance[chat_id] -= price

    success_msg = (
        "✅ **Order Successful!**\n\n"
        f"📱 **WhatsApp Number:** `{assigned_number}`\n"
        f"💵 **Charged:** `$0.40`\n"
        f"💰 **Remaining Balance:** `${users_balance[chat_id]:.2f}`\n\n"
        "আপনার ক্লোন অ্যাপে এই নম্বরটি দিয়ে হোয়াটসঅ্যাপ ভেরিফিকেশন কোড (OTP) সম্পন্ন করুন।"
    )
    bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "/admin" and str(message.chat.id) == str(ADMIN_ID))
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("➕ Add US WhatsApp Number")
    btn2 = types.KeyboardButton("💵 Add Balance to User")
    btn3 = types.KeyboardButton("📦 Check Stock")
    btn4 = types.KeyboardButton("🔙 Main Menu")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "🛠 **Admin Control Panel:**\nSelect an option below:", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "/admin" and str(message.chat.id) != str(ADMIN_ID))
def not_admin(message):
    bot.send_message(message.chat.id, "❌ আপনি এই কমান্ড ব্যবহার করার অনুমতিপ্রাপ্ত নন।")

@bot.message_handler(func=lambda message: str(message.chat.id) == str(ADMIN_ID))
def admin_button_handler(message):
    text = message.text

    if text == "➕ Add US WhatsApp Number":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Confirm Add Sample US Number", callback_data="add_us_num"))
        bot.send_message(message.chat.id, "Click below to add a US WhatsApp number to the stock:", reply_markup=markup)
        
    elif text == "💵 Add Balance to User":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Add $1.00 Test Balance", callback_data="add_admin_balance"))
        bot.send_message(message.chat.id, "Click below to test balance addition:", reply_markup=markup)
        
    elif text == "📦 Check Stock":
        stock_count = len(whatsapp_stock)
        bot.send_message(message.chat.id, f"📊 **Current US WhatsApp Stock:** `{stock_count}` টি নম্বর মজুদ আছে।", parse_mode="Markdown")
        
    elif text == "🔙 Main Menu":
        send_welcome(message)

@bot.callback_query_handler(func=lambda call: str(call.message.chat.id) == str(ADMIN_ID))
def callback_handler(call):
    if call.data == "add_us_num":
        sample_us_number = "+1 (555) 019-4839"
        whatsapp_stock.append(sample_us_number)
        bot.answer_callback_query(call.id, "US Number added to stock!")
        bot.send_message(call.message.chat.id, f"✅ স্টকে সফলভাবে ১টি ইউএস নম্বর যোগ করা হয়েছে!\nমোট স্টক: {len(whatsapp_stock)} টি।")
        
    elif call.data == "add_admin_balance":
        admin_chat = str(ADMIN_ID)
        if admin_chat not in users_balance:
            users_balance[admin_chat] = 0.0
        users_balance[admin_chat] += 1.00
        bot.answer_callback_query(call.id, "Balance added!")
        bot.send_message(call.message.chat.id, f"✅ আপনার একাউন্টে ১.০০ ডলার যোগ করা হয়েছে। বর্তমান ব্যালেন্স: `${users_balance[admin_chat]:.2f}`")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
