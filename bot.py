import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector

import db_manager
from control_handlers import control_router
from postbot_handlers import postbot_router
from scheduler import PostScheduler

# Load environment variables
load_dotenv()

class ColorFormatter(logging.Formatter):
    GREY = "\x1b[38;20m"
    CYAN = "\x1b[36;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    FORMAT = "%(asctime)s [%(name)s] %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    
    COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: CYAN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelno, self.RESET)
        formatter = logging.Formatter(f"{log_color}{self.FORMAT}{self.RESET}")
        return formatter.format(record)

# Setup Logging
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self, dp_postbot: Dispatcher):
        self.dp_postbot = dp_postbot
        self.running_bots = {}   # bot_id -> Bot
        self.polling_task = None  # asyncio.Task for dynamic polling

    async def start_bot(self, bot_id: int, token: str, proxy: str = None):
        if bot_id in self.running_bots:
            return
            
        session = None
        if proxy and proxy.lower() != "none":
            try:
                if proxy.startswith("socks5://") or proxy.startswith("socks4://"):
                    connector = ProxyConnector.from_url(proxy)
                    session = AiohttpSession(connector=connector)
                elif proxy.startswith("http://") or proxy.startswith("https://"):
                    session = AiohttpSession(proxy=proxy)
                else:
                    logger.error(f"Unsupported proxy type for bot {bot_id}: {proxy}")
            except Exception as e:
                logger.error(f"Failed to setup proxy for bot {bot_id}: {e}")
                
        bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode="HTML"))
        
        try:
            me = await bot.get_me()
            bot.username = me.username
            
            # Register Bot Commands for the satellite bot
            try:
                from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
                # 1. Private chat commands (English, Russian, Hebrew)
                await bot.set_my_commands([
                    BotCommand(command="start", description="Start bot & open menu"),
                    BotCommand(command="menu", description="Show main menu")
                ], scope=BotCommandScopeAllPrivateChats())
                
                await bot.set_my_commands([
                    BotCommand(command="start", description="Запустить бота и открыть меню"),
                    BotCommand(command="menu", description="Показать главное меню")
                ], scope=BotCommandScopeAllPrivateChats(), language_code="ru")
                
                await bot.set_my_commands([
                    BotCommand(command="start", description="הפעל את הבוט ופתח את התפריט"),
                    BotCommand(command="menu", description="הצג את התפריט הראשי")
                ], scope=BotCommandScopeAllPrivateChats(), language_code="he")
                
                # 2. Group/Channel commands (English, Russian, Hebrew)
                await bot.set_my_commands([
                    BotCommand(command="chat", description="Show chat/group ID and information")
                ], scope=BotCommandScopeAllGroupChats())
                
                await bot.set_my_commands([
                    BotCommand(command="chat", description="Показать ID и информацию о чате/группе")
                ], scope=BotCommandScopeAllGroupChats(), language_code="ru")
                
                await bot.set_my_commands([
                    BotCommand(command="chat", description="הצג מזהה ומידע על הצ'אט/קבוצה")
                ], scope=BotCommandScopeAllGroupChats(), language_code="he")
                
                logger.info(f"Dynamic PostBot @{me.username} commands configured.")
            except Exception as cmd_err:
                logger.error(f"Failed to set commands for dynamic PostBot @{me.username}: {cmd_err}")
                
        except Exception as e:
            logger.error(f"Failed to call get_me for bot {bot_id}: {e}")
            await bot.session.close()
            return
            
        self.running_bots[bot_id] = bot
        logger.info(f"Dynamic PostBot @{me.username} (ID: {bot_id}) registered.")
        await self.restart_polling()

    async def restart_polling(self):
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
            self.polling_task = None
            
        if self.running_bots:
            self.polling_task = asyncio.create_task(self._run_polling())
            logger.info("Restarted satellite polling task with active bots.")

    async def _run_polling(self):
        try:
            bots_list = list(self.running_bots.values())
            allowed = self.dp_postbot.resolve_used_update_types()
            logger.info(f"Starting polling for satellite bots: {[getattr(b, 'username', 'unknown') for b in bots_list]} with allowed updates: {allowed}")
            await self.dp_postbot.start_polling(*bots_list, handle_signals=False, allowed_updates=allowed)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in satellite polling task: {e}")

    async def stop_bot(self, bot_id: int):
        if bot_id in self.running_bots:
            bot = self.running_bots.pop(bot_id)
            await bot.session.close()
            logger.info(f"Dynamic PostBot ID {bot_id} stopped.")
            await self.restart_polling()

    async def start_all_active_bots(self):
        bots = db_manager.get_all_postbots()
        for bot_row in bots:
            bot_id, token, _, proxy, is_active = bot_row
            if is_active:
                await self._setup_bot_without_restart(bot_id, token, proxy)
        await self.restart_polling()

    async def _setup_bot_without_restart(self, bot_id: int, token: str, proxy: str = None):
        if bot_id in self.running_bots:
            return
        session = None
        if proxy and proxy.lower() != "none":
            try:
                if proxy.startswith("socks5://") or proxy.startswith("socks4://"):
                    connector = ProxyConnector.from_url(proxy)
                    session = AiohttpSession(connector=connector)
                elif proxy.startswith("http://") or proxy.startswith("https://"):
                    session = AiohttpSession(proxy=proxy)
            except Exception:
                pass
        bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode="HTML"))
        try:
            me = await bot.get_me()
            bot.username = me.username
            self.running_bots[bot_id] = bot
            logger.info(f"Dynamic PostBot @{me.username} (ID: {bot_id}) pre-registered.")
        except Exception as e:
            logger.error(f"Failed to setup bot ID {bot_id} on startup: {e}")
            await bot.session.close()

    async def stop_all_bots(self):
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
            self.polling_task = None
            
        bot_ids = list(self.running_bots.keys())
        for bid in bot_ids:
            bot = self.running_bots.pop(bid)
            await bot.session.close()
        logger.info("All dynamic PostBots stopped.")

async def on_startup(dispatcher: Dispatcher, bot_manager: BotManager):
    logger.info("Initializing active postbots on startup...")
    await bot_manager.start_all_active_bots()

async def on_shutdown(dispatcher: Dispatcher, bot_manager: BotManager):
    logger.info("Shutting down all active postbots on shutdown...")
    await bot_manager.stop_all_bots()

async def main():
    token = os.getenv("MAIN_BOT_TOKEN")
    if not token or token == "6813618380:AAEoYp1uF4T":
        logger.warning("MAIN_BOT_TOKEN is not configured or still set to default placeholder in .env. Please configure it.")
        
    # Database Initialisation
    db_manager.init_db()
    
    # Shared memory storage for FSM
    storage = MemoryStorage()
    
    # Initialize Dispatchers
    dp_control = Dispatcher(storage=storage)
    dp_postbot = Dispatcher(storage=storage)
    
    # Register Routers
    dp_control.include_router(control_router)
    dp_postbot.include_router(postbot_router)
    
    # Initialize Bot Manager for client bots
    bot_manager = BotManager(dp_postbot=dp_postbot)
    
    # Register Startup/Shutdown Handlers on Control Bot
    dp_control.startup.register(on_startup)
    dp_control.shutdown.register(on_shutdown)
    
    # Initialize and start Scheduler
    scheduler = PostScheduler(bot_manager=bot_manager)
    await scheduler.start()
    
    # Start Control Bot
    control_bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    
    # Set bot commands menu
    try:
        from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
        # Default (English)
        await control_bot.set_my_commands([
            BotCommand(command="start", description="Start bot & show profile"),
            BotCommand(command="menu", description="Open main menu"),
            BotCommand(command="reset", description="Clear all promo codes from DB")
        ], scope=BotCommandScopeAllPrivateChats())
        # Hebrew
        await control_bot.set_my_commands([
            BotCommand(command="start", description="הפעל את הבוт והצג פרופיל"),
            BotCommand(command="menu", description="פתח את התפריט הראши"),
            BotCommand(command="reset", description="מחק את כל קודי הקופון")
        ], scope=BotCommandScopeAllPrivateChats(), language_code="he")
        # Russian
        await control_bot.set_my_commands([
            BotCommand(command="start", description="Запустить бота и показать профиль"),
            BotCommand(command="menu", description="Открыть главное меню"),
            BotCommand(command="reset", description="Сбросить (удалить) все промокоды")
        ], scope=BotCommandScopeAllPrivateChats(), language_code="ru")
        logger.info("Bot commands set successfully in English, Hebrew, and Russian.")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")
        
    try:
        logger.info("Starting Main Control Bot...")
        allowed = dp_control.resolve_used_update_types()
        logger.info(f"Starting polling for control bot with allowed updates: {allowed}")
        await dp_control.start_polling(control_bot, bot_manager=bot_manager, allowed_updates=allowed)
    finally:
        await scheduler.stop()
        await control_bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot ecosystem stopped by user.")
