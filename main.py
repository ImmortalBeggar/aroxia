import logging
import os
import time
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from aroxia.brain import Brain
from aroxia.memory import Memory
from aroxia.auth import Auth
from aroxia.multimodal import MultimodalHandler
from aroxia.loader import HotReloader
from aroxia.intelligence import IntelligenceModule
from aroxia.self import SelfModule
from aroxia.speech import SpeechModule
from aroxia.config import ConfigManager

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class AroxiaBot:
    def __init__(self, token):
        self.token = token
        self.auth = Auth()
        self.memory = Memory()
        self.mm = MultimodalHandler()
        self.reloader = HotReloader()
        self.intel = IntelligenceModule()
        self.self_info = SelfModule()
        self.speech = SpeechModule()
        self.settings = ConfigManager()
        
        # Initialize Brain with Dev Key by default
        dev_key = self.auth.get_developer_key()
        self.brain = Brain(api_key=dev_key)
        self.last_bot_interaction = 0
        self.response_mode = "both" # "text", "voice", "both"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! I am Aroxia, your companion. How can I help you today?")

    async def set_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mode = context.args[0].lower() if context.args else ""
        if mode in ["text", "voice", "both"]:
            self.response_mode = mode
            await update.message.reply_text(f"Response mode set to: {mode}")
        else:
            await update.message.reply_text("Usage: /mode [text|voice|both]")

    async def handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.settings.get("stickers", "enabled"): return
        sticker = update.message.sticker
        await update.message.reply_text(f"Nice sticker! (Emoji: {sticker.emoji})")

    async def handle_animation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.settings.get("gifs", "enabled"): return
        await update.message.reply_text("I love a good GIF!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        from_user = update.message.from_user
        bot_username = (await context.bot.get_me()).username
        
        # 1. Bot Detection & Protocol
        is_from_bot = from_user.is_bot
        text = update.message.text
        is_mention = f"@{bot_username}" in text
        is_reply_to_me = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
        
        if is_from_bot:
            now = time.time()
            if now - self.last_bot_interaction < 10:
                return
            if not is_mention:
                return
            self.last_bot_interaction = now

        # 2. Selective Interaction
        if not (is_mention or is_reply_to_me or update.message.chat.type == "private"):
            return

        # Show "Typing..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        await self.intel.wait_for_slot()

        # Progress bar (simulated)
        status_msg = None
        if len(text) > 100 or "search" in text.lower():
            status_msg = await update.message.reply_text("Aroxia is thinking... [░░░░░░░░░░] 0%")

        user_id = from_user.id
        username = from_user.username or from_user.first_name
        clean_text = text.replace(f"@{bot_username}", "").strip()
        
        identity_context = self.self_info.get_identity()
        chat_context = self.memory.get_context(user_id)
        full_system_context = f"{identity_context}\n{chat_context}"
        
        try:
            if status_msg: await status_msg.edit_text("Aroxia is processing... [▓▓▓░░░░░░░] 30%")
            
            response = await self.brain.generate_response(clean_text, context=full_system_context)
            
            self.intel.record_request(len(response) // 4 + 100) 
            if status_msg: await status_msg.delete()
            self.memory.log_interaction(user_id, username, clean_text, response)

            # Multimodal Response Handling
            if self.response_mode in ["text", "both"]:
                await update.message.reply_text(response)
            
            if self.response_mode in ["voice", "both"]:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
                v_cfg = self.settings.get("voice")
                voice_path = self.speech.text_to_speech(response, lang=v_cfg['lang'], slow=v_cfg['slow'])
                with open(voice_path, 'rb') as v:
                    await update.message.reply_voice(v)
                self.speech.cleanup()
            
        except Exception as e:
            if status_msg: await status_msg.edit_text("Reverting to local fallback...")
            response = await self.brain.generate_response(clean_text, context=full_system_context)
            await update.message.reply_text(response)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image = self.mm.process_image(photo_bytes)
        
        caption = update.message.caption or "What is in this image?"
        response = await self.brain.generate_response(caption, image=image)
        
        await update.message.reply_text(response)

    def run(self):
        app = ApplicationBuilder().token(self.token).build()
        
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("mode", self.set_mode))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        app.add_handler(MessageHandler(filters.Sticker.ALL, self.handle_sticker))
        app.add_handler(MessageHandler(filters.ANIMATION, self.handle_animation))
        
        print("Aroxia is running...")
        app.run_polling()

if __name__ == '__main__':
    TELEGRAM_TOKEN = "8621619489:AAE8JGosFxq1391LraS4NrTboo4MCita2Aw"
    bot = AroxiaBot(TELEGRAM_TOKEN)
    bot.run()
