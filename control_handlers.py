import re
import os
import logging
from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector

import db_manager
from locales import t

logger = logging.getLogger(__name__)
control_router = Router()

class ControlStates(StatesGroup):
    waiting_for_password = State()
    # Add Bot Wizard
    add_bot_admin_id = State()
    add_bot_admin_username = State()
    add_bot_token = State()
    add_bot_proxy = State()
    # Add Bot Admin
    add_postbot_admin_id = State()
    # Add Main Admin
    add_admin_id = State()
    add_admin_username = State()
    # Bot Sync Wizard
    sync_select_source = State()
    sync_select_target = State()

# Test bot connection and send test message
async def test_bot_connection(token: str, proxy: str, admin_id: int):
    session = None
    if proxy and proxy.lower() != "none":
        try:
            if proxy.startswith("socks5://") or proxy.startswith("socks4://"):
                connector = ProxyConnector.from_url(proxy)
                session = AiohttpSession(connector=connector)
            elif proxy.startswith("http://") or proxy.startswith("https://"):
                session = AiohttpSession(proxy=proxy)
            else:
                return False, "Unsupported proxy type. Use socks5:// or http://"
        except Exception as e:
            return False, f"Proxy setup error: {str(e)}"
            
    test_bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode="HTML"))
    try:
        me = await test_bot.get_me()
        
        # Get admin's details dynamically from Telegram
        try:
            admin_chat = await test_bot.get_chat(admin_id)
            admin_username = admin_chat.username or admin_chat.first_name or f"User_{admin_id}"
        except Exception as chat_err:
            logger.warning(f"Could not get chat for admin {admin_id}: {chat_err}")
            admin_username = f"User_{admin_id}"
            
        await test_bot.send_message(
            chat_id=admin_id,
            text=f"🟢 <b>PostBot Activation</b>\n\nYou have been successfully registered as an admin for this bot!"
        )
        return True, (me.username, admin_username)
    except Exception as e:
        return False, str(e)
    finally:
        await test_bot.session.close()

# Main Menu Keyboard Builder
def get_main_menu_keyboard(user_id, lang):
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_bot_list', lang), callback_data="ctl_bot_list", style="primary")
    builder.button(text=t('btn_sync_bots', lang), callback_data="ctl_sync_bots", style="primary")
    
    # Manage admins is Superadmin only
    if db_manager.is_superadmin(user_id):
        builder.button(text=t('btn_add_admin', lang), callback_data="ctl_manage_admins", style="primary")
        
    builder.button(text=t('btn_language', lang), callback_data="ctl_lang_menu", style="primary")
    builder.button(text=t('btn_help', lang), callback_data="ctl_help", style="primary")
    
    builder.adjust(1)
    return builder.as_markup()

# Command /start
@control_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    name = message.from_user.full_name
    lang = db_manager.get_user_lang(user_id)
    
    welcome_text = t('start_welcome', lang) + "\n\n" + t(
        'start_info', lang,
        name=name,
        username=f"@{username}" if username != "unknown" else "None",
        user_id=user_id,
        lang_code=message.from_user.language_code or "Unknown"
    )
    
    if db_manager.is_admin(user_id):
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(user_id, lang))
    else:
        superadmin = db_manager.get_superadmin()
        if not superadmin:
            await message.answer(t('enter_password', lang))
        else:
            await message.answer(welcome_text)


# Command /menu
@control_router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await message.answer(t('not_authorized', lang))
        return
    await state.clear()
    await message.answer(t('menu_title', lang), reply_markup=get_main_menu_keyboard(user_id, lang))

# Command /reset
@control_router.message(Command("reset"))
async def cmd_reset(message: Message):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await message.answer(t('not_authorized', lang))
        return
    
    db_manager.delete_all_promo_codes()
    await message.answer(t('promo_reset_success', lang))

# Callback Help
@control_router.callback_query(F.data.startswith("ctl_help"))
async def process_help(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    page = 0
    if callback.data.startswith("ctl_help_page_"):
        try:
            page = int(callback.data.split("_")[3])
        except (IndexError, ValueError):
            page = 0
            
    total_pages = 3
    page = max(0, min(page, total_pages - 1))
    
    page_key = f"help_page_{page + 1}"
    text = t('help_title', lang) + "\n\n" + t(page_key, lang)
    
    builder = InlineKeyboardBuilder()
    
    # Navigation row
    if page > 0:
        builder.button(text="⬅️", callback_data=f"ctl_help_page_{page-1}", style="primary")
    else:
        builder.button(text=" ", callback_data="dummy")
        
    builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
    
    if page < total_pages - 1:
        builder.button(text="➡️", callback_data=f"ctl_help_page_{page+1}", style="primary")
    else:
        builder.button(text=" ", callback_data="dummy")
        
    builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
    
    builder.adjust(3, 1)
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Callback Main Menu
@control_router.callback_query(F.data == "ctl_main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(t('menu_title', lang), reply_markup=get_main_menu_keyboard(user_id, lang))
    await callback.answer()

# Language Menu
@control_router.callback_query(F.data == "ctl_lang_menu")
async def process_lang_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English" + (" ✅" if lang == "en" else ""), callback_data="ctl_set_lang_en", style="primary")
    builder.button(text="🇷🇺 Русский" + (" ✅" if lang == "ru" else ""), callback_data="ctl_set_lang_ru", style="primary")
    builder.button(text="🇮🇱 עברית" + (" ✅" if lang == "he" else ""), callback_data="ctl_set_lang_he", style="primary")
    builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(t('select_language', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_set_lang_"))
async def process_set_lang(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.split("_")[3]
    username = callback.from_user.username or "unknown"
    
    db_manager.set_user_lang(user_id, username, lang_code)
    await callback.message.edit_text(t('menu_title', lang_code), reply_markup=get_main_menu_keyboard(user_id, lang_code))
    await callback.answer()

# ================= ADD BOT WIZARD (FSM) =================

@control_router.callback_query(F.data == "ctl_add_bot")
async def process_add_bot(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    await state.set_state(ControlStates.add_bot_admin_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    
    await callback.message.edit_text(t('add_bot_start', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.message(ControlStates.add_bot_admin_id)
async def process_bot_admin_id(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not message.text or not message.text.isdigit():
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
        await message.answer(t('invalid_admin_id', lang), reply_markup=builder.as_markup())
        return
        
    await state.update_data(admin_id=int(message.text))
    await state.set_state(ControlStates.add_bot_admin_username)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_back', lang), callback_data="ctl_add_bot", style="primary")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(2)
    
    await message.answer(t('add_bot_admin_username', lang), reply_markup=builder.as_markup())

@control_router.message(ControlStates.add_bot_admin_username)
async def process_bot_admin_username(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    username = message.text.strip() if message.text else ""
    
    if not username:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
        await message.answer("❌ Username cannot be empty. Please send a valid username.", reply_markup=builder.as_markup())
        return
        
    if username.startswith('@'):
        username = username[1:]
        
    await state.update_data(admin_username=username)
    await state.set_state(ControlStates.add_bot_token)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_back', lang), callback_data="ctl_add_bot", style="primary")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(2)
    
    await message.answer(t('add_bot_token', lang), reply_markup=builder.as_markup())

@control_router.callback_query(F.data == "ctl_add_bot_back_username")
async def process_add_bot_back_username(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    await state.set_state(ControlStates.add_bot_admin_username)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_back', lang), callback_data="ctl_add_bot", style="primary")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(2)
    
    await callback.message.edit_text(t('add_bot_admin_username', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data == "ctl_add_bot_back_token")
async def process_add_bot_back_token(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    await state.set_state(ControlStates.add_bot_token)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_back', lang), callback_data="ctl_add_bot_back_username", style="primary")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(2)
    
    await callback.message.edit_text(t('add_bot_token', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.message(ControlStates.add_bot_token)
async def process_bot_token(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    token = message.text.strip() if message.text else ""
    
    if not re.match(r"^\d+:[A-Za-z0-9_-]+$", token):
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
        await message.answer(t('invalid_token', lang), reply_markup=builder.as_markup())
        return
        
    if message.bot and token == message.bot.token:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
        await message.answer("❌ You cannot add the Main Control Bot as a satellite postbot. Please use a different bot token.", reply_markup=builder.as_markup())
        return
        
    await state.update_data(token=token)
    await state.set_state(ControlStates.add_bot_proxy)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_skip', lang), callback_data="ctl_add_bot_skip_proxy", style="success")
    builder.button(text=t('btn_back', lang), callback_data="ctl_add_bot_back_token", style="primary")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(1, 2)
    
    await message.answer(t('add_bot_proxy', lang), reply_markup=builder.as_markup())

async def perform_proxy_setup_and_save(state: FSMContext, bot_manager, status_msg: Message, data: dict, lang: str):
    success, result = await test_bot_connection(data['token'], data['proxy'], data['admin_id'])
    
    if success:
        bot_username, owner_username = result
        user_entered_username = data.get('admin_username', owner_username)
        if user_entered_username:
            owner_username = user_entered_username
            
        # Add to database
        db_success, bot_id = db_manager.add_postbot(data['token'], bot_username, data['admin_id'], owner_username, data['proxy'])
        if db_success:
            # Start polling dynamically!
            await bot_manager.start_bot(bot_id, data['token'], data['proxy'])
            try:
                await status_msg.delete()
            except Exception:
                pass
            builder = InlineKeyboardBuilder()
            builder.button(text=t('btn_bot_list', lang), callback_data="ctl_bot_list", style="success")
            builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
            builder.adjust(1)
            await status_msg.answer(t('bot_added_success', lang, username=bot_username), reply_markup=builder.as_markup())
            await state.clear()
        else:
            builder = InlineKeyboardBuilder()
            builder.button(text=t('btn_bot_list', lang), callback_data="ctl_bot_list", style="success")
            builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
            builder.adjust(1)
            await status_msg.edit_text("❌ This bot token is already registered in the system.", reply_markup=builder.as_markup())
            await state.clear()
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_back', lang), callback_data="ctl_add_bot_back_token", style="primary")
        builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
        builder.adjust(2)
        
        err_msg = t('invalid_token_error', lang) if "Unauthorized" in result or "invalid" in result.lower() else t('test_msg_failed', lang)
        await status_msg.edit_text(f"{err_msg}\n\n<i>Details: {result}</i>", reply_markup=builder.as_markup())

@control_router.callback_query(F.data == "ctl_add_bot_skip_proxy")
async def process_add_bot_skip_proxy(callback: CallbackQuery, state: FSMContext, bot_manager):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    await state.update_data(proxy="none")
    data = await state.get_data()
    
    await callback.message.edit_text(t('testing_connection', lang))
    await callback.answer()
    
    await perform_proxy_setup_and_save(state, bot_manager, callback.message, data, lang)

@control_router.message(ControlStates.add_bot_proxy)
async def process_bot_proxy(message: Message, state: FSMContext, bot_manager):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    proxy = message.text.strip() if message.text else "none"
    
    if proxy.lower() != "none":
        if not (proxy.startswith("http://") or proxy.startswith("https://") or proxy.startswith("socks5://") or proxy.startswith("socks4://")):
            builder = InlineKeyboardBuilder()
            builder.button(text=t('btn_skip', lang), callback_data="ctl_add_bot_skip_proxy", style="success")
            builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
            builder.adjust(1)
            await message.answer(t('invalid_proxy', lang), reply_markup=builder.as_markup())
            return
            
    await state.update_data(proxy=proxy)
    data = await state.get_data()
    
    status_msg = await message.answer(t('testing_connection', lang))
    await perform_proxy_setup_and_save(state, bot_manager, status_msg, data, lang)

# ================= BOT LIST MANAGEMENT =================

@control_router.callback_query(F.data == "dummy")
async def process_dummy(callback: CallbackQuery):
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_bot_list"))
async def process_bot_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    page = 0
    if callback.data.startswith("ctl_bot_list_page_"):
        page = int(callback.data.split("_")[4])
        
    bots = db_manager.get_all_postbots()
    builder = InlineKeyboardBuilder()
    
    limit = 8
    total_items = len(bots) if bots else 0
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    page_bots = []
    if bots:
        start_idx = page * limit
        end_idx = start_idx + limit
        page_bots = bots[start_idx:end_idx]
        for b in page_bots:
            builder.button(text=f"🤖 @{b[2]}", callback_data=f"ctl_bot_card_{b[0]}")
            
    sizes = [1] * len(page_bots)
    
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️", callback_data=f"ctl_bot_list_page_{page-1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
            
        builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
        
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"ctl_bot_list_page_{page+1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
        sizes.append(3)
        
    builder.button(text=t('btn_add_bot', lang), callback_data="ctl_add_bot", style="success")
    builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
    sizes.append(1)
    sizes.append(1)
    builder.adjust(*sizes)
    
    text = t('bot_list_title', lang) if bots else t('no_bots', lang)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_bot_card_"))
async def process_bot_card(callback: CallbackQuery, bot_id: int = None):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    if bot_id is None:
        bot_id = int(callback.data.split("_")[3])
    bot_row = db_manager.get_postbot(bot_id)
    if not bot_row:
        await callback.answer("Bot not found.", show_alert=True)
        return
        
    admins = db_manager.get_postbot_admins(bot_id)
    owner_username = "None"
    for adm in admins:
        if adm[2] == "owner":
            owner_username = adm[1]
            break
            
    status_str = "🟢 Active" if bot_row[4] == 1 else "🔴 Inactive"
    
    text = t(
        'bot_card', lang,
        username=bot_row[2],
        owner=owner_username,
        token=bot_row[1],
        proxy=bot_row[3] or "None",
        status=status_str
    )
    
    builder = InlineKeyboardBuilder()
    if bot_row[4] == 1:
        builder.button(text=t('btn_deactivate_bot', lang), callback_data=f"ctl_bot_deactivate_{bot_id}", style="danger")
    else:
        builder.button(text=t('btn_activate_bot', lang), callback_data=f"ctl_bot_activate_{bot_id}", style="success")
        
    builder.button(text=t('btn_update_data', lang), callback_data=f"ctl_bot_update_{bot_id}", style="primary")
    builder.button(text=t('btn_manage_bot_admins', lang), callback_data=f"ctl_bot_admins_{bot_id}", style="primary")
    builder.button(text=t('btn_delete_bot', lang), callback_data=f"ctl_bot_delconf_{bot_id}", style="danger")
    builder.button(text=t('btn_back', lang), callback_data="ctl_bot_list", style="primary")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_bot_deactivate_"))
async def process_bot_deactivate(callback: CallbackQuery, bot_manager):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bot_id = int(callback.data.split("_")[3])
    
    db_manager.update_postbot_active_status(bot_id, 0)
    await bot_manager.stop_bot(bot_id)
    
    await callback.answer("Bot deactivated successfully.", show_alert=True)
    await process_bot_card(callback, bot_id=bot_id)

@control_router.callback_query(F.data.startswith("ctl_bot_activate_"))
async def process_bot_activate(callback: CallbackQuery, bot_manager):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bot_id = int(callback.data.split("_")[3])
    bot_row = db_manager.get_postbot(bot_id)
    if not bot_row:
        await callback.answer("Bot not found.", show_alert=True)
        return
        
    token, proxy = bot_row[1], bot_row[3]
    
    await callback.message.edit_text("🔄 <i>Testing bot connection...</i>")
    success, result = await test_bot_connection(token, proxy, user_id)
    
    if success:
        db_manager.update_postbot_active_status(bot_id, 1)
        await bot_manager.start_bot(bot_id, token, proxy)
        await callback.answer("Bot activated and started successfully.", show_alert=True)
    else:
        await callback.answer(f"❌ Failed to activate bot. Connection test failed:\n\n{result}", show_alert=True)
        
    await process_bot_card(callback, bot_id=bot_id)

# Update Bot Username
@control_router.callback_query(F.data.startswith("ctl_bot_update_"))
async def process_bot_update(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bot_id = int(callback.data.split("_")[3])
    bot_row = db_manager.get_postbot(bot_id)
    if not bot_row:
        await callback.answer("Bot not found.", show_alert=True)
        return
        
    token = bot_row[1]
    proxy = bot_row[3]
    
    session = None
    if proxy and proxy.lower() != "none":
        try:
            if proxy.startswith("socks5://") or proxy.startswith("socks4://"):
                connector = ProxyConnector.from_url(proxy)
                session = AiohttpSession(connector=connector)
            else:
                session = AiohttpSession(proxy=proxy)
        except Exception:
            pass
            
    temp_bot = Bot(token=token, session=session)
    try:
        me = await temp_bot.get_me()
        db_manager.update_postbot_username(bot_id, me.username)
        await callback.answer("🟢 Data updated successfully from Telegram API!", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Failed to fetch: {str(e)}", show_alert=True)
    finally:
        await temp_bot.session.close()
        
    await process_bot_card(callback, bot_id=bot_id)

# Delete Bot Confirmation
@control_router.callback_query(F.data.startswith("ctl_bot_delconf_"))
async def process_bot_delconf(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bot_id = int(callback.data.split("_")[3])
    bot_row = db_manager.get_postbot(bot_id)
    if not bot_row:
        await callback.answer("Bot not found.", show_alert=True)
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_confirm_delete', lang), callback_data=f"ctl_bot_delete_{bot_id}", style="danger")
    builder.button(text=t('btn_cancel', lang), callback_data=f"ctl_bot_card_{bot_id}", style="primary")
    builder.adjust(1)
    
    await callback.message.edit_text(t('delete_confirm', lang, username=bot_row[2]), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_bot_delete_"))
async def process_bot_delete(callback: CallbackQuery, bot_manager):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bot_id = int(callback.data.split("_")[3])
    
    await bot_manager.stop_bot(bot_id)
    db_manager.delete_postbot(bot_id)
    
    await callback.answer(t('bot_deleted', lang), show_alert=True)
    await process_bot_list(callback)

# ================= POSTBOT ADMINS MANAGEMENT (VIA CONTROL BOT) =================

@control_router.callback_query(F.data.startswith("ctl_bot_admins_"))
async def process_postbot_admins(callback: CallbackQuery, bot_id: int = None):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    parts = callback.data.split("_")
    if bot_id is None:
        bot_id = int(parts[3])
        
    page = 0
    if len(parts) >= 6 and parts[4] == "page":
        page = int(parts[5])
        
    bot_row = db_manager.get_postbot(bot_id)
    if not bot_row:
        await callback.answer("Bot not found.", show_alert=True)
        return
        
    admins = db_manager.get_postbot_admins(bot_id)
    
    limit = 8
    total_items = len(admins) if admins else 0
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    builder = InlineKeyboardBuilder()
    page_admins = []
    if admins:
        start_idx = page * limit
        end_idx = start_idx + limit
        page_admins = admins[start_idx:end_idx]
        for adm in page_admins:
            adm_id, adm_user, adm_role = adm
            if adm_role == "owner":
                builder.button(text=f"👑 @{adm_user} (Owner)", callback_data="dummy")
            else:
                builder.button(text=f"🗑️ Remove @{adm_user}", callback_data=f"ctl_pbadm_remove_{bot_id}_{adm_id}", style="danger")
                
    sizes = [1] * len(page_admins)
    
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️", callback_data=f"ctl_bot_admins_{bot_id}_page_{page-1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
            
        builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
        
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"ctl_bot_admins_{bot_id}_page_{page+1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
        sizes.append(3)
        
    builder.button(text=t('btn_add_new_admin', lang), callback_data=f"ctl_pbadm_add_{bot_id}", style="success")
    builder.button(text=t('btn_back', lang), callback_data=f"ctl_bot_card_{bot_id}", style="primary")
    sizes.append(1)
    sizes.append(1)
    builder.adjust(*sizes)
    
    await callback.message.edit_text(t('postbot_admin_list_title', lang, username=bot_row[2]), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_pbadm_remove_"))
async def process_pbadm_remove(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    parts = callback.data.split("_")
    bot_id = int(parts[3])
    target_id = int(parts[4])
    
    success = db_manager.remove_postbot_admin(bot_id, target_id)
    if success:
        await callback.answer(t('admin_removed', lang), show_alert=True)
    else:
        await callback.answer(t('cannot_remove_owner', lang), show_alert=True)
        
    await process_postbot_admins(callback, bot_id=bot_id)

@control_router.callback_query(F.data.startswith("ctl_pbadm_add_"))
async def process_pbadm_add(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bot_id = int(callback.data.split("_")[3])
    await state.update_data(target_pbot_id=bot_id)
    await state.set_state(ControlStates.add_postbot_admin_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"ctl_bot_admins_{bot_id}", style="danger")
    
    await callback.message.edit_text(t('enter_admin_id', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.message(ControlStates.add_postbot_admin_id)
async def process_add_pbadm_id_msg(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_admin(user_id):
        await message.answer(t('not_authorized', lang))
        return
        
    target = message.text.strip() if message.text else ""
    if not target.isdigit():
        await message.answer("❌ Invalid ID format. Please send a numeric Telegram User ID.")
        return
        
    target_id = int(target)
    state_data = await state.get_data()
    bot_id = state_data['target_pbot_id']
    
    bot_row = db_manager.get_postbot(bot_id)
    if not bot_row:
        await message.answer("Bot not found.")
        await state.clear()
        return
        
    status_msg = await message.answer(t('testing_connection', lang))
    
    # Test connection and send message to verify user has initiated contact
    success, result = await test_bot_connection(bot_row[1], bot_row[3], target_id)
    
    if success:
        bot_username, admin_username = result
        # Save in database
        db_manager.add_postbot_admin(bot_id, target_id, admin_username, 'admin')
        await status_msg.delete()
        await message.answer(t('admin_added', lang), reply_markup=get_main_menu_keyboard(user_id, lang))
        await state.clear()
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data=f"ctl_bot_admins_{bot_id}", style="danger")
        await status_msg.edit_text(f"❌ Failed to verify user: {result}\n\nMake sure the user has started a chat with @{bot_row[2]}.", reply_markup=builder.as_markup())

# ================= ADMIN MANAGEMENT (SUPERADMIN ONLY) =================

@control_router.callback_query(F.data.startswith("ctl_manage_admins"))
async def process_manage_admins(callback: CallbackQuery, state: FSMContext = None):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    if state:
        await state.clear()
        
    page = 0
    if callback.data.startswith("ctl_manage_admins_page_"):
        page = int(callback.data.split("_")[4])
        
    admins = db_manager.get_admins()
    
    limit = 8
    total_items = len(admins) if admins else 0
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    builder = InlineKeyboardBuilder()
    page_admins = []
    if admins:
        start_idx = page * limit
        end_idx = start_idx + limit
        page_admins = admins[start_idx:end_idx]
        for adm in page_admins:
            adm_id, adm_user, adm_role = adm
            display_name = f"@{adm_user}" if adm_user and not adm_user.startswith("ID_") else f"ID: {adm_id}"
            prefix = "👑 " if adm_role == "superadmin" else "👤 "
            builder.button(text=f"{prefix}{display_name}", callback_data=f"ctl_adm_card_{adm_id}")
            
    sizes = [1] * len(page_admins)
    
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️", callback_data=f"ctl_manage_admins_page_{page-1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
            
        builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
        
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"ctl_manage_admins_page_{page+1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
        sizes.append(3)
        
    builder.button(text=t('btn_add_new_admin', lang), callback_data="ctl_adm_add", style="success")
    builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
    sizes.append(1)
    sizes.append(1)
    builder.adjust(*sizes)
    
    await callback.message.edit_text(t('admin_list_title', lang), reply_markup=builder.as_markup())
    await callback.answer()

# Helper to render admin card detail view
async def show_admin_card(message: Message, target_id: int, lang: str, user_id: int):
    admins = db_manager.get_admins()
    admin_row = None
    for adm in admins:
        if adm[0] == target_id:
            admin_row = adm
            break
            
    if not admin_row:
        await message.edit_text("❌ Admin not found.")
        return
        
    adm_id, adm_user, adm_role = admin_row
    
    card_text = t('admin_card_title', lang) + "\n\n" + t(
        'admin_card_details', lang,
        user_id=adm_id,
        username=adm_user,
        role=adm_role
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_refresh_admin', lang), callback_data=f"ctl_adm_refresh_{adm_id}", style="primary")
    
    if adm_role != "superadmin" and adm_id != user_id:
        builder.button(text=t('btn_delete_admin', lang), callback_data=f"ctl_adm_remove_{adm_id}", style="danger")
        
    builder.button(text=t('btn_back', lang), callback_data="ctl_manage_admins", style="primary")
    builder.adjust(1)
    
    await message.edit_text(card_text, reply_markup=builder.as_markup())

@control_router.callback_query(F.data.startswith("ctl_adm_card_"))
async def process_adm_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    target_id = int(callback.data.split("_")[3])
    await show_admin_card(callback.message, target_id, lang, user_id)
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_adm_refresh_"))
async def process_adm_refresh(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    target_id = int(callback.data.split("_")[3])
    
    try:
        chat = await callback.bot.get_chat(target_id)
        new_username = chat.username or "unknown"
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE control_admins SET username = ? WHERE user_id = ?", (new_username, target_id))
        conn.commit()
        conn.close()
        
        await callback.answer(t('admin_refreshed', lang, username=new_username), show_alert=True)
    except Exception as e:
        logger.error(f"Failed to refresh admin {target_id}: {e}")
        await callback.answer(t('admin_refresh_failed', lang, error=str(e)), show_alert=True)
        
    await show_admin_card(callback.message, target_id, lang, user_id)

@control_router.callback_query(F.data.startswith("ctl_adm_remove_"))
async def process_adm_remove(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    target_id = int(callback.data.split("_")[3])
    if target_id == user_id:
        await callback.answer(t('cannot_remove_self', lang), show_alert=True)
        return
        
    # Check if target is superadmin
    admins = db_manager.get_admins()
    for adm in admins:
        if adm[0] == target_id and adm[2] == "superadmin":
            await callback.answer(t('cannot_remove_superadmin', lang), show_alert=True)
            return
            
    db_manager.remove_admin(target_id)
    await callback.answer(t('admin_removed', lang), show_alert=True)
    await process_manage_admins(callback)

@control_router.callback_query(F.data == "ctl_adm_add")
async def process_adm_add(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    await state.set_state(ControlStates.add_admin_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_manage_admins", style="danger")
    
    await callback.message.edit_text(t('enter_admin_id', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.message(ControlStates.add_admin_id)
async def process_add_admin_id_msg(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await message.answer(t('not_authorized', lang))
        return
        
    target = message.text.strip() if message.text else ""
    
    if not target.isdigit():
        await message.answer("❌ Invalid ID format. Please send a numeric Telegram User ID.")
        return
        
    target_id = int(target)
    await state.update_data(new_admin_id=target_id)
    await state.set_state(ControlStates.add_admin_username)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_manage_admins", style="danger")
    
    await message.answer(t('enter_admin_username', lang), reply_markup=builder.as_markup())

@control_router.message(ControlStates.add_admin_username)
async def process_add_admin_username_msg(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_superadmin(user_id):
        await message.answer(t('not_authorized', lang))
        return
        
    username = message.text.strip() if message.text else ""
    if not username:
        await message.answer("❌ Username cannot be empty. Please send a valid username.")
        return
        
    if username.startswith('@'):
        username = username[1:]
        
    data = await state.get_data()
    target_id = data.get("new_admin_id")
    
    db_manager.add_admin(target_id, username)
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Manage Admins", callback_data="ctl_manage_admins", style="primary")
    builder.button(text="🤖 Main Menu", callback_data="ctl_main_menu", style="primary")
    builder.adjust(1)
    
    await message.answer(t('admin_added', lang), reply_markup=builder.as_markup())

# Verification of Promo Code
@control_router.message(F.chat.type == "private", F.text.startswith("tg-"))
async def process_verify_promo_code(message: Message):
    import time
    code = message.text.strip()
    row = db_manager.get_promo_code(code)
    if not row:
        await message.answer("❌ Code not found or invalid.")
        return
        
    code_val, group_id, user_id, discount_amount, created_at, expires_at, user_name, user_username = row
    now = int(time.time())
    if now >= expires_at:
        db_manager.delete_promo_code(code)
        await message.answer("❌ Code not found or invalid.")
        return
        
    diff = expires_at - now
    hours = diff // 3600
    minutes = (diff % 3600) // 60
    seconds = diff % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
    remaining_str = ", ".join(parts)
    
    username_str = f"@{user_username}" if user_username else "None"
    
    response = (
        f"Discount: {discount_amount}%\n"
        f"Remaining validity duration: {remaining_str}\n"
        f"User ID: {user_id}\n"
        f"Name: {user_name or 'None'}\n"
        f"Username: {username_str}"
    )
    
    await message.answer(response)
    db_manager.delete_promo_code(code)

# ================= BOT SYNCHRONIZATION =================

@control_router.callback_query(F.data == "ctl_sync_bots")
async def process_sync_init(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    bots = db_manager.get_all_postbots()
    active_bots = [b for b in bots if b[4] == 1]  # is_active == 1
    
    if len(active_bots) < 2:
        await callback.answer("❌ You need at least 2 active postbots to synchronize.", show_alert=True)
        return
        
    await state.set_state(ControlStates.sync_select_source)
    
    builder = InlineKeyboardBuilder()
    for b in active_bots:
        builder.button(text=f"@{b[2]}", callback_data=f"ctl_sync_src_{b[0]}")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(t('sync_select_source', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_sync_src_"), StateFilter(ControlStates.sync_select_source))
async def process_sync_src(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    src_bot_id = int(callback.data.split("_")[3])
    
    await state.update_data(src_bot_id=src_bot_id)
    await state.set_state(ControlStates.sync_select_target)
    
    bots = db_manager.get_all_postbots()
    target_bots = [b for b in bots if b[4] == 1 and b[0] != src_bot_id]
    
    builder = InlineKeyboardBuilder()
    for b in target_bots:
        builder.button(text=f"@{b[2]}", callback_data=f"ctl_sync_dst_{b[0]}")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(t('sync_select_target', lang), reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data.startswith("ctl_sync_dst_"), StateFilter(ControlStates.sync_select_target))
async def process_sync_dst(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    dst_bot_id = int(callback.data.split("_")[3])
    
    data = await state.get_data()
    src_bot_id = data.get('src_bot_id')
    
    if src_bot_id == dst_bot_id:
        await callback.answer(t('sync_error_same_bot', lang), show_alert=True)
        return
        
    await state.update_data(dst_bot_id=dst_bot_id)
    
    src_bot = db_manager.get_postbot(src_bot_id)
    dst_bot = db_manager.get_postbot(dst_bot_id)
    
    if not src_bot or not dst_bot:
        await callback.answer("Bot not found.", show_alert=True)
        return
        
    src_groups = db_manager.get_post_groups(src_bot_id)
    if not src_groups:
        await callback.answer(t('sync_error_no_groups', lang), show_alert=True)
        await state.clear()
        await process_sync_init(callback, state)
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_confirm', lang), callback_data="ctl_sync_confirm", style="success")
    builder.button(text=t('btn_cancel', lang), callback_data="ctl_main_menu", style="danger")
    builder.adjust(2)
    
    confirm_text = t('sync_confirm', lang, source=src_bot[2], target=dst_bot[2])
    await callback.message.edit_text(confirm_text, reply_markup=builder.as_markup())
    await callback.answer()

@control_router.callback_query(F.data == "ctl_sync_confirm")
async def process_sync_execution(callback: CallbackQuery, state: FSMContext, bot_manager):
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    if not db_manager.is_admin(user_id):
        await callback.answer(t('not_authorized', lang), show_alert=True)
        return
        
    data = await state.get_data()
    src_bot_id = data.get('src_bot_id')
    dst_bot_id = data.get('dst_bot_id')
    
    await state.clear()
    await callback.answer()
    
    status_msg = callback.message
    await status_msg.edit_text("🔄 <i>Connecting to bots...</i>")
    
    src_bot_row = db_manager.get_postbot(src_bot_id)
    dst_bot_row = db_manager.get_postbot(dst_bot_id)
    
    if not src_bot_row or not dst_bot_row:
        await status_msg.edit_text("❌ Bot not found in database.")
        return
        
    bot_A = bot_manager.running_bots.get(src_bot_id)
    bot_B = bot_manager.running_bots.get(dst_bot_id)
    
    close_A = False
    close_B = False
    
    async def build_temp_bot(row):
        token, proxy = row[1], row[3]
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
        return Bot(token=token, session=session, default=DefaultBotProperties(parse_mode="HTML"))
        
    try:
        if not bot_A:
            bot_A = await build_temp_bot(src_bot_row)
            close_A = True
        if not bot_B:
            bot_B = await build_temp_bot(dst_bot_row)
            close_B = True
            
        await status_msg.edit_text(t('sync_step_check', lang))
        
        src_groups = db_manager.get_post_groups(src_bot_id)
        all_src_chats = []
        for grp in src_groups:
            chats = db_manager.get_chats(grp[0])
            all_src_chats.extend(chats)
            
        unique_chats = {}
        for chat in all_src_chats:
            unique_chats[chat[0]] = chat
            
        missing_chats = []
        for chat_id, chat in unique_chats.items():
            try:
                test_msg = await bot_B.send_message(chat_id=chat_id, text="🔄 <i>Проверка присутствия резервного бота перед синхронизацией...</i>")
                await bot_B.delete_message(chat_id=chat_id, message_id=test_msg.message_id)
            except Exception as e:
                logger.warning(f"Target bot not present in chat {chat[2]} (ID: {chat_id}): {e}")
                missing_chats.append(f"• {chat[2]} (<code>{chat_id}</code>)")
                
        if missing_chats:
            chats_list_str = "\n".join(missing_chats)
            await status_msg.edit_text(t('sync_error_missing_chats', lang, target=dst_bot_row[2], chats=chats_list_str))
            return
            
        await status_msg.edit_text(t('sync_step_groups', lang))
        
        groups_synced_count = 0
        posts_copied_count = 0
        
        import os
        import tempfile
        import asyncio
        from aiogram.types import FSInputFile
        
        temp_dir = tempfile.gettempdir()
        
        for grp in src_groups:
            src_group_id = grp[0]
            name = grp[2]
            passcode = grp[3]
            default_kb = grp[4]
            interval = grp[5]
            time_range = grp[6]
            
            dst_group = db_manager.get_post_group_by_passcode_for_bot(passcode, dst_bot_id)
            promo_settings = db_manager.get_post_group_promo_settings(src_group_id)
            
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            if not dst_group:
                cursor.execute("""
                    INSERT INTO post_groups (
                        bot_id, name, passcode, default_kb, interval, time_range, is_active,
                        promo_enabled, promo_discount_min, promo_discount_max, promo_trigger_emoji,
                        promo_text_instruction, promo_text_success, promo_duration_hours, promo_text_duration,
                        promo_post_duration_hours, promo_post_frequency, promo_post_counter
                    ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    dst_bot_id, name, passcode, default_kb, interval, time_range,
                    promo_settings[0], promo_settings[1], promo_settings[2], promo_settings[3],
                    promo_settings[4], promo_settings[5], promo_settings[6], promo_settings[7],
                    promo_settings[8], promo_settings[9]
                ))
                conn.commit()
                dst_group_id = cursor.lastrowid
            else:
                dst_group_id = dst_group[0]
                cursor.execute("""
                    UPDATE post_groups SET
                        name = ?, default_kb = ?, interval = ?, time_range = ?, is_active = 0,
                        promo_enabled = ?, promo_discount_min = ?, promo_discount_max = ?, promo_trigger_emoji = ?,
                        promo_text_instruction = ?, promo_text_success = ?, promo_duration_hours = ?, promo_text_duration = ?,
                        promo_post_duration_hours = ?, promo_post_frequency = ?
                    WHERE group_id = ?
                """, (
                    name, default_kb, interval, time_range,
                    promo_settings[0], promo_settings[1], promo_settings[2], promo_settings[3],
                    promo_settings[4], promo_settings[5], promo_settings[6], promo_settings[7],
                    promo_settings[8], promo_settings[9], dst_group_id
                ))
                conn.commit()
                
            conn.close()
            groups_synced_count += 1
            
            src_chats = db_manager.get_chats(src_group_id)
            for chat in src_chats:
                db_manager.add_chat(chat[0], dst_group_id, chat[2], chat[3])
                
            src_posts = db_manager.get_posts(src_group_id)
            
            for post in src_posts:
                post_id, _, post_type, file_id, text_msg, kb = post
                
                # Check if post already exists in target group
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT post_id FROM posts WHERE group_id = ? AND type = ? AND text_msg = ?", (dst_group_id, post_type, text_msg))
                existing_post = cursor.fetchone()
                conn.close()
                
                if existing_post:
                    posts_copied_count += 1
                    continue
                    
                current_progress = posts_copied_count + 1
                await status_msg.edit_text(t('sync_step_posts', lang, current=current_progress, total=current_progress))
                
                new_file_id = None
                if post_type in ['photo', 'video', 'animation', 'document'] and file_id:
                    try:
                        sent_msg_A = None
                        if post_type == 'photo':
                            sent_msg_A = await bot_A.send_photo(chat_id=user_id, photo=file_id)
                            file_id_to_download = sent_msg_A.photo[-1].file_id
                        elif post_type == 'video':
                            sent_msg_A = await bot_A.send_video(chat_id=user_id, video=file_id)
                            file_id_to_download = sent_msg_A.video.file_id
                        elif post_type == 'animation':
                            sent_msg_A = await bot_A.send_animation(chat_id=user_id, animation=file_id)
                            file_id_to_download = sent_msg_A.animation.file_id
                        elif post_type == 'document':
                            sent_msg_A = await bot_A.send_document(chat_id=user_id, document=file_id)
                            file_id_to_download = sent_msg_A.document.file_id
                            
                        file_info = await bot_A.get_file(file_id_to_download)
                        temp_file_path = os.path.join(temp_dir, f"temp_media_{post_id}")
                        await bot_A.download_file(file_info.file_path, temp_file_path)
                        
                        sent_msg_B = None
                        if post_type == 'photo':
                            sent_msg_B = await bot_B.send_photo(chat_id=user_id, photo=FSInputFile(temp_file_path))
                            new_file_id = sent_msg_B.photo[-1].file_id
                        elif post_type == 'video':
                            sent_msg_B = await bot_B.send_video(chat_id=user_id, video=FSInputFile(temp_file_path))
                            new_file_id = sent_msg_B.video.file_id
                        elif post_type == 'animation':
                            sent_msg_B = await bot_B.send_animation(chat_id=user_id, animation=FSInputFile(temp_file_path))
                            new_file_id = sent_msg_B.animation.file_id
                        elif post_type == 'document':
                            sent_msg_B = await bot_B.send_document(chat_id=user_id, document=FSInputFile(temp_file_path))
                            new_file_id = sent_msg_B.document.file_id
                            
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                            
                        if sent_msg_A:
                            try:
                                await bot_A.delete_message(chat_id=user_id, message_id=sent_msg_A.message_id)
                            except Exception:
                                pass
                        if sent_msg_B:
                            try:
                                await bot_B.delete_message(chat_id=user_id, message_id=sent_msg_B.message_id)
                            except Exception:
                                pass
                                
                    except Exception as media_err:
                        logger.error(f"Error transferring media for post {post_id}: {media_err}")
                        new_file_id = file_id
                        
                    await asyncio.sleep(3)
                    
                db_manager.add_post(dst_group_id, post_type, new_file_id, text_msg, kb)
                posts_copied_count += 1
                
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_bot_list', lang), callback_data="ctl_bot_list", style="success")
        builder.button(text=t('btn_back', lang), callback_data="ctl_main_menu", style="danger")
        builder.adjust(1)
        
        await status_msg.edit_text(t('sync_success', lang, target=dst_bot_row[2], groups=groups_synced_count, posts=posts_copied_count), reply_markup=builder.as_markup())
        
    except Exception as sync_err:
        logger.error(f"Sync error: {sync_err}")
        await status_msg.edit_text(f"❌ <b>Synchronization Failed!</b>\n\nAn unexpected error occurred during execution: {sync_err}")
        
    finally:
        if close_A and bot_A:
            await bot_A.session.close()
        if close_B and bot_B:
            await bot_B.session.close()

# Hidden Password Handler and Unauthorized Catch-All
@control_router.message(StateFilter(None))
async def process_unauthorized_or_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    lang = db_manager.get_user_lang(user_id)
    
    # Check if the user is already admin
    if db_manager.is_admin(user_id):
        return
        
    required_password = os.getenv("PASSWORD", "Boss2026!")
    if message.text and message.text.strip() == required_password:
        superadmin = db_manager.get_superadmin()
        if not superadmin:
            success = db_manager.add_superadmin(user_id, username)
            if success:
                await state.clear()
                await message.answer(t('success_superadmin', lang), reply_markup=get_main_menu_keyboard(user_id, lang))
            else:
                await message.answer(t('already_has_superadmin', lang))
        else:
            await message.answer(t('already_has_superadmin', lang))
    else:
        await message.answer(t('not_authorized', lang))
