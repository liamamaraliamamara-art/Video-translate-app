import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Logging သတ်မှတ်ခြင်း
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables ကနေ Tokens တွေကို ယူခြင်း
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client ကို Initialize လုပ်ခြင်း
client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    
    # ဗီဒီယိုဖိုင် ရှိမရှိ စစ်ဆေးခြင်း
    video = message.video or message.document
    if not video:
        await message.reply_text("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင်တစ်ခု ပို့ပေးပါ။")
        return

    await message.reply_text("🎬 ဗီဒီယိုကို လက်ခံရရှိပါပြီ။ Gemini က ဇာတ်လမ်းကို သုံးသပ်ပြီး Recap Script ရေးနေပါပြီ၊ ခဏစောင့်ပေးပါ...")

    file_path = "downloaded_video.mp4"
    
    try:
        # Telegram ကနေ ဗီဒီယိုကို Download ဆွဲခြင်း
        file = await context.bot.get_file(video.file_id)
        await file.download_to_drive(file_path)

        # Gemini Files API သို့ ဗီဒီယိုတင်ခြင်း
        print("Uploading video to Gemini...")
        uploaded_file = client.files.upload(file=file_path)

        # Gemini Model ဖြင့် Script တောင်းခံခြင်း
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                uploaded_file,
                "ဒီဗီဒီယိုအတွက် ဆွဲဆောင်မှုရှိပြီး အသေးစိတ်ကျတဲ့ Movie/Video Recap Script တစ်ခုကို မြန်မာဘာသာဖြင့် ရေးပေးပါ။ အစ၊ အလယ်၊ အဆုံး ဇာတ်ကွက်တွေကို ရှင်းရှင်းလင်းလင်း ခွဲခြားဖော်ပြပေးပါ။"
            ]
        )

        script_text = response.text

        # စာသားရှည်နေရင် Telegram ရဲ့ ကန့်သတ်ချက်ကြောင့် အပိုင်းလိုက် ပို့ပေးခြင်း
        if len(script_text) > 4000:
            for i in range(0, len(script_text), 4000):
                await message.reply_text(script_text[i:i+4000])
        else:
            await message.reply_text(script_text)

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply_text(f"❌ အမှားအယွင်း ဖြစ်သွားပါတယ်: {str(e)}")

    finally:
        # ဖုန်း/Server ထဲက ပုံတူ ဗီဒီယိုဖိုင်ကို ရှင်းလင်းခြင်း (Space လွတ်အောင်)
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    # Bot ကို စတင် Run ခြင်း
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # ဗီဒီယို သို့မဟုတ် Document ပုံစံနဲ့လာတဲ့ ဖိုင်များကို ဖမ်းယူရန်
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    
    print("Bot is running...")
    app.run_polling()
