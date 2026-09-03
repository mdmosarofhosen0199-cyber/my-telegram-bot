import os
import telebot
from telebot import types
from flask import Flask, request, jsonify

TOKEN = os.environ.get('BOT_TOKEN', '7699745781:AAG56sS1JswG6sD8_H-V0E5ZcTqH4o8t0i0')
ADMIN_ID = "6688928171"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

numbers_stock = []
fb_ids_stock = []

@app.route('/', methods=['GET'])
def home():
    return "OTP & Digital Product Bot Server Active!", 200

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Unauthorized', 403

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🛒 নাম্বার কিনুন $0.40")
    btn2 = types.KeyboardButton("👤 ফেসবুক আইডি কিনুন $0.25")
    btn3 = types.KeyboardButton("💳 ব্যালেন্স রিচার্জ")
    btn4 = types.KeyboardButton("👤 আমার প্রোফাইল")
    btn5 = types.KeyboardButton("💬 লাইভ সাপোর্ট")
    btn6 = types.KeyboardButton("🌐 ভাষা পরিবর্তন")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, "👋 স্বাগতম! আমাদের ওটিপি এবং ডিজিটাল প্রোডাক্ট সার্ভিস বটে।", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "/admin" and str(message.chat.id) == str(ADMIN_ID))
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("➕ Add Number")
    btn2 = types.KeyboardButton("➕ Add FB ID")
    btn3 = types.KeyboardButton("💰 Add Balance")
    btn4 = types.KeyboardButton("📦 Check Stock")
    btn5 = types.KeyboardButton("📢 Broadcast")
    btn6 = types.KeyboardButton("🔙 Main Menu")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, "🛠 **Admin Control Panel:**\nSelect an option below:", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "/admin" and str(message.chat.id) != str(ADMIN_ID))
def not_admin(message):
    bot.send_message(message.chat.id, "❌ You are not authorized to use this command.")

@bot.message_handler(func=lambda message: str(message.chat.id) == str(ADMIN_ID))
def admin_button_handler(message):
    text = message.text

    if text == "➕ Add Number":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Confirm Add Sample Number", callback_data="add_sample_num"))
        bot.send_message(message.chat.id, "Click below to quickly add a sample number to stock:", reply_markup=markup)
        
    elif text == "➕ Add FB ID":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Confirm Add Sample FB ID", callback_data="add_sample_fbid"))
        bot.send_message(message.chat.id, "Click below to quickly add a sample Facebook ID to stock:", reply_markup=markup)
        
    elif text == "💰 Add Balance":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💵 Add $1.00 Test Balance", callback_data="add_test_balance"))
        bot.send_message(message.chat.id, "Click below to manage user balance options:", reply_markup=markup)
        
    elif text == "📦 Check Stock":
        num_count = len(numbers_stock)
        fb_count = len(fb_ids_stock)
        bot.send_message(message.chat.id, f"📊 **Current Stock:**\nNumbers: {num_count}\nFacebook IDs: {fb_count}", parse_mode="Markdown")
        
    elif text == "📢 Broadcast":
        bot.send_message(message.chat.id, "📢 Broadcast system is ready. Send your announcement text.")
        
    elif text == "🔙 Main Menu":
        send_welcome(message)

@bot.callback_query_handler(func=lambda call: str(call.message.chat.id) == str(ADMIN_ID))
def callback_handler(call):
    if call.data == "add_sample_num":
        numbers_stock.append("Sample_Number_01")
        bot.answer_callback_query(call.id, "Number added successfully!")
        bot.send_message(call.message.chat.id, "✅ Successfully added 1 number to stock via button click.")
    elif call.data == "add_sample_fbid":
        fb_ids_stock.append("Sample_FB_ID_01")
        bot.answer_callback_query(call.id, "Facebook ID added successfully!")
        bot.send_message(call.message.chat.id, "✅ Successfully added 1 Facebook ID to stock via button click.")
    elif call.data == "add_test_balance":
        bot.answer_callback_query(call.id, "Balance action triggered!")
        bot.send_message(call.message.chat.id, "✅ Test balance option triggered successfully.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
