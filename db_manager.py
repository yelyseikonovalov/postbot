import sqlite3
import json
import os
import logging

DB_PATH = os.getenv("DATABASE_PATH", "db.db")
logger = logging.getLogger(__name__)

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Schema Migration: post_groups (remove global passcode UNIQUE, add UNIQUE(bot_id, passcode))
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='post_groups'")
        row = cursor.fetchone()
        if row and "passcode TEXT UNIQUE" in row[0]:
            logger.info("Migrating post_groups schema to remove global passcode UNIQUE constraint...")
            cursor.execute("ALTER TABLE post_groups RENAME TO post_groups_old")
            
            # Create new table
            cursor.execute("""
                CREATE TABLE post_groups (
                    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id INTEGER,
                    name TEXT,
                    passcode TEXT,
                    default_kb TEXT,
                    interval INTEGER DEFAULT 900,
                    time_range TEXT DEFAULT '00:00-24:00',
                    is_active INTEGER DEFAULT 1,
                    promo_enabled INTEGER DEFAULT 0,
                    promo_discount_min INTEGER DEFAULT 5,
                    promo_discount_max INTEGER DEFAULT 10,
                    promo_trigger_emoji TEXT DEFAULT '❤️',
                    promo_text_instruction TEXT,
                    promo_text_success TEXT,
                    promo_duration_hours INTEGER DEFAULT 3,
                    promo_text_duration TEXT,
                    promo_post_duration_hours INTEGER DEFAULT 12,
                    promo_post_frequency INTEGER DEFAULT 10,
                    promo_post_counter INTEGER DEFAULT 0,
                    UNIQUE(bot_id, passcode),
                    FOREIGN KEY (bot_id) REFERENCES postbots (bot_id) ON DELETE CASCADE
                )
            """)
            
            # Copy data dynamically
            cursor.execute("PRAGMA table_info(post_groups_old)")
            old_cols = [col[1] for col in cursor.fetchall()]
            common_cols = [c for c in old_cols if c in [
                'group_id', 'bot_id', 'name', 'passcode', 'default_kb', 'interval', 'time_range', 'is_active',
                'promo_enabled', 'promo_discount_min', 'promo_discount_max', 'promo_trigger_emoji',
                'promo_text_instruction', 'promo_text_success', 'promo_duration_hours', 'promo_text_duration',
                'promo_post_duration_hours', 'promo_post_frequency', 'promo_post_counter'
            ]]
            cols_str = ", ".join(common_cols)
            cursor.execute(f"INSERT INTO post_groups ({cols_str}) SELECT {cols_str} FROM post_groups_old")
            cursor.execute("DROP TABLE post_groups_old")
            conn.commit()
            logger.info("post_groups schema migration completed successfully.")
    except Exception as e:
        logger.error(f"Migration error for post_groups table: {e}")

    # Schema Migration: chats (composite PRIMARY KEY (chat_id, group_id))
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='chats'")
        row = cursor.fetchone()
        if row and "chat_id INTEGER PRIMARY KEY" in row[0]:
            logger.info("Migrating chats schema to support composite PRIMARY KEY (chat_id, group_id)...")
            cursor.execute("ALTER TABLE chats RENAME TO chats_old")
            
            # Create new table
            cursor.execute("""
                CREATE TABLE chats (
                    chat_id INTEGER,
                    group_id INTEGER,
                    title TEXT,
                    username TEXT,
                    last_posted_index INTEGER DEFAULT -1,
                    sent_posts_count INTEGER DEFAULT 0,
                    PRIMARY KEY (chat_id, group_id),
                    FOREIGN KEY (group_id) REFERENCES post_groups (group_id) ON DELETE CASCADE
                )
            """)
            
            # Copy data dynamically
            cursor.execute("PRAGMA table_info(chats_old)")
            old_cols = [col[1] for col in cursor.fetchall()]
            common_cols = [c for c in old_cols if c in [
                'chat_id', 'group_id', 'title', 'username', 'last_posted_index', 'sent_posts_count'
            ]]
            cols_str = ", ".join(common_cols)
            cursor.execute(f"INSERT INTO chats ({cols_str}) SELECT {cols_str} FROM chats_old")
            cursor.execute("DROP TABLE chats_old")
            conn.commit()
            logger.info("chats schema migration completed successfully.")
    except Exception as e:
        logger.error(f"Migration error for chats table: {e}")

    # Migration check: drop old tables if they refer to bot_id instead of group_id
    try:
        cursor.execute("PRAGMA table_info(posts)")
        columns = [col[1] for col in cursor.fetchall()]
        if columns and "bot_id" in columns and "group_id" not in columns:
            logger.info("Dropping old posts and chats tables to migrate schemas...")
            cursor.execute("DROP TABLE IF EXISTS posts")
            cursor.execute("DROP TABLE IF EXISTS chats")
            cursor.execute("DROP TABLE IF EXISTS postbots")
            cursor.execute("DROP TABLE IF EXISTS control_admins")
    except Exception as e:
        logger.error(f"Migration check error: {e}")
        
    # 1. users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT DEFAULT 'en'
        )
    """)
    
    # 2. control_admins
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT
        )
    """)
    
    # 3. postbots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postbots (
            bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            username TEXT,
            proxy TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # 4. postbot_admins [NEW]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postbot_admins (
            bot_id INTEGER,
            user_id INTEGER,
            username TEXT,
            role TEXT,
            PRIMARY KEY (bot_id, user_id),
            FOREIGN KEY (bot_id) REFERENCES postbots (bot_id) ON DELETE CASCADE
        )
    """)
    
    # 5. post_groups [UPDATED]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER,
            name TEXT,
            passcode TEXT,
            default_kb TEXT,
            interval INTEGER DEFAULT 900,
            time_range TEXT DEFAULT '00:00-24:00',
            is_active INTEGER DEFAULT 1,
            UNIQUE(bot_id, passcode),
            FOREIGN KEY (bot_id) REFERENCES postbots (bot_id) ON DELETE CASCADE
        )
    """)
    
    # 6. posts [UPDATED]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            type TEXT,
            file_id TEXT,
            text_msg TEXT,
            kb TEXT,
            FOREIGN KEY (group_id) REFERENCES post_groups (group_id) ON DELETE CASCADE
        )
    """)
    
    # 7. chats [UPDATED]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER,
            group_id INTEGER,
            title TEXT,
            username TEXT,
            last_posted_index INTEGER DEFAULT -1,
            PRIMARY KEY (chat_id, group_id),
            FOREIGN KEY (group_id) REFERENCES post_groups (group_id) ON DELETE CASCADE
        )
    """)
    
    # Migration checks
    try:
        cursor.execute("PRAGMA table_info(post_groups)")
        cols = [col[1] for col in cursor.fetchall()]
        if "is_active" not in cols:
            logger.info("Adding is_active column to post_groups table...")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN is_active INTEGER DEFAULT 1")
        if "promo_enabled" not in cols:
            logger.info("Adding promo columns to post_groups table...")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_enabled INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_discount_min INTEGER DEFAULT 5")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_discount_max INTEGER DEFAULT 10")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_trigger_emoji TEXT DEFAULT '❤️'")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_text_instruction TEXT")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_text_success TEXT")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_duration_hours INTEGER DEFAULT 3")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_text_duration TEXT")
        
        # New promo post settings migration checks
        if "promo_post_duration_hours" not in cols:
            logger.info("Adding promo_post columns to post_groups table...")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_post_duration_hours INTEGER DEFAULT 12")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_post_frequency INTEGER DEFAULT 10")
            cursor.execute("ALTER TABLE post_groups ADD COLUMN promo_post_counter INTEGER DEFAULT 0")
    except Exception as migration_err:
        logger.error(f"Migration error for post_groups: {migration_err}")
        
    try:
        cursor.execute("PRAGMA table_info(postbots)")
        cols = [col[1] for col in cursor.fetchall()]
        if "is_active" not in cols:
            logger.info("Adding is_active column to postbots table...")
            cursor.execute("ALTER TABLE postbots ADD COLUMN is_active INTEGER DEFAULT 1")
    except Exception as migration_err2:
        logger.error(f"Migration error for postbots: {migration_err2}")
        
    # Table to track dispatched promo posts and their expiration
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promo_posts (
            chat_id INTEGER,
            message_id INTEGER,
            group_id INTEGER,
            expires_at INTEGER,
            original_text TEXT,
            original_kb TEXT,
            post_type TEXT,
            PRIMARY KEY (chat_id, message_id)
        )
    """)
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            group_id INTEGER,
            user_id INTEGER,
            discount_amount INTEGER,
            created_at INTEGER,
            expires_at INTEGER,
            FOREIGN KEY (group_id) REFERENCES post_groups (group_id) ON DELETE CASCADE
        )
    """)
    
    try:
        cursor.execute("PRAGMA table_info(promo_codes)")
        cols = [col[1] for col in cursor.fetchall()]
        if "user_name" not in cols:
            logger.info("Adding user_name column to promo_codes...")
            cursor.execute("ALTER TABLE promo_codes ADD COLUMN user_name TEXT")
        if "user_username" not in cols:
            logger.info("Adding user_username column to promo_codes...")
            cursor.execute("ALTER TABLE promo_codes ADD COLUMN user_username TEXT")
    except Exception as migration_err:
        logger.error(f"Migration error for promo_codes: {migration_err}")
        
    try:
        cursor.execute("PRAGMA table_info(chats)")
        cols = [col[1] for col in cursor.fetchall()]
        if "sent_posts_count" not in cols:
            logger.info("Adding sent_posts_count column to chats...")
            cursor.execute("ALTER TABLE chats ADD COLUMN sent_posts_count INTEGER DEFAULT 0")
    except Exception as migration_err:
        logger.error(f"Migration error for chats: {migration_err}")

    try:
        cursor.execute("PRAGMA table_info(promo_posts)")
        cols = [col[1] for col in cursor.fetchall()]
        if "original_text" not in cols:
            logger.info("Adding original_text column to promo_posts...")
            cursor.execute("ALTER TABLE promo_posts ADD COLUMN original_text TEXT")
        if "original_kb" not in cols:
            logger.info("Adding original_kb column to promo_posts...")
            cursor.execute("ALTER TABLE promo_posts ADD COLUMN original_kb TEXT")
        if "post_type" not in cols:
            logger.info("Adding post_type column to promo_posts...")
            cursor.execute("ALTER TABLE promo_posts ADD COLUMN post_type TEXT")
    except Exception as migration_err:
        logger.error(f"Migration error for promo_posts: {migration_err}")
        
    conn.commit()
    conn.close()

# Users
def get_user_lang(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'en'

def set_user_lang(user_id, username, lang):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, language)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            language = excluded.language
    """, (user_id, username, lang))
    conn.commit()
    conn.close()

# Admins
def get_superadmin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM control_admins WHERE role = 'superadmin'")
    row = cursor.fetchone()
    conn.close()
    return row if row else None

def add_superadmin(user_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM control_admins WHERE role = 'superadmin'")
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("""
        INSERT INTO control_admins (user_id, username, role)
        VALUES (?, ?, 'superadmin')
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            role = 'superadmin'
    """, (user_id, username))
    conn.commit()
    conn.close()
    return True

def add_admin(user_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO control_admins (user_id, username, role)
        VALUES (?, ?, 'admin')
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            role = 'admin'
    """, (user_id, username))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM control_admins WHERE user_id = ? AND role != 'superadmin'", (user_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0

def get_admins():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role FROM control_admins")
    rows = cursor.fetchall()
    conn.close()
    return rows

def is_admin(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM control_admins WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def is_superadmin(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM control_admins WHERE user_id = ? AND role = 'superadmin'", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# Postbots
def add_postbot(token, username, owner_id, owner_username, proxy=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO postbots (token, username, proxy, is_active)
            VALUES (?, ?, ?, 1)
        """, (token, username, proxy))
        bot_id = cursor.lastrowid
        
        # Add creator as owner in postbot_admins using owner_username
        cursor.execute("""
            INSERT INTO postbot_admins (bot_id, user_id, username, role)
            VALUES (?, ?, ?, 'owner')
        """, (bot_id, owner_id, owner_username))
        
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
        bot_id = None
    finally:
        conn.close()
    return success, bot_id

def get_postbot(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id, token, username, proxy, is_active FROM postbots WHERE bot_id = ?", (bot_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_postbot_by_token(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id, token, username, proxy, is_active FROM postbots WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_postbots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id, token, username, proxy, is_active FROM postbots")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_postbot(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM postbots WHERE bot_id = ?", (bot_id,))
    cursor.execute("DELETE FROM postbot_admins WHERE bot_id = ?", (bot_id,))
    
    # Cascade delete postgroups
    cursor.execute("SELECT group_id FROM post_groups WHERE bot_id = ?", (bot_id,))
    groups = cursor.fetchall()
    for g in groups:
        gid = g[0]
        cursor.execute("DELETE FROM posts WHERE group_id = ?", (gid,))
        cursor.execute("DELETE FROM chats WHERE group_id = ?", (gid,))
        cursor.execute("DELETE FROM promo_posts WHERE group_id = ?", (gid,))
        cursor.execute("DELETE FROM promo_codes WHERE group_id = ?", (gid,))
        
    cursor.execute("DELETE FROM post_groups WHERE bot_id = ?", (bot_id,))
    conn.commit()
    conn.close()

def update_postbot_username(bot_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE postbots SET username = ? WHERE bot_id = ?", (username, bot_id))
    conn.commit()
    conn.close()

def update_postbot_active_status(bot_id, is_active):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE postbots SET is_active = ? WHERE bot_id = ?", (is_active, bot_id))
    conn.commit()
    conn.close()

# PostBot Admins Management
def add_postbot_admin(bot_id, user_id, username, role='admin'):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO postbot_admins (bot_id, user_id, username, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(bot_id, user_id) DO UPDATE SET
                username = excluded.username,
                role = excluded.role
        """, (bot_id, user_id, username, role))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        conn.close()
    return success

def remove_postbot_admin(bot_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Cannot remove owner
    cursor.execute("DELETE FROM postbot_admins WHERE bot_id = ? AND user_id = ? AND role != 'owner'", (bot_id, user_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

def get_postbot_admins(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role FROM postbot_admins WHERE bot_id = ?", (bot_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def is_postbot_admin(bot_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM postbot_admins WHERE bot_id = ? AND user_id = ?", (bot_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def is_postbot_owner(bot_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM postbot_admins WHERE bot_id = ? AND user_id = ? AND role = 'owner'", (bot_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# PostGroups
def add_post_group(bot_id, name, passcode, default_kb, interval, time_range):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO post_groups (bot_id, name, passcode, default_kb, interval, time_range)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (bot_id, name, passcode, default_kb, interval, time_range))
        conn.commit()
        gid = cursor.lastrowid
    except sqlite3.IntegrityError:
        gid = None
    finally:
        conn.close()
    return gid

def get_post_group(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active FROM post_groups WHERE group_id = ?", (group_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_post_group_by_passcode(passcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active FROM post_groups WHERE passcode = ?", (passcode,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_post_group_by_passcode_for_bot(passcode, bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active FROM post_groups WHERE passcode = ? AND bot_id = ?", (passcode, bot_id))
    row = cursor.fetchone()
    conn.close()
    return row

def get_post_groups(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, bot_id, name, passcode, default_kb, interval, time_range, is_active FROM post_groups WHERE bot_id = ?", (bot_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_post_group(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post_groups WHERE group_id = ?", (group_id,))
    cursor.execute("DELETE FROM posts WHERE group_id = ?", (group_id,))
    cursor.execute("DELETE FROM chats WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

def update_post_group_interval(group_id, interval):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET interval = ? WHERE group_id = ?", (interval, group_id))
    conn.commit()
    conn.close()

def update_post_group_time_range(group_id, time_range):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET time_range = ? WHERE group_id = ?", (time_range, group_id))
    conn.commit()
    conn.close()

def update_post_group_default_kb(group_id, kb):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET default_kb = ? WHERE group_id = ?", (kb, group_id))
    conn.commit()
    conn.close()

# Posts
def add_post(group_id, type_, file_id, text_msg, kb):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (group_id, type, file_id, text_msg, kb)
        VALUES (?, ?, ?, ?, ?)
    """, (group_id, type_, file_id, text_msg, kb))
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return post_id

def get_posts(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT post_id, group_id, type, file_id, text_msg, kb FROM posts WHERE group_id = ?", (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_post(post_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()

def delete_all_posts(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

# Chats
def add_chat(chat_id, group_id, title, username=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO chats (chat_id, group_id, title, username, last_posted_index)
            VALUES (?, ?, ?, ?, -1)
            ON CONFLICT(chat_id, group_id) DO UPDATE SET title = excluded.title, username = excluded.username
        """, (chat_id, group_id, title, username))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        conn.close()
    return success

def get_chats(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, group_id, title, username, last_posted_index FROM chats WHERE group_id = ?", (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_chat_sent_posts_count(chat_id, group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sent_posts_count FROM chats WHERE chat_id = ? AND group_id = ?", (chat_id, group_id))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def increment_chat_post_counter(chat_id, group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET sent_posts_count = sent_posts_count + 1 WHERE chat_id = ? AND group_id = ?", (chat_id, group_id))
    conn.commit()
    conn.close()

def get_chat(chat_id, group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, group_id, title, username, last_posted_index FROM chats WHERE chat_id = ? AND group_id = ?", (chat_id, group_id))
    row = cursor.fetchone()
    conn.close()
    return row

def update_chat_last_index(chat_id, group_id, last_index):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET last_posted_index = ? WHERE chat_id = ? AND group_id = ?", (last_index, chat_id, group_id))
    conn.commit()
    conn.close()

def delete_chat(chat_id, group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE chat_id = ? AND group_id = ?", (chat_id, group_id))
    conn.commit()
    conn.close()

def update_chat_group(chat_id, src_group_id, dest_group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET group_id = ?, last_posted_index = -1 WHERE chat_id = ? AND group_id = ?", (dest_group_id, chat_id, src_group_id))
    conn.commit()
    conn.close()

def update_chat_details(chat_id, group_id, title, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ?, username = ? WHERE chat_id = ? AND group_id = ?", (title, username, chat_id, group_id))
    conn.commit()
    conn.close()

def update_post_group_active(group_id, is_active):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET is_active = ? WHERE group_id = ?", (is_active, group_id))
    conn.commit()
    conn.close()

def deactivate_all_post_groups(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET is_active = 0 WHERE bot_id = ?", (bot_id,))
    conn.commit()
    conn.close()

def activate_all_post_groups(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET is_active = 1 WHERE bot_id = ?", (bot_id,))
    conn.commit()
    conn.close()

def update_post_group_promo_settings(group_id, min_discount, max_discount, trigger_emoji, instruction_text, success_text, duration_hours, duration_text, post_duration_hours, post_frequency):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE post_groups SET
            promo_discount_min = ?,
            promo_discount_max = ?,
            promo_trigger_emoji = ?,
            promo_text_instruction = ?,
            promo_text_success = ?,
            promo_duration_hours = ?,
            promo_text_duration = ?,
            promo_post_duration_hours = ?,
            promo_post_frequency = ?
        WHERE group_id = ?
    """, (min_discount, max_discount, trigger_emoji, instruction_text, success_text, duration_hours, duration_text, post_duration_hours, post_frequency, group_id))
    conn.commit()
    conn.close()

def increment_post_group_promo_counter(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET promo_post_counter = promo_post_counter + 1 WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

def add_promo_post(chat_id, message_id, group_id, expires_at, original_text=None, original_kb=None, post_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO promo_posts (chat_id, message_id, group_id, expires_at, original_text, original_kb, post_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (chat_id, message_id, group_id, expires_at, original_text, original_kb, post_type))
    conn.commit()
    conn.close()

def get_active_promo_post(chat_id, message_id):
    import time
    now = int(time.time())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, expires_at, original_text, original_kb, post_type FROM promo_posts WHERE chat_id = ? AND message_id = ? AND expires_at > ?", (chat_id, message_id, now))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_expired_promo_posts():
    import time
    now = int(time.time())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promo_posts WHERE expires_at <= ?", (now,))
    conn.commit()
    conn.close()

def delete_promo_post(chat_id, message_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promo_posts WHERE chat_id = ? AND message_id = ?", (chat_id, message_id))
    conn.commit()
    conn.close()

def update_post_group_promo_enabled(group_id, enabled):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE post_groups SET promo_enabled = ? WHERE group_id = ?", (enabled, group_id))
    conn.commit()
    conn.close()

def add_promo_code(code, group_id, user_id, discount_amount, created_at, expires_at, user_name=None, user_username=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO promo_codes (code, group_id, user_id, discount_amount, created_at, expires_at, user_name, user_username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, group_id, user_id, discount_amount, created_at, expires_at, user_name, user_username))
    conn.commit()
    conn.close()

def get_promo_code(code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, group_id, user_id, discount_amount, created_at, expires_at, user_name, user_username FROM promo_codes WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_promo_code(code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promo_codes WHERE code = ?", (code,))
    conn.commit()
    conn.close()

def delete_all_promo_codes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promo_codes")
    conn.commit()
    conn.close()

def get_chat_by_id(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, group_id, title, username, last_posted_index FROM chats WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_post_group_promo_settings(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT promo_enabled, promo_discount_min, promo_discount_max, promo_trigger_emoji,
               promo_text_instruction, promo_text_success, promo_duration_hours, promo_text_duration,
               promo_post_duration_hours, promo_post_frequency, promo_post_counter
        FROM post_groups WHERE group_id = ?
    """, (group_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_active_user_promo(group_id, user_id):
    import time
    now = int(time.time())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT code, discount_amount, expires_at 
        FROM promo_codes 
        WHERE group_id = ? AND user_id = ? AND expires_at > ?
        LIMIT 1
    """, (group_id, user_id, now))
    row = cursor.fetchone()
    conn.close()
    return row

# Initialize tables
init_db()
