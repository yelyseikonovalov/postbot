import asyncio
import logging
import time
import zoneinfo
from datetime import datetime, time as datetime_time
from aiogram import Bot

import db_manager
from locales import t
from postbot_handlers import json_to_markup

logger = logging.getLogger(__name__)

def is_time_in_range(time_range_str: str) -> bool:
    try:
        normalized = "".join(time_range_str.split())
        start_str, end_str = normalized.split("-")
        sh, sm = map(int, start_str.split(":"))
        if end_str == "24:00":
            eh, em = 23, 59
        else:
            eh, em = map(int, end_str.split(":"))
            
        start = datetime_time(sh, sm)
        end = datetime_time(eh, em)
    except Exception as e:
        logger.debug(f"Failed to parse time range '{time_range_str}': {e}. Defaulting to True.")
        return True
        
    tz = zoneinfo.ZoneInfo("Asia/Jerusalem")
    now_dt = datetime.now(tz)
    now_time = now_dt.time()
    
    if start <= end:
        return start <= now_time <= end
    else:  # Crosses midnight
        return now_time >= start or now_time <= end

class PostScheduler:
    def __init__(self, bot_manager):
        self.bot_manager = bot_manager
        self.last_post_times = {}  # group_id -> float
        self.is_running = False
        self._task = None
        self.last_cleanup_time = 0
        self.last_promo_cleanup_time = 0

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Background posting scheduler started.")

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Background posting scheduler stopped.")

    async def _loop(self):
        await asyncio.sleep(5)  # Wait for startup
        while self.is_running:
            try:
                # Fetch all postbots to ensure they are active
                bots = db_manager.get_all_postbots()
                current_time = time.time()
                
                # 30-minute cleanup routine for blocked / lost chats
                if current_time - self.last_cleanup_time >= 1800:
                    self.last_cleanup_time = current_time
                    try:
                        await self._cleanup_inactive_chats(bots)
                    except Exception as cleanup_err:
                        logger.error(f"Error during inactive chats cleanup: {cleanup_err}")
                        
                # 5-minute cleanup routine for expired promo posts in the database
                if current_time - self.last_promo_cleanup_time >= 300:
                    self.last_promo_cleanup_time = current_time
                    try:
                        db_manager.delete_expired_promo_posts()
                    except Exception as promo_cleanup_err:
                        logger.error(f"Error during expired promo posts cleanup: {promo_cleanup_err}")
                
                for bot_row in bots:
                    # bot_row: bot_id, token, username, proxy, is_active
                    bot_id, token, username, proxy, is_active = bot_row
                    
                    if not is_active:
                        continue
                        
                    bot_instance = self.bot_manager.running_bots.get(bot_id)
                    if not bot_instance:
                        continue
                        
                    # Fetch postgroups for this bot
                    groups = db_manager.get_post_groups(bot_id)
                    for group_row in groups:
                        # group_row: group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active
                        group_id, _, name, passcode, _, interval, time_range, group_active = group_row
                        
                        if not group_active:
                            continue
                            
                        # Timezone range filter check
                        if not is_time_in_range(time_range):
                            continue
                            
                        # Interval check
                        last_time = self.last_post_times.get(group_id, 0)
                        if current_time - last_time >= interval:
                            try:
                                await self._post_next(group_id, bot_instance)
                            except Exception as post_err:
                                logger.error(f"Error executing post for group {group_id} ({name}): {post_err}")
                                from aiogram.exceptions import TelegramUnauthorizedError
                                is_unauthorized = False
                                if isinstance(post_err, TelegramUnauthorizedError) or "unauthorized" in str(post_err).lower() or "token" in str(post_err).lower():
                                    is_unauthorized = True
                                if is_unauthorized:
                                    logger.warning(f"Deactivating bot ID {bot_id} in scheduler due to error: {post_err}")
                                    db_manager.update_postbot_active_status(bot_id, 0)
                                    await self.bot_manager.stop_bot(bot_id)
                                    await self.bot_manager.notify_bot_disabled(bot_id, str(post_err))
                            self.last_post_times[group_id] = current_time
                            
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                
            await asyncio.sleep(5)  # check every 5 seconds

    async def _post_next(self, group_id, bot: Bot):
        posts = db_manager.get_posts(group_id)
        if not posts:
            return
            
        chats = db_manager.get_chats(group_id)
        if not chats:
            return
            
        for chat in chats:
            # chat: chat_id, group_id, title, username, last_posted_index
            chat_id, _, title, username, last_idx = chat
            
            next_idx = (last_idx + 1) % len(posts)
            post = posts[next_idx]
            _, _, type_, file_id, text_msg, kb_json = post
            
            promo_settings = db_manager.get_post_group_promo_settings(group_id)
            final_text = text_msg or ""
            attach_promo = False
            
            if promo_settings and promo_settings[0] == 1:
                sent_count = db_manager.get_chat_sent_posts_count(chat_id, group_id)
                post_freq = promo_settings[9] or 10
                if (sent_count + 1) % post_freq == 0:
                    attach_promo = True
                    promo_inst = promo_settings[4]
                    if promo_inst:
                        if final_text:
                            final_text += f"\n\n<b>{promo_inst}</b>"
                        else:
                            final_text = f"<b>{promo_inst}</b>"
            
            # Use group's default keyboard if the post does not have a custom keyboard
            actual_kb = kb_json
            if not actual_kb or actual_kb == "[]":
                group_row = db_manager.get_post_group(group_id)
                if group_row and group_row[4]:
                    actual_kb = group_row[4]
            
            kb_markup = json_to_markup(actual_kb)
            
            sent_msg = None
            try:
                if type_ == "photo":
                    sent_msg = await bot.send_photo(chat_id=chat_id, photo=file_id, caption=final_text, reply_markup=kb_markup)
                elif type_ == "video":
                    sent_msg = await bot.send_video(chat_id=chat_id, video=file_id, caption=final_text, reply_markup=kb_markup)
                elif type_ == "animation":
                    sent_msg = await bot.send_animation(chat_id=chat_id, animation=file_id, caption=final_text, reply_markup=kb_markup)
                elif type_ == "document":
                    sent_msg = await bot.send_document(chat_id=chat_id, document=file_id, caption=final_text, reply_markup=kb_markup)
                else:  # text
                    sent_msg = await bot.send_message(chat_id=chat_id, text=final_text, reply_markup=kb_markup)
                    
                # Update last posted index & increment sent count
                db_manager.update_chat_last_index(chat_id, group_id, next_idx)
                db_manager.increment_chat_post_counter(chat_id, group_id)
                
                # If promo was attached and message sent successfully, register in promo_posts
                if attach_promo and sent_msg:
                    post_dur = promo_settings[8] or 12
                    expires_at = int(time.time()) + int(post_dur * 3600)
                    db_manager.add_promo_post(
                        chat_id=chat_id,
                        message_id=sent_msg.message_id,
                        group_id=group_id,
                        expires_at=expires_at,
                        original_text=text_msg or "",
                        original_kb=actual_kb,
                        post_type=type_
                    )
                    logger.info(f"Registered promo post in chat {chat_id}, message {sent_msg.message_id}, expires in {post_dur} hours")
                
                # Pin message
                if sent_msg:
                    try:
                        await bot.pin_chat_message(chat_id=chat_id, message_id=sent_msg.message_id)
                    except Exception as pin_err:
                        logger.debug(f"Could not pin message in chat {chat_id}: {pin_err}")
                        
            except Exception as send_err:
                logger.error(f"Failed to post to chat {chat_id} in group {group_id}: {send_err}")
                err_str = str(send_err).lower()
                if any(term in err_str for term in ["chat not found", "forbidden", "kicked", "chat was deactivated", "not member of chat"]):
                    logger.warning(f"Immediately removing chat {chat_id} from group {group_id} due to send failure: {send_err}")
                    db_manager.delete_chat(chat_id, group_id)
                    try:
                        group_row = db_manager.get_post_group(group_id)
                        if group_row:
                            bot_id, name = group_row[1], group_row[2]
                            await self._notify_chat_removed(bot, bot_id, chat_id, title, name)
                    except Exception as notify_err:
                        logger.error(f"Failed to trigger immediate notify on post failure: {notify_err}")
                    
            # 2-second flood protection delay between different chats
            await asyncio.sleep(2.0)

    async def _notify_chat_removed(self, bot_instance: Bot, bot_id: int, chat_id: int, title: str, group_name: str):
        try:
            admins = db_manager.get_postbot_admins(bot_id)
            owner_id = None
            for adm in admins:
                if adm[2] == "owner":
                    owner_id = adm[0]
                    break
            if owner_id:
                owner_lang = db_manager.get_user_lang(owner_id)
                alert_text = t(
                    'chat_removed_alert', owner_lang,
                    title=title,
                    chat_id=chat_id,
                    group_name=group_name
                )
                await bot_instance.send_message(owner_id, alert_text)
        except Exception as notify_err:
            logger.error(f"Failed to notify bot owner for chat {chat_id} removal: {notify_err}")

    async def _cleanup_inactive_chats(self, bots):
        logger.info("Starting 30-minute status check of connected groups and channels...")
        for bot_row in bots:
            bot_id, token, username, proxy, is_active = bot_row
            if not is_active:
                continue
                
            bot_instance = self.bot_manager.running_bots.get(bot_id)
            if not bot_instance:
                continue
                
            groups = db_manager.get_post_groups(bot_id)
            for group_row in groups:
                # group_row: group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active
                group_id, _, name, passcode, _, _, _, _ = group_row
                chats = db_manager.get_chats(group_id)
                for chat in chats:
                    chat_id, _, title, _, _ = chat
                    try:
                        # Check access status
                        await bot_instance.get_chat(chat_id)
                    except Exception as e:
                        err_str = str(e).lower()
                        if any(term in err_str for term in ["chat not found", "forbidden", "kicked", "chat was deactivated", "not member of chat"]):
                            logger.info(f"Cleanup: Removing access-lost chat {chat_id} ('{title}') from group {group_id}")
                            db_manager.delete_chat(chat_id, group_id)
                            await self._notify_chat_removed(bot_instance, bot_id, chat_id, title, name)
