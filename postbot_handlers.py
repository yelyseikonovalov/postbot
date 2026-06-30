import json
import logging
import random
import re
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, MessageReactionUpdated, ReactionTypeEmoji
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatType

import db_manager
from locales import t

logger = logging.getLogger(__name__)
postbot_router = Router()
active_promo_edits = {}

class PostbotStates(StatesGroup):
    # Dynamic bot admin FSM via bot itself
    add_admin_id = State()
    
    # PostGroup FSM Wizard
    create_group_name = State()
    create_group_layout = State()
    create_group_kb_btn_text = State()
    create_group_kb_btn_url = State()
    create_group_passcode = State()
    create_group_interval = State()
    create_group_timerange = State()
    create_group_confirm = State()
    
    # Add Post FSM Wizard
    add_post_content = State()
    add_post_confirm = State()
    
    # Edit PostGroup Settings
    edit_group_interval = State()
    edit_group_timerange = State()
    edit_group_kb_layout = State()
    edit_group_kb_btn_text = State()
    edit_group_kb_btn_url = State()
    
    # Promo FSM Wizard
    promo_discount_range = State()
    promo_trigger_emoji = State()
    promo_post_duration_hours = State()
    promo_post_frequency = State()
    promo_text_instruction = State()
    promo_text_success = State()
    promo_duration_hours = State()
    promo_text_duration = State()
    
    # Edit Chat Title
    edit_chat_title = State()

def validate_time_range(time_range: str) -> bool:
    normalized = "".join(time_range.split())
    if not re.match(r"^\d{2}:\d{2}-\d{2}:\d{2}$", normalized):
        return False
    try:
        start_str, end_str = normalized.split("-")
        sh, sm = map(int, start_str.split(":"))
        eh, em = map(int, end_str.split(":"))
        if not (0 <= sh <= 23 and 0 <= sm <= 59):
            return False
        if eh == 24 and em == 0:
            return True
        if not (0 <= eh <= 23 and 0 <= em <= 59):
            return False
        return True
    except Exception:
        return False

def get_bot_db_id(tg_bot_id: int):
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id FROM postbots WHERE token LIKE ?", (f"{tg_bot_id}:%",))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Helper to verify postbot admin privileges
async def get_authorized_bot_id(message_or_call, bot: Bot):
    bot_db_id = get_bot_db_id(bot.id)
    if not bot_db_id:
        return None
    user_id = message_or_call.from_user.id
    if db_manager.is_postbot_admin(bot_db_id, user_id):
        return bot_db_id
    return None

# Helper to serialize keyboard
def markup_to_json(markup):
    if not markup:
        return "[]"
    keyboard = []
    for row in markup.inline_keyboard:
        row_buttons = []
        for btn in row:
            btn_dict = {"text": btn.text}
            if btn.url:
                btn_dict["url"] = btn.url
            elif btn.callback_data:
                btn_dict["callback_data"] = btn.callback_data
            row_buttons.append(btn_dict)
        keyboard.append(row_buttons)
    return json.dumps(keyboard)

# Helper to deserialize keyboard
def json_to_markup(kb_json):
    if not kb_json or kb_json == "[]":
        return None
    try:
        data = json.loads(kb_json)
        keyboard = []
        for row in data:
            row_buttons = []
            for btn in row:
                if "url" in btn:
                    row_buttons.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
                elif "callback_data" in btn:
                    row_buttons.append(InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]))
            keyboard.append(row_buttons)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    except Exception:
        return None

def build_kb_json_from_list(btn_list, layout_limit):
    rows = []
    current_row = []
    for btn in btn_list:
        current_row.append(btn)
        if len(current_row) == layout_limit:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)
    return json.dumps(rows)

def format_keyboard_schema(kb_json, lang):
    if not kb_json or kb_json == "[]":
        return t('no_keyboard_configured', lang)
    try:
        data = json.loads(kb_json)
        if not data:
            return t('no_keyboard_configured', lang)
        lines = []
        for row in data:
            row_str = " | ".join([f"[{btn['text']}] ({btn.get('url', '')})" for btn in row])
            lines.append(f"<code>{row_str}</code>")
        return "\n".join(lines)
    except Exception:
        return t('no_keyboard_configured', lang)

# Keyboards
def get_start_keyboard(bot_db_id, user_id, lang):
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_postgroups', lang), callback_data="pb_groups_list", style="primary")
    
    # Manage Bot Admins (Owner only)
    if db_manager.is_postbot_owner(bot_db_id, user_id):
        builder.button(text=t('btn_add_admin', lang), callback_data="pb_manage_admins", style="primary")
        
    builder.button(text=t('btn_settings', lang), callback_data="pb_settings_menu", style="primary")
    builder.button(text=t('btn_language', lang), callback_data="pb_lang_menu", style="primary")
    builder.button(text=t('btn_help', lang), callback_data="pb_help", style="primary")
    builder.adjust(1)
    return builder.as_markup()

def get_postgroup_list_keyboard(bot_db_id, lang, page=0):
    builder = InlineKeyboardBuilder()
    groups = db_manager.get_post_groups(bot_db_id)
    
    limit = 8
    total_items = len(groups) if groups else 0
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    page_groups = groups[page * limit : (page + 1) * limit] if groups else []
    for g in page_groups:
        builder.button(text=f"📦 {g[2]}", callback_data=f"pb_group_card_{g[0]}")
        
    sizes = [1] * len(page_groups)
    
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️", callback_data=f"pb_groups_list_page_{page-1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
            
        builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
        
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"pb_groups_list_page_{page+1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
        sizes.append(3)
        
    builder.button(text=t('btn_create_group', lang), callback_data="pb_group_create", style="success")
    builder.button(text=t('btn_back', lang), callback_data="pb_main_menu", style="danger")
    sizes.append(1) # create group
    sizes.append(1) # back
    
    builder.adjust(*sizes)
    return builder.as_markup()

def get_postgroup_card_keyboard(group_id, lang):
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_add_post', lang), callback_data=f"pb_post_add_{group_id}", style="success")
    
    posts = db_manager.get_posts(group_id)
    if len(posts) > 0:
        builder.button(text=t('btn_posts', lang), callback_data=f"pb_post_delany_{group_id}", style="primary")
        
    builder.button(text=t('btn_chats', lang), callback_data=f"pb_group_chats_{group_id}_page_0", style="primary")
    builder.button(text=t('btn_edit_settings', lang), callback_data=f"pb_group_edit_{group_id}", style="primary")
    builder.button(text=t('btn_delete_group', lang), callback_data=f"pb_group_delconf_{group_id}", style="danger")
    builder.button(text=t('btn_back', lang), callback_data="pb_groups_list", style="primary")
    builder.adjust(1)
    return builder.as_markup()

def get_post_pagination_keyboard(posts, index, group_id, lang):
    builder = InlineKeyboardBuilder()
    prev_idx = (index - 1) % len(posts)
    next_idx = (index + 1) % len(posts)
    
    builder.button(text="⬅️", callback_data=f"pb_page_{group_id}_{prev_idx}", style="primary")
    builder.button(text=t('btn_back', lang), callback_data=f"pb_group_card_{group_id}", style="primary")
    builder.button(text="➡️", callback_data=f"pb_page_{group_id}_{next_idx}", style="primary")
    
    post_id = posts[index][0]
    builder.button(text=t('btn_confirm_delete', lang), callback_data=f"pb_postdelete_{group_id}_{post_id}_{index}", style="danger")
    builder.button(text=t('btn_del_all_posts', lang), callback_data=f"pb_post_delall_{group_id}", style="danger")
    builder.adjust(3, 1, 1)
    return builder.as_markup()

# Command /start /menu
@postbot_router.message(Command("start", "menu"), F.chat.type == ChatType.PRIVATE)
async def process_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    bot_db_id = get_bot_db_id(bot.id)
    if not bot_db_id:
        return
        
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_postbot_admin(bot_db_id, user_id):
        # We don't say anything, it's a client bot that should ignore unauthorized users
        return
        
    await message.answer(
        t('menu_title', lang),
        reply_markup=get_start_keyboard(bot_db_id, user_id, lang)
    )



# Callback Main Menu
@postbot_router.callback_query(F.data == "pb_main_menu")
async def cb_main_menu(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    await state.clear()
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    await callback.message.edit_text(t('menu_title', lang), reply_markup=get_start_keyboard(bot_db_id, user_id, lang))
    await callback.answer()

# Language Menu
@postbot_router.callback_query(F.data == "pb_lang_menu")
async def cb_lang_menu(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English" + (" ✅" if lang == "en" else ""), callback_data="pb_set_lang_en", style="primary")
    builder.button(text="🇷🇺 Русский" + (" ✅" if lang == "ru" else ""), callback_data="pb_set_lang_ru", style="primary")
    builder.button(text="🇮🇱 עברית" + (" ✅" if lang == "he" else ""), callback_data="pb_set_lang_he", style="primary")
    builder.button(text=t('btn_back', lang), callback_data="pb_main_menu", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(t('select_language', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_set_lang_"))
async def cb_set_lang(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    user_id = callback.from_user.id
    lang_code = callback.data.split("_")[3]
    username = callback.from_user.username or "unknown"
    
    db_manager.set_user_lang(user_id, username, lang_code)
    await callback.message.edit_text(t('menu_title', lang_code), reply_markup=get_start_keyboard(bot_db_id, user_id, lang_code))
    await callback.answer()

# Callback Help
@postbot_router.callback_query(F.data.startswith("pb_help"))
async def cb_help(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    user_id = callback.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    page = 0
    if callback.data.startswith("pb_help_page_"):
        try:
            page = int(callback.data.split("_")[3])
        except (IndexError, ValueError):
            page = 0
            
    total_pages = 3
    page = max(0, min(page, total_pages - 1))
    
    page_key = f"pb_help_page_{page + 1}"
    text = t('help_title', lang) + "\n\n" + t(page_key, lang)
    
    builder = InlineKeyboardBuilder()
    
    # Navigation row
    if page > 0:
        builder.button(text="⬅️", callback_data=f"pb_help_page_{page-1}", style="primary")
    else:
        builder.button(text=" ", callback_data="dummy")
        
    builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
    
    if page < total_pages - 1:
        builder.button(text="➡️", callback_data=f"pb_help_page_{page+1}", style="primary")
    else:
        builder.button(text=" ", callback_data="dummy")
        
    builder.button(text=t('btn_back', lang), callback_data="pb_main_menu", style="danger")
    
    builder.adjust(3, 1)
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# ================= POSTGROUPS LIST & CARD =================

@postbot_router.callback_query(F.data == "dummy")
async def process_dummy(callback: CallbackQuery):
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_groups_list"))
async def cb_groups_list(callback: CallbackQuery, bot: Bot, state: FSMContext = None):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    if state:
        await state.clear()
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    page = 0
    if callback.data.startswith("pb_groups_list_page_"):
        page = int(callback.data.split("_")[4])
        
    await callback.message.edit_text(t('pg_list_title', lang, username=bot.username), reply_markup=get_postgroup_list_keyboard(bot_db_id, lang, page))
    await callback.answer()

async def send_or_edit_group_card(message_or_call, bot: Bot, group_id: int, edit: bool = False):
    lang = db_manager.get_user_lang(message_or_call.from_user.id)
    group_row = db_manager.get_post_group(group_id)
    if not group_row:
        return
        
    # group_row: group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active
    _, _, name, passcode, default_kb, interval, time_range, is_active = group_row
    
    posts = db_manager.get_posts(group_id)
    chats = db_manager.get_chats(group_id)
    
    promo_settings = db_manager.get_post_group_promo_settings(group_id)
    promo_enabled = promo_settings[0] if promo_settings else 0
    promo_status_str = t('status_enabled', lang) if promo_enabled else t('status_disabled', lang)
    
    kb_schema = format_keyboard_schema(default_kb, lang)
    status_str = t('status_enabled', lang) if is_active else t('status_disabled', lang)
    text = t(
        'pg_card', lang,
        name=name,
        passcode=passcode,
        status=status_str,
        promo_status=promo_status_str,
        post_count=len(posts),
        interval=interval,
        time_range=time_range,
        chat_count=len(chats),
        kb_schema=kb_schema
    )
    
    kb_markup = get_postgroup_card_keyboard(group_id, lang)
    
    if edit and isinstance(message_or_call, CallbackQuery):
        try:
            await message_or_call.message.edit_text(text, reply_markup=kb_markup)
        except Exception as e:
            err_str = str(e).lower()
            if "message is not modified" in err_str:
                pass
            else:
                try:
                    await message_or_call.message.delete()
                except Exception:
                    pass
                await message_or_call.message.answer(text, reply_markup=kb_markup)
    else:
        if isinstance(message_or_call, CallbackQuery):
            await message_or_call.message.answer(text, reply_markup=kb_markup)
        else:
            await message_or_call.answer(text, reply_markup=kb_markup)

@postbot_router.callback_query(F.data.startswith("pb_group_card_"))
async def cb_group_card(callback: CallbackQuery, bot: Bot, group_id: int = None):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    if group_id is None:
        group_id = int(callback.data.split("_")[3])
        
    await send_or_edit_group_card(callback, bot, group_id, edit=True)
    await callback.answer()

# ================= POSTGROUP CHATS MANAGEMENT =================

async def show_group_chats(callback: CallbackQuery, bot: Bot, group_id: int, page: int):
    lang = db_manager.get_user_lang(callback.from_user.id)
    group_row = db_manager.get_post_group(group_id)
    if not group_row:
        await callback.answer("Group not found.", show_alert=True)
        return
        
    group_name = group_row[2]
    chats = db_manager.get_chats(group_id)
    
    limit = 8
    total_items = len(chats) if chats else 0
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    builder = InlineKeyboardBuilder()
    page_chats = []
    
    if chats:
        start_idx = page * limit
        end_idx = start_idx + limit
        page_chats = chats[start_idx:end_idx]
        for c in page_chats:
            c_id, _, c_title, c_user, _ = c
            display_name = c_title or f"ID: {c_id}"
            builder.button(text=f"📢 {display_name}", callback_data=f"pb_chat_card_{group_id}_{c_id}")
            
    sizes = [1] * len(page_chats)
    
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️", callback_data=f"pb_group_chats_{group_id}_page_{page-1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
            
        builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
        
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"pb_group_chats_{group_id}_page_{page+1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
        sizes.append(3)
        
    builder.button(text=t('btn_refresh_chats', lang), callback_data=f"pb_chats_refresh_{group_id}", style="success")
    builder.button(text=t('btn_back', lang), callback_data=f"pb_group_card_{group_id}", style="primary")
    sizes.append(1) # Refresh
    sizes.append(1) # Back
    
    builder.adjust(*sizes)
    
    text = t('chats_list_title', lang, group_name=group_name)
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except Exception as e:
        logger.debug(f"Failed to edit chat list message: {e}")
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_group_chats_"))
async def cb_group_chats(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    parts = callback.data.split("_")
    group_id = int(parts[3])
    page = 0
    if len(parts) >= 6 and parts[4] == "page":
        page = int(parts[5])
        
    await show_group_chats(callback, bot, group_id, page)

@postbot_router.callback_query(F.data.startswith("pb_chats_refresh_"))
async def cb_chats_refresh(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    chats = db_manager.get_chats(group_id)
    refreshed_count = 0
    failed_count = 0
    
    for c in chats:
        c_id, _, _, _, _ = c
        try:
            chat_info = await bot.get_chat(c_id)
            title = chat_info.title
            username = chat_info.username
            db_manager.update_chat_details(c_id, group_id, title, username)
            refreshed_count += 1
        except Exception as e:
            logger.warning(f"Failed to refresh chat {c_id}: {e}")
            failed_count += 1
            
    await callback.answer(f"Refreshed: {refreshed_count}, Failed: {failed_count}")
    await show_group_chats(callback, bot, group_id, 0)

@postbot_router.callback_query(F.data.startswith("pb_chat_card_"))
async def cb_chat_card(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    parts = callback.data.split("_")
    group_id = int(parts[3])
    chat_id = int(parts[4])
    
    chat_row = db_manager.get_chat(chat_id, group_id)
    if not chat_row:
        await callback.answer("Chat connection not found.", show_alert=True)
        return
        
    c_id, _, c_title, c_user, _ = chat_row
    
    member_count = "N/A"
    try:
        member_count = await bot.get_chat_member_count(c_id)
    except Exception as e:
        logger.warning(f"Failed to get member count for {c_id}: {e}")
        
    text = t(
        'chat_details_title', lang,
        title=c_title or "None",
        username=f"@{c_user}" if c_user else "None",
        chat_id=c_id,
        member_count=member_count
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_edit_title', lang), callback_data=f"pb_chat_edit_title_{group_id}_{chat_id}", style="primary")
    builder.button(text=t('btn_transfer', lang), callback_data=f"pb_chat_transfer_{group_id}_{chat_id}", style="primary")
    builder.button(text=t('btn_unlink', lang), callback_data=f"pb_chat_unlink_{group_id}_{chat_id}", style="danger")
    builder.button(text=t('btn_back', lang), callback_data=f"pb_group_chats_{group_id}_page_0", style="primary")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_chat_edit_title_"))
async def cb_chat_edit_title(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    parts = callback.data.split("_")
    group_id = int(parts[4])
    chat_id = int(parts[5])
    
    await state.set_state(PostbotStates.edit_chat_title)
    await state.update_data(target_group_id=group_id, target_chat_id=chat_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_chat_card_{group_id}_{chat_id}", style="danger")
    
    await callback.message.edit_text(t('enter_new_chat_title', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.edit_chat_title)
async def process_new_chat_title(message: Message, state: FSMContext, bot: Bot):
    bot_db_id = get_bot_db_id(bot.id)
    if not bot_db_id:
        return
        
    user_id = message.from_user.id
    lang = db_manager.get_user_lang(user_id)
    
    if not db_manager.is_postbot_admin(bot_db_id, user_id):
        return
        
    new_title = message.text.strip() if message.text else ""
    if not new_title:
        await message.answer("❌ Title cannot be empty. Please enter a valid title.")
        return
        
    state_data = await state.get_data()
    group_id = state_data.get("target_group_id")
    chat_id = state_data.get("target_chat_id")
    
    chat_row = db_manager.get_chat(chat_id, group_id)
    if not chat_row:
        await message.answer("Chat not found.")
        await state.clear()
        return
        
    try:
        await bot.set_chat_title(chat_id, new_title)
        db_manager.update_chat_details(chat_id, group_id, new_title, chat_row[3])
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📋 Chat Details", callback_data=f"pb_chat_card_{group_id}_{chat_id}", style="primary")
        builder.button(text="🤖 Main Menu", callback_data="pb_main_menu", style="primary")
        builder.adjust(1)
        
        await message.answer(t('chat_title_updated', lang), reply_markup=builder.as_markup())
        await state.clear()
    except Exception as e:
        logger.error(f"Failed to set chat title for {chat_id}: {e}")
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data=f"pb_chat_card_{group_id}_{chat_id}", style="danger")
        await message.answer(f"❌ Failed to change title on Telegram. Make sure the bot has 'Change Channel/Group Info' administrator permission.\n\nError details: {e}", reply_markup=builder.as_markup())

@postbot_router.callback_query(F.data.startswith("pb_chat_unlink_"))
async def cb_chat_unlink(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    parts = callback.data.split("_")
    group_id = int(parts[3])
    chat_id = int(parts[4])
    
    db_manager.delete_chat(chat_id, group_id)
    await callback.answer(t('chat_unlinked', lang), show_alert=True)
    
    # Redirect back to chats list
    callback.data = f"pb_group_chats_{group_id}_page_0"
    await cb_group_chats(callback, bot)

@postbot_router.callback_query(F.data.startswith("pb_chat_transfer_"))
async def cb_chat_transfer(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    parts = callback.data.split("_")
    group_id = int(parts[3])
    chat_id = int(parts[4])
    
    page = 0
    if len(parts) >= 7 and parts[5] == "page":
        page = int(parts[6])
        
    groups = db_manager.get_post_groups(bot_db_id)
    other_groups = [g for g in groups if g[0] != group_id]
    
    if not other_groups:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_back', lang), callback_data=f"pb_chat_card_{group_id}_{chat_id}", style="primary")
        builder.adjust(1)
        await callback.message.edit_text(t('no_other_groups', lang), reply_markup=builder.as_markup())
        await callback.answer()
        return
        
    limit = 8
    total_items = len(other_groups)
    total_pages = (total_items + limit - 1) // limit
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    builder = InlineKeyboardBuilder()
    
    start_idx = page * limit
    end_idx = start_idx + limit
    page_groups = other_groups[start_idx:end_idx]
    
    for g in page_groups:
        dest_group_id = g[0]
        dest_group_name = g[2]
        builder.button(text=f"📦 {dest_group_name}", callback_data=f"pb_chat_dotrans_{group_id}_{chat_id}_{dest_group_id}")
        
    sizes = [1] * len(page_groups)
    
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️", callback_data=f"pb_chat_transfer_{group_id}_{chat_id}_page_{page-1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
            
        builder.button(text=f"{page+1}/{total_pages}", callback_data="dummy")
        
        if page < total_pages - 1:
            builder.button(text="➡️", callback_data=f"pb_chat_transfer_{group_id}_{chat_id}_page_{page+1}", style="primary")
        else:
            builder.button(text=" ", callback_data="dummy")
        sizes.append(3)
        
    builder.button(text=t('btn_back', lang), callback_data=f"pb_chat_card_{group_id}_{chat_id}", style="primary")
    sizes.append(1)
    
    builder.adjust(*sizes)
    
    text = t('select_transfer_group', lang)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_chat_dotrans_"))
async def cb_chat_do_transfer(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    parts = callback.data.split("_")
    src_group_id = int(parts[3])
    chat_id = int(parts[4])
    dest_group_id = int(parts[5])
    
    dest_group_row = db_manager.get_post_group(dest_group_id)
    if not dest_group_row:
        await callback.answer("Destination group not found.", show_alert=True)
        return
        
    dest_group_name = dest_group_row[2]
    
    db_manager.update_chat_group(chat_id, src_group_id, dest_group_id)
    
    await callback.answer(t('chat_transferred', lang, group_name=dest_group_name), show_alert=True)
    await cb_group_card(callback, bot, group_id=dest_group_id)

# ================= CREATE POSTGROUP WIZARD =================

@postbot_router.callback_query(F.data == "pb_group_create")
async def cb_group_create(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    await state.set_state(PostbotStates.create_group_name)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    
    await callback.message.edit_text(t('create_group_name', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.create_group_name)
async def process_create_group_name(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    name = message.text.strip() if message.text else ""
    if not name:
        await message.answer("❌ Name cannot be empty.")
        return
        
    await state.update_data(name=name)
    await state.set_state(PostbotStates.create_group_layout)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    builder.adjust(1)
    
    await message.answer(t('create_group_layout', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.create_group_layout)
async def process_create_group_layout(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    
    if text == "0":
        # No keyboard
        await state.update_data(layout_str="0", layout_list=[], positions=[], current_btn_idx=0, buttons_flat=[], default_kb="[]")
        await state.set_state(PostbotStates.create_group_passcode)
        
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
        builder.adjust(1)
        
        await message.answer(t('create_group_passcode', lang), reply_markup=builder.as_markup())
        return
        
    import re
    if not re.match(r"^[1-8](-[1-8])*$", text):
        await message.answer(t('invalid_layout_schema', lang))
        return
        
    layout_list = [int(x) for x in text.split("-")]
    positions = []
    for r_idx, num_btns in enumerate(layout_list):
        for c_idx in range(num_btns):
            positions.append((r_idx + 1, c_idx + 1))
            
    await state.update_data(
        layout_str=text,
        layout_list=layout_list,
        positions=positions,
        current_btn_idx=0,
        buttons_flat=[]
    )
    
    await state.set_state(PostbotStates.create_group_kb_btn_text)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    builder.adjust(1)
    
    await message.answer(
        t('create_group_kb_btn_text_prompt', lang, row=1, col=1),
        reply_markup=builder.as_markup()
    )

@postbot_router.message(PostbotStates.create_group_kb_btn_text)
async def process_kb_btn_text(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    btn_text = message.text.strip() if message.text else ""
    if not btn_text:
        await message.answer("❌ Button text cannot be empty.")
        return
        
    await state.update_data(current_btn_text=btn_text)
    await state.set_state(PostbotStates.create_group_kb_btn_url)
    
    data = await state.get_data()
    positions = data['positions']
    current_btn_idx = data['current_btn_idx']
    row, col = positions[current_btn_idx]
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    builder.adjust(1)
    
    await message.answer(
        t('create_group_kb_btn_url_prompt', lang, row=row, col=col),
        reply_markup=builder.as_markup()
    )

@postbot_router.message(PostbotStates.create_group_kb_btn_url)
async def process_kb_btn_url(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    url = message.text.strip() if message.text else ""
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("t.me/")):
        await message.answer("❌ Invalid URL. It must start with http:// or https://")
        return
        
    data = await state.get_data()
    btn_text = data['current_btn_text']
    buttons_flat = data.get('buttons_flat', [])
    buttons_flat.append({"text": btn_text, "url": url})
    
    positions = data['positions']
    current_btn_idx = data['current_btn_idx'] + 1
    
    await state.update_data(buttons_flat=buttons_flat, current_btn_idx=current_btn_idx)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    builder.adjust(1)
    
    if current_btn_idx < len(positions):
        await state.set_state(PostbotStates.create_group_kb_btn_text)
        row, col = positions[current_btn_idx]
        await message.answer(
            t('create_group_kb_btn_text_prompt', lang, row=row, col=col),
            reply_markup=builder.as_markup()
        )
    else:
        layout_list = data['layout_list']
        keyboard_rows = []
        flat_idx = 0
        for num_btns in layout_list:
            row_btns = []
            for _ in range(num_btns):
                row_btns.append(buttons_flat[flat_idx])
                flat_idx += 1
            keyboard_rows.append(row_btns)
        default_kb = json.dumps(keyboard_rows)
        
        await state.update_data(default_kb=default_kb)
        await state.set_state(PostbotStates.create_group_passcode)
        
        await message.answer(
            t('create_group_passcode', lang),
            reply_markup=builder.as_markup()
        )

@postbot_router.message(PostbotStates.create_group_passcode)
async def process_create_passcode(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    passcode = message.text.strip() if message.text else ""
    if not passcode:
        return
        
    # Check if passcode is unique for this bot
    existing = db_manager.get_post_group_by_passcode_for_bot(passcode, bot_db_id)
    if existing:
        await message.answer(t('duplicate_passcode', lang))
        return
        
    await state.update_data(passcode=passcode)
    await state.set_state(PostbotStates.create_group_interval)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    
    await message.answer(t('create_group_interval', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.create_group_interval)
async def process_create_interval(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    interval_str = message.text.strip() if message.text else ""
    if not interval_str.isdigit() or int(interval_str) < 60:
        await message.answer(t('invalid_interval', lang))
        return
        
    await state.update_data(interval=int(interval_str))
    await state.set_state(PostbotStates.create_group_timerange)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    
    await message.answer(t('create_group_timerange', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.create_group_timerange)
async def process_create_timerange(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    time_range = "".join(message.text.split()) if message.text else ""
    
    # Format validation
    if not validate_time_range(time_range):
        await message.answer(t('invalid_time_range', lang))
        return
        
    await state.update_data(time_range=time_range)
    data = await state.get_data()
    
    default_kb = data.get('default_kb', '[]')
    kb_schema = format_keyboard_schema(default_kb, lang)
    
    text = t(
        'create_group_confirm', lang,
        name=data['name'],
        layout=data.get('layout_str', '0'),
        passcode=data['passcode'],
        interval=data['interval'],
        time_range=data['time_range'],
        buttons=kb_schema
    )
    
    await state.set_state(PostbotStates.create_group_confirm)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_confirm', lang), callback_data="pb_confirm_create_group", style="success")
    builder.button(text=t('btn_cancel', lang), callback_data="pb_groups_list", style="danger")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

@postbot_router.callback_query(PostbotStates.create_group_confirm, F.data == "pb_confirm_create_group")
async def cb_confirm_create_group(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    data = await state.get_data()
    default_kb = data.get('default_kb', '[]')
    
    gid = db_manager.add_post_group(
        bot_db_id,
        data['name'],
        data['passcode'],
        default_kb,
        data['interval'],
        data['time_range']
    )
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    if gid:
        await callback.message.edit_text(t('group_added_success', lang), reply_markup=get_postgroup_list_keyboard(bot_db_id, lang))
    else:
        await callback.message.edit_text("❌ An error occurred while saving the group.", reply_markup=get_postgroup_list_keyboard(bot_db_id, lang))
        
    await state.clear()
    await callback.answer()

# ================= DELETE POSTGROUP =================

@postbot_router.callback_query(F.data.startswith("pb_group_delconf_"))
async def cb_group_delconf(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    group_row = db_manager.get_post_group(group_id)
    if not group_row:
        await callback.answer("Group not found.", show_alert=True)
        return
        
    lang = db_manager.get_user_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_confirm_delete', lang), callback_data=f"pb_group_delete_{group_id}", style="danger")
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="primary")
    builder.adjust(1)
    
    await callback.message.edit_text(t('confirm_delete_group', lang, name=group_row[2]), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_group_delete_"))
async def cb_group_delete(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    db_manager.delete_post_group(group_id)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    await callback.answer(t('group_deleted', lang), show_alert=True)
    await callback.message.edit_text(t('pg_list_title', lang, username=bot.username), reply_markup=get_postgroup_list_keyboard(bot_db_id, lang))

# ================= ADD POST TO POSTGROUP (FSM) =================

@postbot_router.callback_query(F.data.startswith("pb_post_add_"))
async def cb_post_add(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    await state.update_data(target_group_id=group_id)
    await state.set_state(PostbotStates.add_post_content)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    
    await callback.message.edit_text(t('add_post_start', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.add_post_content)
async def process_add_post_content(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    content_type = message.content_type
    file_id = None
    text_msg = message.caption or message.text
    
    if message.photo:
        file_id = message.photo[-1].file_id
        type_ = "photo"
    elif message.video:
        file_id = message.video.file_id
        type_ = "video"
    elif message.animation:
        file_id = message.animation.file_id
        type_ = "animation"
    elif message.document:
        file_id = message.document.file_id
        type_ = "document"
    else:
        type_ = "text"
        
    kb_json = "[]"
    if message.reply_markup:
        kb_json = markup_to_json(message.reply_markup)
        
    await state.update_data(post_type=type_, file_id=file_id, text_msg=text_msg, kb_json=kb_json)
    await state.set_state(PostbotStates.add_post_confirm)
    
    lang = db_manager.get_user_lang(message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_confirm', lang), callback_data="pb_confirm_add_post", style="success")
    builder.button(text=t('btn_cancel', lang), callback_data="pb_main_menu", style="danger")
    builder.adjust(1)
    
    await message.answer(t('add_post_confirm', lang), reply_markup=builder.as_markup())

@postbot_router.callback_query(PostbotStates.add_post_confirm, F.data == "pb_confirm_add_post")
async def cb_confirm_add_post(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    data = await state.get_data()
    group_id = data['target_group_id']
    
    # If no custom keyboard is provided, keep it empty "[]" to dynamically use group's default_kb at send time
    kb_json = data.get('kb_json', '[]')
            
    db_manager.add_post(
        group_id,
        data['post_type'],
        data['file_id'],
        data['text_msg'],
        kb_json
    )
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    await callback.message.edit_text(t('post_added_to_group', lang), reply_markup=get_postgroup_card_keyboard(group_id, lang))
    await state.clear()
    await callback.answer()

# ================= DELETE POSTS PAGINATION =================

@postbot_router.callback_query(F.data.startswith("pb_post_delall_"))
async def cb_post_delall(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    group_id = int(callback.data.split("_")[3])
    db_manager.delete_all_posts(group_id)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    await callback.answer(t('group_deleted', lang), show_alert=True)
    # Re-render card
    await cb_group_card(callback, bot, group_id=group_id)

@postbot_router.callback_query(F.data.startswith("pb_post_delany_"))
async def cb_post_delany(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    group_id = int(callback.data.split("_")[3])
    posts = db_manager.get_posts(group_id)
    if not posts:
        await callback.answer("No posts to delete.", show_alert=True)
        return
        
    await render_post_for_deletion(callback.message, posts, 0, group_id, bot)
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_page_"))
async def cb_page_navigate(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    parts = callback.data.split("_")
    group_id = int(parts[2])
    index = int(parts[3])
    
    posts = db_manager.get_posts(group_id)
    if not posts:
        await callback.answer("No posts.", show_alert=True)
        return
        
    await render_post_for_deletion(callback.message, posts, index, group_id, bot)
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_postdelete_"))
async def cb_post_delete(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    parts = callback.data.split("_")
    group_id = int(parts[2])
    post_id = int(parts[3])
    current_idx = int(parts[4])
    
    db_manager.delete_post(post_id)
    posts = db_manager.get_posts(group_id)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    if not posts:
        await callback.message.delete()
        await callback.message.answer("🗑️ All posts deleted.", reply_markup=get_postgroup_card_keyboard(group_id, lang))
    else:
        new_idx = min(current_idx, len(posts) - 1)
        await render_post_for_deletion(callback.message, posts, new_idx, group_id, bot)
        
    await callback.answer()

async def render_post_for_deletion(message: Message, posts, index, group_id, bot: Bot):
    post = posts[index]
    _, _, type_, file_id, text_msg, kb_json = post
    lang = db_manager.get_user_lang(message.chat.id)
    
    preview_header = f"📋 <b>Post {index+1}/{len(posts)}</b>\n\n"
    kb_markup = get_post_pagination_keyboard(posts, index, group_id, lang)
    
    try:
        await message.delete()
    except Exception:
        pass
        
    if type_ == "photo":
        await message.answer_photo(photo=file_id, caption=preview_header + (text_msg or ""), reply_markup=kb_markup)
    elif type_ == "video":
        await message.answer_video(video=file_id, caption=preview_header + (text_msg or ""), reply_markup=kb_markup)
    elif type_ == "animation":
        await message.answer_animation(animation=file_id, caption=preview_header + (text_msg or ""), reply_markup=kb_markup)
    elif type_ == "document":
        await message.answer_document(document=file_id, caption=preview_header + (text_msg or ""), reply_markup=kb_markup)
    else:
        await message.answer(text=preview_header + (text_msg or ""), reply_markup=kb_markup)

# ================= EDIT SETTINGS =================

@postbot_router.callback_query(F.data.startswith("pb_group_edit_"))
async def cb_group_edit(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    group_row = db_manager.get_post_group(group_id)
    is_active = group_row[7] if len(group_row) > 7 else 1
    
    toggle_text = t('btn_toggle_posting_off', lang) if is_active else t('btn_toggle_posting_on', lang)
    toggle_style = "danger" if is_active else "success"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=toggle_text, callback_data=f"pb_group_toggle_{group_id}", style=toggle_style)
    builder.button(text=t('btn_edit_interval', lang), callback_data=f"pb_ed_int_{group_id}", style="primary")
    builder.button(text=t('btn_edit_timerange', lang), callback_data=f"pb_ed_time_{group_id}", style="primary")
    builder.button(text=t('btn_edit_kb', lang), callback_data=f"pb_ed_kb_{group_id}", style="primary")
    builder.button(text=t('btn_promo_settings', lang), callback_data=f"pb_promo_menu_{group_id}", style="primary")
    builder.button(text=t('btn_back', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(t('edit_settings_menu', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_group_toggle_"))
async def cb_group_toggle(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    group_row = db_manager.get_post_group(group_id)
    if not group_row:
        await callback.answer("Group not found.", show_alert=True)
        return
        
    is_active = group_row[7] if len(group_row) > 7 else 1
    new_active = 0 if is_active else 1
    
    db_manager.update_post_group_active(group_id, new_active)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    await callback.answer(t('status_enabled', lang) if new_active else t('status_disabled', lang))
    await cb_group_edit(callback, bot)

@postbot_router.callback_query(F.data.startswith("pb_ed_int_"))
async def cb_ed_int(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    await state.update_data(edit_group_id=group_id)
    await state.set_state(PostbotStates.edit_group_interval)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    
    await callback.message.edit_text(t('enter_interval', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.edit_group_interval)
async def process_edit_interval(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    if not text.isdigit() or int(text) < 60:
        await message.answer(t('invalid_interval', lang))
        return
        
    data = await state.get_data()
    group_id = data['edit_group_id']
    db_manager.update_post_group_interval(group_id, int(text))
    
    await state.clear()
    await message.answer(t('interval_updated', lang))
    await send_or_edit_group_card(message, bot, group_id)

@postbot_router.callback_query(F.data.startswith("pb_ed_time_"))
async def cb_ed_time(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    await state.update_data(edit_group_id=group_id)
    await state.set_state(PostbotStates.edit_group_timerange)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    
    await callback.message.edit_text(t('enter_timerange', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.edit_group_timerange)
async def process_edit_timerange(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    text = "".join(message.text.split()) if message.text else ""
    if not validate_time_range(text):
        await message.answer(t('invalid_time_range', lang))
        return
        
    data = await state.get_data()
    group_id = data['edit_group_id']
    db_manager.update_post_group_time_range(group_id, text)
    
    await state.clear()
    await message.answer(t('timerange_updated', lang))
    await send_or_edit_group_card(message, bot, group_id)

# ================= EDIT KEYBOARD WIZARD =================

@postbot_router.callback_query(F.data.startswith("pb_ed_kb_"))
async def cb_ed_kb(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    await state.update_data(edit_group_id=group_id)
    await state.set_state(PostbotStates.edit_group_kb_layout)
    
    lang = db_manager.get_user_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    
    await callback.message.edit_text(t('create_group_layout', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.edit_group_kb_layout)
async def process_edit_kb_layout(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    data = await state.get_data()
    group_id = data['edit_group_id']
    
    if text == "0":
        db_manager.update_post_group_default_kb(group_id, "[]")
        await state.clear()
        await message.answer(t('btn_edit_kb_success', lang))
        await send_or_edit_group_card(message, bot, group_id)
        return
        
    import re
    if not re.match(r"^[1-8](-[1-8])*$", text):
        await message.answer(t('invalid_layout_schema', lang))
        return
        
    layout_list = [int(x) for x in text.split("-")]
    positions = []
    for r_idx, num_btns in enumerate(layout_list):
        for c_idx in range(num_btns):
            positions.append((r_idx + 1, c_idx + 1))
            
    await state.update_data(
        layout_str=text,
        layout_list=layout_list,
        positions=positions,
        current_btn_idx=0,
        buttons_flat=[]
    )
    
    await state.set_state(PostbotStates.edit_group_kb_btn_text)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    builder.adjust(1)
    
    await message.answer(
        t('create_group_kb_btn_text_prompt', lang, row=1, col=1),
        reply_markup=builder.as_markup()
    )

@postbot_router.message(PostbotStates.edit_group_kb_btn_text)
async def process_edit_kb_btn_text(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    btn_text = message.text.strip() if message.text else ""
    if not btn_text:
        await message.answer("❌ Button text cannot be empty.")
        return
        
    await state.update_data(current_btn_text=btn_text)
    await state.set_state(PostbotStates.edit_group_kb_btn_url)
    
    data = await state.get_data()
    group_id = data['edit_group_id']
    positions = data['positions']
    current_btn_idx = data['current_btn_idx']
    row, col = positions[current_btn_idx]
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    builder.adjust(1)
    
    await message.answer(
        t('create_group_kb_btn_url_prompt', lang, row=row, col=col),
        reply_markup=builder.as_markup()
    )

@postbot_router.message(PostbotStates.edit_group_kb_btn_url)
async def process_edit_kb_btn_url(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
        
    lang = db_manager.get_user_lang(message.from_user.id)
    url = message.text.strip() if message.text else ""
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("t.me/")):
        await message.answer("❌ Invalid URL. It must start with http:// or https://")
        return
        
    data = await state.get_data()
    group_id = data['edit_group_id']
    btn_text = data['current_btn_text']
    buttons_flat = data.get('buttons_flat', [])
    buttons_flat.append({"text": btn_text, "url": url})
    
    positions = data['positions']
    current_btn_idx = data['current_btn_idx'] + 1
    
    await state.update_data(buttons_flat=buttons_flat, current_btn_idx=current_btn_idx)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_group_card_{group_id}", style="danger")
    builder.adjust(1)
    
    if current_btn_idx < len(positions):
        await state.set_state(PostbotStates.edit_group_kb_btn_text)
        row, col = positions[current_btn_idx]
        await message.answer(
            t('create_group_kb_btn_text_prompt', lang, row=row, col=col),
            reply_markup=builder.as_markup()
        )
    else:
        layout_list = data['layout_list']
        keyboard_rows = []
        flat_idx = 0
        for num_btns in layout_list:
            row_btns = []
            for _ in range(num_btns):
                row_btns.append(buttons_flat[flat_idx])
                flat_idx += 1
            keyboard_rows.append(row_btns)
        default_kb = json.dumps(keyboard_rows)
        
        db_manager.update_post_group_default_kb(group_id, default_kb)
        await state.clear()
        
        await message.answer(t('btn_edit_kb_success', lang))
        await send_or_edit_group_card(message, bot, group_id)

# ================= POSTBOT ADMIN MANAGEMENT (INSIDE POSTBOT) =================

@postbot_router.callback_query(F.data == "pb_manage_admins")
async def cb_manage_admins(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    user_id = callback.from_user.id
    if not db_manager.is_postbot_owner(bot_db_id, user_id):
        return
        
    lang = db_manager.get_user_lang(user_id)
    admins = db_manager.get_postbot_admins(bot_db_id)
    
    builder = InlineKeyboardBuilder()
    for adm in admins:
        adm_id, adm_user, adm_role = adm
        if adm_role == "owner":
            builder.button(text=f"👑 @{adm_user} (Owner)", callback_data="dummy")
        else:
            builder.button(text=f"🗑️ Remove @{adm_user}", callback_data=f"pb_adm_remove_{adm_id}", style="danger")
            
    builder.button(text=t('btn_add_new_admin', lang), callback_data="pb_adm_add", style="success")
    builder.button(text=t('btn_back', lang), callback_data="pb_main_menu", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(t('postbot_admin_list_title', lang, username=bot.username), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_adm_remove_"))
async def cb_adm_remove(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    user_id = callback.from_user.id
    if not db_manager.is_postbot_owner(bot_db_id, user_id):
        return
        
    target_id = int(callback.data.split("_")[3])
    db_manager.remove_postbot_admin(bot_db_id, target_id)
    
    lang = db_manager.get_user_lang(user_id)
    await callback.answer(t('admin_removed', lang), show_alert=True)
    
    await cb_manage_admins(callback, bot)

@postbot_router.callback_query(F.data == "pb_adm_add")
async def cb_adm_add(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    user_id = callback.from_user.id
    if not db_manager.is_postbot_owner(bot_db_id, user_id):
        return
        
    lang = db_manager.get_user_lang(user_id)
    await state.set_state(PostbotStates.add_admin_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data="pb_manage_admins", style="danger")
    
    await callback.message.edit_text(t('enter_admin_id', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.add_admin_id)
async def process_add_admin_id(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = get_bot_db_id(bot.id)
    if not bot_db_id:
        return
        
    user_id = message.from_user.id
    if not db_manager.is_postbot_owner(bot_db_id, user_id):
        return
        
    lang = db_manager.get_user_lang(user_id)
    text = message.text.strip() if message.text else ""
    if not text.isdigit():
        await message.answer("❌ Invalid ID format. Please send a numeric Telegram User ID.")
        return
        
    target_id = int(text)
    
    # Verify target has started chat with this bot
    status_msg = await message.answer(t('testing_connection', lang))
    try:
        # Get admin's details dynamically from Telegram
        try:
            target_chat = await bot.get_chat(target_id)
            admin_username = target_chat.username or target_chat.first_name or f"User_{target_id}"
        except Exception as chat_err:
            logger.warning(f"Could not get chat for admin {target_id}: {chat_err}")
            admin_username = f"User_{target_id}"

        await bot.send_message(
            chat_id=target_id,
            text=f"🟢 <b>PostBot Link</b>\n\nYou have been successfully added as an admin of @{bot.username}."
        )
        db_manager.add_postbot_admin(bot_db_id, target_id, admin_username, 'admin')
        await status_msg.delete()
        await message.answer(t('admin_added', lang), reply_markup=get_start_keyboard(bot_db_id, user_id, lang))
        await state.clear()
    except Exception as e:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('btn_cancel', lang), callback_data="pb_manage_admins", style="danger")
        await status_msg.edit_text(f"❌ Failed to send message to user: {e}\n\nMake sure the user has started a chat with this bot.", reply_markup=builder.as_markup())

# ================= CHAT INFORMATION COMMAND =================

@postbot_router.message(Command("chat"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
@postbot_router.channel_post(Command("chat"))
async def cmd_chat_info(message: Message):
    chat = message.chat
    username_str = f"@{chat.username}" if chat.username else "None"
    
    info_text = (
        f"ℹ️ <b>Chat / Group Information:</b>\n\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"📝 <b>Title:</b> {chat.title or 'Channel/Group'}\n"
        f"🏷️ <b>Username:</b> {username_str}\n"
        f"👤 <b>Type:</b> {chat.type}"
    )
    await message.reply(info_text)

# ================= PASSCODE LINKING (CHANNELS/GROUPS) =================

@postbot_router.message(F.chat.type != ChatType.PRIVATE)
async def handle_group_passcode(message: Message, bot: Bot):
    bot_db_id = get_bot_db_id(bot.id)
    if not bot_db_id:
        return
        
    text = message.text or message.caption
    if not text:
        return
        
    # Check if text is passcode for a PostGroup of this bot
    group_row = db_manager.get_post_group_by_passcode_for_bot(text, bot_db_id)
    if group_row:
        # Link this chat
        group_id = group_row[0]
        success = db_manager.add_chat(message.chat.id, group_id, message.chat.title, message.chat.username)
        if success:
            try:
                await message.delete()
            except Exception:
                pass
            # If promo is enabled, configure reactions for this newly linked chat
            promo_settings = db_manager.get_post_group_promo_settings(group_id)
            if promo_settings and promo_settings[0] == 1:
                try:
                    await set_group_reactions(bot, message.chat.id)
                except Exception as e:
                    logger.error(f"Failed to enable reactions for newly linked chat {message.chat.id}: {e}")
            res = await message.answer("✅ Channel/Group successfully linked to the PostGroup!")
            import asyncio
            await asyncio.sleep(5)
            try:
                await res.delete()
            except Exception:
                pass

# ================= POSTBOT SETTINGS SECTION =================

@postbot_router.callback_query(F.data == "pb_settings_menu")
async def cb_settings_menu(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    groups = db_manager.get_post_groups(bot_db_id)
    group_lines = []
    for g in groups:
        g_name = g[2]
        g_active = g[7] if len(g) > 7 else 1
        status_text = t('status_enabled', lang) if g_active else t('status_disabled', lang)
        group_lines.append(f"• <b>{g_name}</b>: {status_text}")
        
    group_list_str = "\n".join(group_lines) if group_lines else "• " + t('pg_no_groups', lang)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_stop_all_groups', lang), callback_data="pb_stop_all_groups", style="danger")
    builder.button(text=t('btn_start_all_groups', lang), callback_data="pb_start_all_groups", style="success")
    builder.button(text=t('btn_back', lang), callback_data="pb_main_menu", style="primary")
    builder.adjust(1)
    
    text = t('settings_menu_title', lang, group_list=group_list_str)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data == "pb_stop_all_groups")
async def cb_stop_all_groups(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    db_manager.deactivate_all_post_groups(bot_db_id)
    lang = db_manager.get_user_lang(callback.from_user.id)
    await callback.answer(t('all_groups_stopped', lang), show_alert=True)
    await cb_settings_menu(callback, bot)

@postbot_router.callback_query(F.data == "pb_start_all_groups")
async def cb_start_all_groups(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    db_manager.activate_all_post_groups(bot_db_id)
    lang = db_manager.get_user_lang(callback.from_user.id)
    await callback.answer(t('all_groups_started', lang), show_alert=True)
    await cb_settings_menu(callback, bot)

# ================= ATTENTION GRABBER (PROMO) SETTINGS =================

from aiogram.methods.base import TelegramMethod
from aiogram.types import ReactionType
from typing import List, Union

class SetChatAvailableReactions(TelegramMethod[bool]):
    __returning__ = bool
    __api_method__ = 'setChatAvailableReactions'
    
    chat_id: Union[int, str]
    available_reactions: List[ReactionType]

async def set_group_reactions(bot: Bot, chat_id: int):
    allowed = [
        ReactionTypeEmoji(emoji="🔥"),
        ReactionTypeEmoji(emoji="🎉"),
        ReactionTypeEmoji(emoji="🤩"),
        ReactionTypeEmoji(emoji="❤️")
    ]
    method = SetChatAvailableReactions(chat_id=chat_id, available_reactions=allowed)
    await bot(method)

async def enable_promo_reactions_for_group(bot: Bot, group_id: int):
    chats = db_manager.get_chats(group_id)
    for chat in chats:
        chat_id = chat[0]
        try:
            await set_group_reactions(bot, chat_id)
        except Exception as e:
            logger.error(f"Failed to set reactions for chat {chat_id}: {e}")

@postbot_router.callback_query(F.data.startswith("pb_promo_menu_"))
async def cb_promo_menu(callback: CallbackQuery, bot: Bot, state: FSMContext = None):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    if state:
        await state.clear()
        
    group_id = int(callback.data.split("_")[3])
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    row = db_manager.get_post_group_promo_settings(group_id)
    if not row:
        await callback.answer("Error: PostGroup settings not found.")
        return
        
    promo_enabled, min_d, max_d, trigger, text_inst, text_succ, dur, text_dur, post_dur_hours, post_frequency, post_counter = row
    
    is_configured = (text_inst is not None and text_succ is not None and text_dur is not None)
    
    status_str = t('status_enabled', lang) if promo_enabled else t('status_disabled', lang)
    discount_range = f"{min_d}-{max_d}" if min_d is not None and max_d is not None else "5-10"
    
    text = t(
        'promo_settings_title', lang,
        status=status_str,
        trigger_emoji=trigger or "❤️",
        discount_range=discount_range,
        duration_hours=dur if dur is not None else 3,
        text_instruction=text_inst or "Not Configured",
        text_success=text_succ or "Not Configured",
        text_duration=text_dur or "Not Configured",
        post_duration_hours=post_dur_hours if post_dur_hours is not None else 12,
        post_frequency=post_frequency if post_frequency is not None else 10
    )
    
    builder = InlineKeyboardBuilder()
    
    if is_configured:
        toggle_text = t('btn_promo_disable', lang) if promo_enabled else t('btn_promo_enable', lang)
        toggle_style = "danger" if promo_enabled else "success"
        builder.button(text=toggle_text, callback_data=f"pb_promo_toggle_{group_id}", style=toggle_style)
        
    builder.button(text=t('btn_setup_promo', lang), callback_data=f"pb_promo_setup_{group_id}", style="primary")
    builder.button(text=t('btn_back', lang), callback_data=f"pb_group_edit_{group_id}", style="danger")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.callback_query(F.data.startswith("pb_promo_toggle_"))
async def cb_promo_toggle(callback: CallbackQuery, bot: Bot):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    row = db_manager.get_post_group_promo_settings(group_id)
    if not row:
        await callback.answer("Error: PostGroup settings not found.")
        return
        
    promo_enabled, min_d, max_d, trigger, text_inst, text_succ, dur, text_dur, *rest = row
    is_configured = (text_inst is not None and text_succ is not None and text_dur is not None)
    
    if not is_configured:
        await callback.answer(t('setup_promo_first_alert', lang), show_alert=True)
        return
        
    new_status = 0 if promo_enabled else 1
    db_manager.update_post_group_promo_enabled(group_id, new_status)
    
    if new_status == 1:
        await enable_promo_reactions_for_group(bot, group_id)
        
    await callback.answer(t('status_enabled', lang) if new_status else t('status_disabled', lang))
    await cb_promo_menu(callback, bot)

@postbot_router.callback_query(F.data.startswith("pb_promo_setup_"))
async def cb_promo_setup(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
        
    group_id = int(callback.data.split("_")[3])
    lang = db_manager.get_user_lang(callback.from_user.id)
    
    await state.update_data(promo_group_id=group_id)
    await state.set_state(PostbotStates.promo_discount_range)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    await callback.message.edit_text(t('promo_discount_range_prompt', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.promo_discount_range)
async def process_promo_discount_range(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    
    match = re.match(r"^(\d+)-(\d+)$", text)
    if not match:
        await message.answer(t('invalid_discount_range', lang))
        return
    min_d, max_d = int(match.group(1)), int(match.group(2))
    if min_d < 0 or max_d < 0 or min_d > max_d:
        await message.answer(t('invalid_discount_range', lang))
        return
        
    await state.update_data(promo_discount_min=min_d, promo_discount_max=max_d)
    await state.set_state(PostbotStates.promo_trigger_emoji)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥", callback_data="pb_promo_emoji_🔥")
    builder.button(text="🎉", callback_data="pb_promo_emoji_🎉")
    builder.button(text="🤩", callback_data="pb_promo_emoji_🤩")
    builder.button(text="❤️", callback_data="pb_promo_emoji_❤️")
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    builder.adjust(4, 1)
    
    await message.answer(t('promo_trigger_emoji_prompt', lang), reply_markup=builder.as_markup())

@postbot_router.callback_query(PostbotStates.promo_trigger_emoji, F.data.startswith("pb_promo_emoji_"))
async def process_promo_emoji(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(callback, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(callback.from_user.id)
    emoji = callback.data.split("_")[3]
    
    await state.update_data(promo_trigger_emoji=emoji)
    await state.set_state(PostbotStates.promo_post_duration_hours)
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    await callback.message.edit_text(t('promo_post_duration_hours_prompt', lang), reply_markup=builder.as_markup())
    await callback.answer()

@postbot_router.message(PostbotStates.promo_post_duration_hours)
async def process_promo_post_duration(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    
    if not text.isdigit() or int(text) <= 0:
        await message.answer(t('invalid_duration_hours', lang))
        return
        
    await state.update_data(promo_post_duration_hours=int(text))
    await state.set_state(PostbotStates.promo_post_frequency)
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    await message.answer(t('promo_post_frequency_prompt', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.promo_post_frequency)
async def process_promo_post_frequency(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    
    if not text.isdigit() or int(text) <= 0:
        await message.answer(t('invalid_duration_hours', lang))
        return
        
    await state.update_data(promo_post_frequency=int(text))
    await state.set_state(PostbotStates.promo_text_instruction)
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    min_d = data.get('promo_discount_min', 5)
    max_d = data.get('promo_discount_max', 10)
    emoji = data.get('promo_trigger_emoji', "❤️")
    post_dur = data.get('promo_post_duration_hours', 12)
    discount_range = f"{min_d}-{max_d}"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    prompt_text = t('promo_text_instruction_prompt', lang, emoji=emoji, discount_range=discount_range, post_duration=post_dur)
    await message.answer(prompt_text, reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.promo_text_instruction)
async def process_promo_instruction(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    if not text:
        await message.answer("❌ Instruction text cannot be empty. Please send it again.")
        return
        
    await state.update_data(promo_text_instruction=text)
    await state.set_state(PostbotStates.promo_text_success)
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    await message.answer(t('promo_text_success_prompt', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.promo_text_success)
async def process_promo_success(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    if not text:
        await message.answer("❌ Success text cannot be empty. Please send it again.")
        return
        
    await state.update_data(promo_text_success=text)
    await state.set_state(PostbotStates.promo_duration_hours)
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    await message.answer(t('promo_duration_hours_prompt', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.promo_duration_hours)
async def process_promo_duration(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    
    if not text.isdigit() or int(text) <= 0:
        await message.answer(t('invalid_duration_hours', lang))
        return
        
    await state.update_data(promo_duration_hours=int(text))
    await state.set_state(PostbotStates.promo_text_duration)
    
    data = await state.get_data()
    group_id = data['promo_group_id']
    
    builder = InlineKeyboardBuilder()
    builder.button(text=t('btn_cancel', lang), callback_data=f"pb_promo_menu_{group_id}", style="danger")
    
    await message.answer(t('promo_text_duration_prompt', lang), reply_markup=builder.as_markup())

@postbot_router.message(PostbotStates.promo_text_duration)
async def process_promo_text_duration(message: Message, bot: Bot, state: FSMContext):
    bot_db_id = await get_authorized_bot_id(message, bot)
    if not bot_db_id:
        return
    lang = db_manager.get_user_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""
    if not text:
        await message.answer("❌ Alert text cannot be empty. Please send it again.")
        return
        
    data = await state.get_data()
    group_id = data['promo_group_id']
    
    db_manager.update_post_group_promo_settings(
        group_id=group_id,
        min_discount=data['promo_discount_min'],
        max_discount=data['promo_discount_max'],
        trigger_emoji=data['promo_trigger_emoji'],
        instruction_text=data['promo_text_instruction'],
        success_text=data['promo_text_success'],
        duration_hours=data['promo_duration_hours'],
        duration_text=text,
        post_duration_hours=data['promo_post_duration_hours'],
        post_frequency=data['promo_post_frequency']
    )
    
    await state.clear()
    
    row = db_manager.get_post_group_promo_settings(group_id)
    promo_enabled, min_d, max_d, trigger, text_inst, text_succ, dur, text_dur, post_dur_hours, post_frequency, post_counter = row
    
    status_str = t('status_enabled', lang) if promo_enabled else t('status_disabled', lang)
    discount_range = f"{min_d}-{max_d}"
    
    text_display = t(
        'promo_settings_title', lang,
        status=status_str,
        trigger_emoji=trigger or "❤️",
        discount_range=discount_range,
        duration_hours=dur,
        text_instruction=text_inst,
        text_success=text_succ,
        text_duration=text_dur,
        post_duration_hours=post_dur_hours,
        post_frequency=post_frequency
    )
    
    builder = InlineKeyboardBuilder()
    toggle_text = t('btn_promo_disable', lang) if promo_enabled else t('btn_promo_enable', lang)
    toggle_style = "danger" if promo_enabled else "success"
    builder.button(text=toggle_text, callback_data=f"pb_promo_toggle_{group_id}", style=toggle_style)
    builder.button(text=t('btn_setup_promo', lang), callback_data=f"pb_promo_setup_{group_id}", style="primary")
    builder.button(text=t('btn_back', lang), callback_data=f"pb_group_edit_{group_id}", style="danger")
    builder.adjust(1)
    
    await message.answer(text_display, reply_markup=builder.as_markup())

# ================= REACTION HANDLING =================

def generate_promo_code() -> str:
    import string
    chars = string.ascii_letters + string.digits
    random_str = "".join(random.choices(chars, k=17))
    return f"tg-{random_str}"

@postbot_router.message_reaction()
async def on_message_reaction(update: MessageReactionUpdated, bot: Bot):
    logger.info(f"on_message_reaction triggered! Chat ID: {update.chat.id}, User: {update.user}")
    user = update.user
    if not user:
        logger.info("on_message_reaction: update.user is None, ignoring anonymous or channel reaction")
        return
        
    chat_id = update.chat.id
    active_promo = db_manager.get_active_promo_post(chat_id, update.message_id)
    if not active_promo:
        logger.info(f"on_message_reaction: message {update.message_id} in chat {chat_id} is not an active promo post (or has expired), ignoring reaction")
        return
        
    group_id = active_promo[0]
    original_text = None
    original_kb = None
    post_type = None
    if len(active_promo) >= 5:
        original_text = active_promo[2]
        original_kb = active_promo[3]
        post_type = active_promo[4]

    promo_settings = db_manager.get_post_group_promo_settings(group_id)
    if not promo_settings:
        logger.info(f"on_message_reaction: no promo settings for group {group_id}")
        return
        
    promo_enabled, min_d, max_d, trigger_emoji, text_inst, text_succ, dur_hours, text_dur, *rest = promo_settings
    logger.info(f"on_message_reaction: promo_enabled={promo_enabled}, trigger_emoji={trigger_emoji}")
    if not promo_enabled:
        logger.info("on_message_reaction: promo is disabled for this group")
        return
        
    def norm_emoji(e: str) -> str:
        return e.replace("\ufe0f", "").replace("\ufe0e", "") if e else ""

    old_emojis = {norm_emoji(r.emoji) for r in update.old_reaction if isinstance(r, ReactionTypeEmoji)}
    new_emojis = {norm_emoji(r.emoji) for r in update.new_reaction if isinstance(r, ReactionTypeEmoji)}
    logger.info(f"on_message_reaction: normalized old={old_emojis}, new={new_emojis}")
    
    norm_trigger = norm_emoji(trigger_emoji or "❤️")
    logger.info(f"on_message_reaction: normalized trigger_emoji={norm_trigger}")
    
    if norm_trigger in new_emojis and norm_trigger not in old_emojis:
        logger.info("on_message_reaction: trigger emoji detected!")
        # Check if user already has an active promo code for this group
        existing = db_manager.get_active_user_promo(group_id, user.id)
        if existing:
            logger.info(f"on_message_reaction: user {user.id} already has an active promo code {existing}")
            return
            
        # Delete promo post immediately so that no other user (or repeated reaction) can claim a promo code from it
        db_manager.delete_promo_post(chat_id, update.message_id)
            
        # Generate code
        while True:
            code = generate_promo_code()
            if not db_manager.get_promo_code(code):
                break
                
        import time
        now = int(time.time())
        expires_at = now + int(dur_hours * 3600)
        discount = random.randint(min_d, max_d)
        
        db_manager.add_promo_code(
            code=code,
            group_id=group_id,
            user_id=user.id,
            discount_amount=discount,
            created_at=now,
            expires_at=expires_at,
            user_name=user.full_name,
            user_username=user.username
        )
        
        text_succ = text_succ or ""
        text_dur = text_dur or ""
        mention = user.mention_html(user.full_name or f"User_{user.id}")
        response_text = (
            f"{mention}\n\n"
            f"{text_succ}\n"
            f"💰 <b>-{discount}%</b>\n"
            f"🔑 <code>{code}</code>\n\n"
            f"{text_dur}"
        )
        
        import asyncio
        if original_text is not None:
            # We edit the reacted message instead of sending a new one
            async def edit_and_restore(c_id: int, m_id: int, p_text: str, o_text: str, o_kb: str, p_type: str):
                try:
                    if p_type == "text" or not p_type:
                        await bot.edit_message_text(
                            chat_id=c_id,
                            message_id=m_id,
                            text=p_text,
                            parse_mode="HTML",
                            reply_markup=json_to_markup(o_kb)
                        )
                    else:
                        await bot.edit_message_caption(
                            chat_id=c_id,
                            message_id=m_id,
                            caption=p_text,
                            parse_mode="HTML",
                            reply_markup=json_to_markup(o_kb)
                        )
                    
                    await asyncio.sleep(180)
                    
                    if p_type == "text" or not p_type:
                        await bot.edit_message_text(
                            chat_id=c_id,
                            message_id=m_id,
                            text=o_text,
                            parse_mode="HTML",
                            reply_markup=json_to_markup(o_kb)
                        )
                    else:
                        await bot.edit_message_caption(
                            chat_id=c_id,
                            message_id=m_id,
                            caption=o_text,
                            parse_mode="HTML",
                            reply_markup=json_to_markup(o_kb)
                        )
                except asyncio.CancelledError:
                    logger.info(f"Promo edit task for message {m_id} in chat {c_id} cancelled.")
                    raise
                except Exception as restore_err:
                    logger.error(f"Error in edit_and_restore for message {m_id} in chat {c_id}: {restore_err}")
                finally:
                    key_item = (c_id, m_id)
                    if active_promo_edits.get(key_item) == asyncio.current_task():
                        active_promo_edits.pop(key_item, None)

            # Cancel existing task if any
            key = (chat_id, update.message_id)
            if key in active_promo_edits:
                active_promo_edits[key].cancel()
                logger.info(f"Cancelled previous edit_and_restore task for chat {chat_id}, message {update.message_id}")
            
            task = asyncio.create_task(
                edit_and_restore(
                    c_id=chat_id,
                    m_id=update.message_id,
                    p_text=response_text,
                    o_text=original_text,
                    o_kb=original_kb,
                    p_type=post_type
                )
            )
            active_promo_edits[key] = task
        else:
            # Fallback to old behavior (sending a new message and pinning it, then deleting)
            try:
                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=response_text,
                    reply_to_message_id=update.message_id,
                    parse_mode="HTML"
                )
                try:
                    await bot.pin_chat_message(chat_id=chat_id, message_id=sent_msg.message_id)
                except Exception as pin_err:
                    logger.error(f"Failed to pin promo message in chat {chat_id}: {pin_err}")
                    
                async def delete_after_delay(c_id: int, m_id: int):
                    await asyncio.sleep(180)
                    try:
                        await bot.delete_message(chat_id=c_id, message_id=m_id)
                    except Exception as del_err:
                        logger.debug(f"Could not delete promo message {m_id}: {del_err}")
                
                asyncio.create_task(delete_after_delay(chat_id, sent_msg.message_id))
            except Exception as e:
                logger.error(f"Failed to send promo reply (fallback): {e}")
