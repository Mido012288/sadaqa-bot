import os
import random
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

HADITHS = [
    {"text": "إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى.", "source": "رواه البخاري ومسلم"},
    {"text": "من حسن إسلام المرء تركه ما لا يعنيه.", "source": "رواه الترمذي"},
    {"text": "لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه.", "source": "رواه البخاري ومسلم"},
    {"text": "المسلم من سلم المسلمون من لسانه ويده.", "source": "رواه البخاري ومسلم"},
    {"text": "من كان يؤمن بالله واليوم الآخر فليقل خيراً أو ليصمت.", "source": "رواه البخاري ومسلم"},
    {"text": "من سلك طريقاً يطلب فيه علماً سلك الله به طريقاً إلى الجنة.", "source": "رواه مسلم"},
    {"text": "خيركم من تعلم القرآن وعلمه.", "source": "رواه البخاري"},
    {"text": "الدال على الخير كفاعله.", "source": "رواه الترمذي"},
    {"text": "تبسمك في وجه أخيك صدقة.", "source": "رواه الترمذي"},
    {"text": "كل معروف صدقة.", "source": "رواه البخاري"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 سور قصيرة", callback_data="short_surahs")],
        [InlineKeyboardButton("🎧 صوت القرآن", callback_data="audio_surahs")],
        [InlineKeyboardButton("📜 حديث اليوم", callback_data="hadith")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك في بوت الصدقة الجارية 🌙\n\n"
        "اختر من الأزرار أو استخدم الأوامر:\n"
        "/quran رقم - نص السورة\n"
        "/audio رقم - صوت السورة\n"
        "/hadith - حديث عشوائي",
        reply_markup=reply_markup
    )

async def quran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("اكتب رقم السورة. مثال: /quran 1")
        return
    try:
        surah_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("رقم السورة لازم من 1 إلى 114.")
        return
    if not 1 <= surah_num <= 114:
        await update.message.reply_text("رقم السورة من 1 إلى 114.")
        return
    await update.message.reply_text("جاري تحضير السورة...")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.alquran.cloud/v1/surah/{surah_num}")
        data = r.json()
    if data.get("code") != 200:
        await update.message.reply_text("حدث خطأ، حاول لاحقاً.")
        return
    surah = data["data"]
    text = f"سورة {surah['name']}\n\n"
    for ayah in surah["ayahs"]:
        text += f"{ayah['text']} ({ayah['numberInSurah']})\n"
    for i in range(0, len(text), 4000):
        await update.message.reply_text(text[i:i+4000])

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("اكتب رقم السورة. مثال: /audio 1")
        return
    try:
        surah_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("رقم السورة لازم من 1 إلى 114.")
        return
    if not 1 <= surah_num <= 114:
        await update.message.reply_text("رقم السورة من 1 إلى 114.")
        return
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.alquran.cloud/v1/surah/{surah_num}")
        data = r.json()
    surah_name = data["data"]["name"]
    audio_url = f"https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy/{surah_num}.mp3"
    try:
        await update.message.reply_audio(audio=audio_url, title=f"سورة {surah_name}", performer="مشاري العفاسي")
    except Exception:
        await update.message.reply_text(f"رابط السورة الصوتية:\n{audio_url}")

async def hadith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    h = random.choice(HADITHS)
    await update.message.reply_text(f"📜 {h['text']}\n\n— {h['source']}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "short_surahs":
        keyboard = [[InlineKeyboardButton(f"{name}", callback_data=f"quran_{num}")] for name, num in {"الفاتحة":1,"الإخلاص":112,"الفلق":113,"الناس":114,"الكوثر":108,"العصر":103}.items()]
        await query.edit_message_text("اختر سورة:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "audio_surahs":
        keyboard = [[InlineKeyboardButton(f"{name}", callback_data=f"audio_{num}")] for name, num in {"الفاتحة":1,"الإخلاص":112,"الفلق":113,"الناس":114,"الكوثر":108,"العصر":103}.items()]
        await query.edit_message_text("اختر سورة للاستماع:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "hadith":
        h = random.choice(HADITHS)
        await query.edit_message_text(f"📜 {h['text']}\n\n— {h['source']}")
    elif query.data.startswith("quran_"):
        num = int(query.data.split("_")[1])
        await query.edit_message_text("جاري التحضير...")
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.alquran.cloud/v1/surah/{num}")
            data = r.json()
        surah = data["data"]
        text = f"سورة {surah['name']}\n\n"
        for ayah in surah["ayahs"]:
            text += f"{ayah['text']} ({ayah['numberInSurah']})\n"
        for i in range(0, len(text), 4000):
            await query.message.reply_text(text[i:i+4000])
    elif query.data.startswith("audio_"):
        num = int(query.data.split("_")[1])
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.alquran.cloud/v1/surah/{num}")
            data = r.json()
        surah_name = data["data"]["name"]
        audio_url = f"https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy/{num}.mp3"
        try:
            await query.message.reply_audio(audio=audio_url, title=f"سورة {surah_name}", performer="مشاري العفاسي")
        except Exception:
            await query.message.reply_text(f"رابط السورة الصوتية:\n{audio_url}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quran", quran))
    app.add_handler(CommandHandler("audio", audio))
    app.add_handler(CommandHandler("hadith", hadith))
    app.add_handler(CallbackQueryHandler(button))
    print("البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
