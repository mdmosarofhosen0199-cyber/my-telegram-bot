import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8886047734:AAE6TO-EeYX2y6dtJCzzXKzeUJ43ON3bOEM"
ADMIN_ID = 8601269430

def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS numbers 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance REAL)''')
    
    default_number = "+1 (309) 252-7809"
    cursor.execute("SELECT id FROM numbers WHERE phone = ?", (default_number,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO numbers (phone, status) VALUES (?, 'available')", (default_number,))
    
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0.0))
    conn.commit()
    conn.close()

    keyboard = [
        [InlineKeyboardButton("📱 নাম্বার কিনুন", callback_data='buy_number')],
        [InlineKeyboardButton("💰 ব্যালেন্স যোগ করুন", callback_data='add_balance')],
        [InlineKeyboardButton("👤 আমার অ্যাকাউন্ট", callback_data='my_profile')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("স্বাগতম! নিচে থেকে আপনার প্রয়োজনীয় অপশন বেছে নিন:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'buy_number':
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, phone FROM numbers WHERE status = 'available' LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            num_id, phone_num = row
            cursor.execute("UPDATE numbers SET status = 'sold' WHERE id = ?", (num_id,))
            conn.commit()
            await query.edit_message_text(f"✅ আপনার কেনা নাম্বার: `{phone_num}`\n\nহোয়াটসঅ্যাপে কোড পাঠান, ওটিপি এখানে চলে আসবে।", parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ দুঃখিত, বর্তমানে কোনো নাম্বার স্টক নেই!")
        conn.close()

    elif query.data == 'add_balance':
        await query.edit_message_text("💰 ব্যালেন্স রিচার্জ করতে এডমিনের সাথে যোগাযোগ করুন।")

    elif query.data == 'my_profile':
        user_id = query.from_user.id
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        balance = row[0] if row else 0.0
        conn.close()
        await query.edit_message_text(f"👤 **আপনার আইডি:** `{user_id}`\n💵 **বর্তমান ব্যালেন্স:** {balance} টাকা", parse_mode='Markdown')

if __name__ == '__main__':
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    app.run_polling()
