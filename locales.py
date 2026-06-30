# -*- coding: utf-8 -*-

LOCALES = {
    'en': {
        'start_welcome': "👋 Welcome to Control Aya Bot",
        'start_info': (
            "📋 <b>Your Profile Information:</b>\n\n"
            "👤 <b>Name:</b> {name}\n"
            "🏷️ <b>Username:</b> {username}\n"
            "🆔 <b>ID:</b> <code>{user_id}</code> <i>(tap to copy)</i>\n"
            "🌐 <b>Language:</b> {lang_code}\n\n"
            "Use the menu below to navigate."
        ),
        'enter_password': "🔑 <b>Welcome!</b> To become the <b>Superadmin</b>, please enter the system password:",
        'success_superadmin': "🟢 <b>Success!</b> You are now the <b>Superadmin</b>. No other user can claim this role.",
        'already_has_superadmin': "🚫 <b>Access Denied!</b> A Superadmin has already been set for this system.",
        'wrong_password': "❌ <b>Incorrect password!</b> Access denied.",
        'not_authorized': "🚫 <b>Access Denied!</b> You are not an administrator of this bot.",
        
        # Menu & Navigation
        'menu_title': "🤖 <b>Main Menu</b>",
        'btn_add_bot': "➕ Add Bot",
        'btn_bot_list': "📋 Bot List",
        'btn_add_admin': "👥 Manage Admins",
        'btn_language': "🌐 Language",
        'btn_help': "ℹ️ Help",
        'btn_back': "⬅️ Back",
        'btn_cancel': "❌ Cancel",
        'btn_skip': "⏭️ Skip",
        'fsm_reset_success': "🧹 State has been successfully reset! You can start again.",
        'btn_confirm_delete': "🗑️ Yes, Delete",
        'btn_confirm': "✅ Confirm",
        'btn_posts': "📋 Posts",
        'btn_sync_bots': "🔄 Sync Bots",
        
        # Bot Sync
        'sync_select_source': "🔄 <b>Select Source Bot:</b>\n\nChoose the postbot from which you want to copy all settings, groups, and posts.",
        'sync_select_target': "🔄 <b>Select Target Bot:</b>\n\nChoose the backup postbot where you want to copy all the content.",
        'sync_confirm': "🔄 <b>Confirm Synchronization</b>\n\n<b>Source Bot:</b> @{source}\n<b>Target Bot:</b> @{target}\n\n<i>Note: All copied groups on the target bot will be initially disabled (inactive) to avoid double posting. Media posts will be transferred via a download/upload flow with a 3-second delay.</i>",
        'sync_in_progress': "🔄 <b>Synchronization in progress...</b>\n\nRunning checks, copying settings, and transferring media files. Please wait, this might take a few minutes.",
        'sync_success': "✅ <b>Synchronization Completed Successfully!</b>\n\nGroups, settings, and posts have been copied to @{target} (disabled by default).\n\nTotal groups synced: {groups}\nTotal posts copied: {posts}",
        'sync_error_missing_chats': "❌ <b>Synchronization Failed!</b>\n\nThe target bot @{target} is not added or lacks administrator permissions (post/delete messages) in the following groups/channels:\n\n{chats}\n\nPlease add the target bot to these chats and try again.",
        'sync_error_same_bot': "❌ You cannot select the same bot as both source and destination.",
        'sync_error_no_groups': "❌ The source bot has no postgroups configured to copy.",
        'sync_error_not_owner': "❌ You must be the owner of both bots to synchronize them.",
        'sync_step_check': "🔄 <b>Step 1/3: Checking target bot presence in groups...</b>",
        'sync_step_groups': "🔄 <b>Step 2/3: Copying post groups and settings...</b>",
        'sync_step_posts': "🔄 <b>Step 3/3: Copying posts and transferring media ({current}/{total})...</b>",
        
        # Help
        'help_title': "ℹ️ <b>Help & Information</b>",
        'help_text': (
            "ℹ️ <b>Control Bot Guide & Scenarios</b>\n\n"
            "This bot manages satellite posting bots.\n\n"
            "📋 <b>Action Scenarios:</b>\n\n"
            "1️⃣ <b>How to Add a New Postbot:</b>\n"
            "1. Go to @BotFather, create a bot, and copy its <b>Token</b>. In Bot Settings, make sure <b>Allow Groups?</b> is Enabled, and configure <b>Group Admin Rights</b> and <b>Channel Admin Rights</b> to grant the bot all administrator permissions (including Add New Admins).\n"
            "2. In this Control Bot, click <b>Bot List</b> -> <b>➕ Add Bot</b>.\n"
            "3. Send the Telegram ID of the bot's admin.\n"
            "4. Send their Username (without @).\n"
            "5. Send the API Token.\n"
            "6. Send the Proxy URL (http:// or socks5://) or click <b>Skip</b>.\n"
            "<i>The bot will test the connection and launch!</i>\n\n"
            "2️⃣ <b>How to Sync Settings Between Bots:</b>\n"
            "1. Click <b>🔄 Sync Bots</b> on the main menu.\n"
            "2. Select the <b>Source Bot</b> (where to copy settings/posts from).\n"
            "3. Select the <b>Target Bot</b> (where to copy to).\n"
            "4. Confirm synchronization.\n"
            "<i>(All synced groups on the target bot are disabled by default to avoid double posting).</i>\n\n"
            "💡 <b>Useful Commands:</b>\n"
            "• `/start` or `/menu` — opens the main menu and clears the active dialog state.\n"
            "• `/reset` — forces a full reset of the active dialog state if you are stuck or deleted a chat."
        ),
        
        # Language Selection
        'select_language': "🌐 <b>Select your interface language:</b>",
        'lang_changed': "🟢 Language changed successfully!",
        
        # Add Bot FSM
        'add_bot_start': "👤 <b>Step 1/4:</b> Send the Telegram user ID of the person who will be the administrator/owner of this postbot:",
        'add_bot_admin_username': "👤 <b>Step 2/4:</b> Send the Telegram username of the postbot administrator:",
        'invalid_admin_id': "❌ Invalid ID! The ID must be a number. Please try again.",
        'add_bot_token': "🔑 <b>Step 3/4:</b> Send the Telegram Bot API Token for the postbot (from @BotFather):",
        'invalid_token': "❌ Invalid token format! It should look like <code>123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ</code>. Please try again.",
        'add_bot_proxy': (
            "🌐 <b>Step 4/4:</b> Send the Proxy URL.\n"
            "Format:\n"
            "• <code>socks5://username:password@ip:port</code>\n"
            "• <code>http://username:password@ip:port</code>\n\n"
            "Press <b>Skip</b> if you do not want to use a proxy."
        ),
        'invalid_proxy': "❌ Invalid proxy URL format. Please make sure it starts with <code>http://</code> or <code>socks5://</code> (or press Skip).",
        'testing_connection': "🔄 Testing connection to Telegram API and sending verification message...",
        'test_msg_failed': "❌ Failed to send test message to the postbot admin! Make sure they have started a chat with the postbot.",
        'invalid_token_error': "❌ The provided token is invalid or the proxy blocked the request.",
        'bot_added_success': "🟢 <b>Postbot successfully added and started!</b>\n🤖 Bot: @{username}",
        
        # Bot List
        'bot_list_title': "🤖 <b>List of Configured Postbots:</b>",
        'no_bots': "🤖 <b>List of Configured Postbots:</b>\n\n📭 No postbots configured yet.",
        'bot_card': (
            "🤖 <b>Bot Username:</b> @{username}\n"
            "👑 <b>Owner:</b> @{owner}\n"
            "🔑 <b>Token:</b> <code>{token}</code>\n"
            "🌐 <b>Proxy:</b> <code>{proxy}</code>"
        ),
        'btn_update_data': "🔄 Update Data",
        'btn_delete_bot': "🗑️ Delete Bot",
        'delete_confirm': "⚠️ Are you sure you want to delete <b>@{username}</b> from the database? This will stop the bot and delete its configuration.",
        'bot_deleted': "🗑️ Bot successfully deleted.",
        
        # Admin Management (Control Bot & PostBot Admins)
        'admin_list_title': "👥 <b>Administrators:</b>",
        'btn_add_new_admin': "➕ Add Admin",
        'enter_admin_id': "👤 Send the Telegram User ID of the new administrator:",
        'admin_added': "🟢 Administrator successfully added!",
        'admin_removed': "🗑️ Administrator removed successfully.",
        'cannot_remove_self': "❌ You cannot remove yourself.",
        'cannot_remove_superadmin': "❌ You cannot remove the Superadmin.",
        'btn_manage_bot_admins': "👥 Bot Admins",
        'postbot_admin_list_title': "👥 <b>PostBot @{username} Administrators:</b>",
        'cannot_remove_owner': "❌ You cannot remove the original Owner.",
        'enter_admin_username': "🏷️ Send the Telegram Username of the new administrator:",
        'admin_card_title': "👤 <b>Administrator Profile</b>",
        'admin_card_details': "🆔 <b>ID:</b> <code>{user_id}</code>\n🏷️ <b>Username:</b> @{username}\n👑 <b>Role:</b> {role}",
        'btn_refresh_admin': "🔄 Refresh Info",
        'btn_delete_admin': "🗑️ Delete Admin",
        'admin_refreshed': "🟢 Admin username updated to @{username}!",
        'admin_refresh_failed': "❌ Could not retrieve user info from Telegram: {error}",
        
        # PostGroups Translations
        'btn_postgroups': "📦 PostGroups",
        'btn_create_group': "➕ Create PostGroup",
        'pg_list_title': "📋 <b>PostGroups for @{username}:</b>",
        'pg_no_groups': "📭 No PostGroups configured yet.",
                'pg_card': (
            "📦 <b>PostGroup Name:</b> {name}\n"
            "🔑 <b>Password:</b> <code>{passcode}</code>\n"
            "⚡ <b>Posting Status:</b> {status}\n"
            "🎁 <b>Attention Grabber:</b> {promo_status}\n"
            "📝 <b>Posts Count:</b> <code>{post_count}</code>\n"
            "⏱️ <b>Post Interval:</b> <code>{interval}</code> seconds\n"
            "🕒 <b>Israel Posting Window:</b> <code>{time_range}</code>\n"
            "👥 <b>Linked Groups/Channels Count:</b> <code>{chat_count}</code>\n\n"
            "🎹 <b>Default Keyboard:</b>\n{kb_schema}"
        ),
        'btn_delete_group': "🗑️ Delete Group",
        'btn_add_post': "➕ Add Post",
        'btn_del_all_posts': "🗑️ Delete All Posts",
        'btn_del_any_post': "🗑️ Delete Any Post",
        'btn_edit_settings': "⚙️ Edit Settings",
        'create_group_name': "✏️ Enter the Name for the new PostGroup:",
        'create_group_layout': "📱 <b>Default Keyboard Setup:</b>\n\nThe keyboard layout is specified by digits separated by hyphens. Each digit represents the number of buttons in that row.\nExample: <code>1-3-1-2</code> means:\n• Row 1: 1 button\n• Row 2: 3 buttons\n• Row 3: 1 button\n• Row 4: 2 buttons\n\nSend the layout string (e.g., <code>1-3-1-2</code>) or <b><code>0</code></b> if no keyboard is needed.",
        'create_group_kb_intro': "⌨️ Now let's set up the default inline keyboard. Send the button label/text:",
        'create_group_kb_url': "🔗 Send the redirect URL (link) for this button:",
        'create_group_kb_status': "✅ Button added. Add another button, or finish setting up the keyboard:",
        'btn_add_more_buttons': "➕ Add Button",
        'btn_finish_kb': "🟢 Finish Keyboard Setup",
        'create_group_passcode': "🔑 Enter a unique password for linking groups/channels to this PostGroup:",
        'create_group_interval': "⏱️ Enter the posting periodicity/interval in seconds (minimum 60 seconds).\n\n💡 Time is specified in seconds. For example:\n• 30 minutes = 1800 seconds\n• 1 hour = 3600 seconds",
        'create_group_timerange': "🕒 Enter the posting time window in Israel time format (HH:MM-HH:MM, e.g., 08:00-22:00 or 00:00-24:00):",
        'invalid_interval': "❌ Invalid interval! Must be an integer >= 60.",
        'invalid_time_range': "❌ Invalid time range! Please use format HH:MM-HH:MM (e.g. 08:00-22:00).",
        'duplicate_passcode': "❌ This password is already taken. Please enter a different password.",
        'create_group_confirm': (
            "📋 <b>Confirm PostGroup Creation:</b>\n\n"
            "📦 <b>Name:</b> {name}\n"
            "📱 <b>Buttons per Row:</b> {layout}\n"
            "🔑 <b>Password:</b> <code>{passcode}</code>\n"
            "⏱️ <b>Interval:</b> {interval} seconds\n"
            "🕒 <b>Israel Range:</b> {time_range}\n"
            "🎹 <b>Keyboard buttons:</b> {buttons}"
        ),
        'group_added_success': "🟢 PostGroup created successfully!",
        'confirm_delete_group': "⚠️ Are you sure you want to delete the PostGroup <b>{name}</b>? This will delete all its posts and unlink all chats.",
        'group_deleted': "🗑️ PostGroup deleted.",
        
        # Post Creation inside PostGroup
        'add_post_start': "📝 Send the post content (photo, video, gif/animation, or text):",
        'add_post_confirm': "❓ Do you want to save and add this post to the group?",
        'post_added_to_group': "🟢 Post successfully added to the group!",
        
        # PostGroup settings editing
        'edit_settings_menu': "⚙️ <b>Edit PostGroup Settings:</b>",
        'btn_edit_interval': "⏱️ Edit Interval",
        'btn_edit_timerange': "🕒 Edit Time Window",
        'btn_edit_kb': "⌨️ Edit default Keyboard",
        'enter_interval': "⏱️ Enter the posting interval in seconds (minimum 60 seconds).\n\n💡 Time is specified in seconds. For example:\n• 30 minutes = 1800 seconds\n• 1 hour = 3600 seconds",
        'interval_updated': "🟢 Posting interval updated successfully!",
        'enter_timerange': "🕒 Enter Israel posting time window (HH:MM-HH:MM, e.g. 08:00-22:00):",
        'timerange_updated': "🟢 Time window updated successfully!",
        
        # Postbot Help
        'pb_help_text': (
            "ℹ️ <b>Postbot Guide & Scenarios</b>\n\n"
            "This bot automates content posting to your Telegram channels/groups.\n\n"
            "📋 <b>Action Scenarios:</b>\n\n"
            "1️⃣ <b>How to Setup Posting to a Channel/Group:</b>\n"
            "1. Click <b>📦 PostGroups</b> -> <b>➕ Create Group</b>.\n"
            "2. Enter a name, button layout (or 0), and a unique password/passcode (e.g., <code>mycode123</code>).\n"
            "3. Set the posting interval (in seconds) and active time window (e.g., <code>09:00-22:00</code>). Confirm creation.\n"
            "4. Add this bot as an <b>Administrator</b> in your channel/group (with permission to post and delete messages).\n"
            "5. Send your passcode (e.g., <code>mycode123</code>) directly into the channel/group.\n"
            "<i>The bot will delete the passcode message and successfully link the chat!</i>\n\n"
            "2️⃣ <b>How to Queue a New Post:</b>\n"
            "1. Click <b>📦 PostGroups</b> -> select your Group -> <b>➕ Add Post</b>.\n"
            "2. Send your content (text, photo, video, or GIF).\n"
            "3. Attach custom buttons if needed, then click <b>Confirm</b>.\n"
            "<i>The post is added to the queue and will be published according to the interval.</i>\n\n"
            "3️⃣ <b>How to Setup Reaction Promos (Attention Grabber):</b>\n"
            "1. Select your Group -> <b>🛠️ Settings</b> -> <b>📢 Promo Settings</b> -> <b>⚙️ Setup Promo</b>.\n"
            "2. Follow the steps: set discount range, emoji trigger, duration, and texts.\n"
            "3. Click <b>Enable</b> to start monitoring reactions.\n"
            "<i>The bot will automatically publish promo codes when the emoji target is met!</i>\n\n"
            "💡 <b>Useful Commands:</b>\n"
            "• `/start` or `/menu` — opens the main menu and clears the active dialog state.\n"
            "• `/reset` — forces a full reset of the active dialog state if you are stuck."
        ),
        
        # Toggle Posting
        'btn_toggle_posting_on': "🟢 Enable Posting",
        'btn_toggle_posting_off': "🔴 Disable Posting",
        'btn_promo_enable': "🟢 Enable",
        'btn_promo_disable': "🔴 Disable",
        'posting_status': "⚡ <b>Posting Status:</b> {status}",
        'status_enabled': "🟢 Enabled",
        'status_disabled': "🔴 Disabled",
        'chat_removed_alert': "⚠️ <b>Chat Access Lost!</b>\n\nLink to channel/group <b>{title}</b> (ID: <code>{chat_id}</code>) in PostGroup <b>{group_name}</b> was removed because the bot was blocked or the chat no longer exists.",
        
        # Chats Tab
        'btn_chats': "👥 Chats",
        'btn_transfer': "🔄 Transfer",
        'btn_unlink': "🗑️ Unlink",
        'btn_refresh_chats': "🔄 Refresh Info",
        'chats_list_title': "👥 <b>Connected Chats for {group_name}:</b>",
        'chat_details_title': (
            "👥 <b>Chat Details:</b>\n\n"
            "📝 <b>Title:</b> {title}\n"
            "🏷️ <b>Username:</b> {username}\n"
            "🆔 <b>ID:</b> <code>{chat_id}</code>\n"
            "👥 <b>Subscribers/Members:</b> <code>{member_count}</code>"
        ),
        'chat_transferred': "🟢 Chat successfully transferred to {group_name}!",
        'chat_unlinked': "🗑️ Chat successfully unlinked.",
        'select_transfer_group': "🔄 <b>Select destination PostGroup to transfer chat:</b>",
                'no_other_groups': "❌ No other postgroups available for transfer.",
        'btn_settings': "⚙️ Settings",
        'settings_menu_title': "⚙️ <b>PostBot Settings</b>\n\n📋 <b>Groups Status:</b>\n{group_list}",
        'btn_stop_all_groups': "🔴 Stop all groups",
        'btn_start_all_groups': "🟢 Start all groups",
        'all_groups_stopped': "🔴 All post-groups have been stopped.",
        'all_groups_started': "🟢 All post-groups have been started.",
        'create_group_kb_btn_text_prompt': "⌨️ <b>Row {row}, Button {col}:</b>\nSend the text/label for this button:",
        'create_group_kb_btn_url_prompt': "🔗 <b>Row {row}, Button {col}:</b>\nSend the link (URL) for this button:",
        'invalid_layout_schema': "❌ Invalid keyboard layout format! Please use digits separated by hyphens (e.g. 1-3-1-2) or enter 0.",
        'btn_edit_kb_success': "🟢 Default keyboard successfully updated!",
        'no_keyboard_configured': "No keyboard",
        'btn_promo_settings': "🎁 Attention Grabber",
        'promo_settings_title': "🎁 <b>Attention Grabber (Promo) Settings</b>\n\n⚡ <b>Status:</b> {status}\n🎯 <b>Trigger Reaction:</b> {trigger_emoji}\n💰 <b>Discount Range:</b> <code>{discount_range}%</code>\n⏱️ <b>Code Duration:</b> <code>{duration_hours} hours</code>\n⏳ <b>Post Offer Duration:</b> <code>{post_duration_hours} hours</code>\n📊 <b>Post Frequency:</b> <code>Every {post_frequency} posts</code>\n📝 <b>Instruction Text:</b> <i>{text_instruction}</i>\n🎉 <b>Success Text:</b> <i>{text_success}</i>\n⏳ <b>Duration Text:</b> <i>{text_duration}</i>",
        'btn_setup_promo': "⚙️ Configure all fields",
        'promo_discount_range_prompt': "💰 <b>Step 1/8:</b> Enter the discount percentage range (e.g. <code>5-10</code>):",
        'promo_trigger_emoji_prompt': "🎯 <b>Step 2/8:</b> Choose the reaction emoji that will trigger the discount:",
        'promo_post_duration_hours_prompt': "⏱️ <b>Step 3/8:</b> Enter the offer validity duration on the post in hours (e.g. <code>12</code>):",
        'promo_post_frequency_prompt': "📊 <b>Step 4/8:</b> Enter post frequency (attach promo once every N posts, e.g. <code>10</code>):",
        'promo_text_instruction_prompt': "📝 <b>Step 5/8:</b> Enter the instruction text.\nExample:\n<code>Press {emoji} and get a {discount_range}% discount. Offer is valid for {post_duration} hours.</code>",
        'promo_text_success_prompt': "🎉 <b>Step 6/8:</b> Enter the success text.\nExample:\n<code>You received a discount. Congratulations!</code>",
        'promo_duration_hours_prompt': "⏱️ <b>Step 7/8:</b> Enter the promo code validity duration in hours (e.g. <code>3</code>):",
        'promo_text_duration_prompt': "⏳ <b>Step 8/8:</b> Enter the duration alert text.\nExample:\n<code>The discount is valid for 3 hours! Order right now</code>",
        'invalid_discount_range': "❌ Invalid range format! Enter two numbers separated by a hyphen (e.g., 5-10).",
        'invalid_duration_hours': "❌ Invalid duration! Must be a positive integer number of hours.",
        'setup_promo_first_alert': "⚠️ You must configure the Attention Grabber first!" 
    },
    'ru': {
        'start_welcome': "👋 Добро пожаловать в Control Aya Bot",
        'start_info': (
            "📋 <b>Информация о вашем профиле:</b>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "🏷️ <b>Юзернейм:</b> {username}\n"
            "🆔 <b>ID:</b> <code>{user_id}</code> <i>(нажмите для копирования)</i>\n"
            "🌐 <b>Язык профиля:</b> {lang_code}\n\n"
            "Используйте меню ниже для навигации."
        ),
        'enter_password': "🔑 <b>Добро пожаловать!</b> Чтобы стать <b>Суперадмином</b>, введите системный пароль:",
        'success_superadmin': "🟢 <b>Успешно!</b> Теперь вы являетесь <b>Суперадмином</b>. Никто другой не сможет получить эту роль.",
        'already_has_superadmin': "🚫 <b>Доступ запрещен!</b> Суперадмин для этой системы уже назначен.",
        'wrong_password': "❌ <b>Неверный пароль!</b> Доступ запрещен.",
        'not_authorized': "🚫 <b>Доступ запрещен!</b> Вы не являетесь администратором этого бота.",
        
        # Menu & Navigation
        'menu_title': "🤖 <b>Главное меню</b>",
        'btn_add_bot': "➕ Добавить бота",
        'btn_bot_list': "📋 Список ботов",
        'btn_add_admin': "👥 Управление админами",
        'btn_language': "🌐 Язык",
        'btn_help': "ℹ️ Помощь",
        'btn_back': "⬅️ Назад",
        'btn_cancel': "❌ Отмена",
        'btn_skip': "⏭️ Пропустить",
        'fsm_reset_success': "🧹 Состояние диалога успешно сброшено! Вы можете начать заново.",
        'btn_confirm_delete': "🗑️ Да, удалить",
        'btn_confirm': "✅ Подтвердить",
        'btn_posts': "📋 Посты",
        'btn_sync_bots': "🔄 Синхронизация ботов",
        
        # Bot Sync
        'sync_select_source': "🔄 <b>Выберите исходного бота:</b>\n\nВыберите постбота, с которого вы хотите скопировать все настройки, группы и посты.",
        'sync_select_target': "🔄 <b>Выберите целевого бота:</b>\n\nВыберите резервного постбота, в которого вы хотите скопировать весь контент.",
        'sync_confirm': "🔄 <b>Подтверждение синхронизации</b>\n\n<b>Исходный бот:</b> @{source}\n<b>Целевой бот:</b> @{target}\n\n<i>Примечание: Все скопированные группы на целевом боте будут изначально выключены (неактивны), чтобы избежать двойного постинга. Посты с медиафайлами будут скопированы через отправку и скачивание с задержкой в 3 секунды.</i>",
        'sync_in_progress': "🔄 <b>Выполняется синхронизация...</b>\n\nПроверяем доступ в группы, копируем настройки и переносим медиафайлы. Пожалуйста, подождите, это может занять несколько минут.",
        'sync_success': "✅ <b>Синхронизация успешно завершена!</b>\n\nГруппы, настройки и посты были успешно скопированы в @{target} (по умолчанию они выключены).\n\nСинхронизировано групп: {groups}\nСкопировано постов: {posts}",
        'sync_error_missing_chats': "❌ <b>Синхронизация не удалась!</b>\n\nЦелевой бот @{target} не добавлен или не имеет прав администратора (публикация/удаление сообщений) в следующих группах/каналах:\n\n{chats}\n\nПожалуйста, добавьте целевого бота в эти чаты и повторите попытку.",
        'sync_error_same_bot': "❌ Нельзя выбрать одного и того же бота в качестве источника и цели.",
        'sync_error_no_groups': "❌ У исходного бота нет настроенных групп для копирования.",
        'sync_error_not_owner': "❌ Вы должны быть владельцем обоих ботов для их синхронизации.",
        'sync_step_check': "🔄 <b>Шаг 1/3: Проверка присутствия резервного бота в группах...</b>",
        'sync_step_groups': "🔄 <b>Шаг 2/3: Копирование групп и настроек...</b>",
        'sync_step_posts': "🔄 <b>Шаг 3/3: Копирование постов и перенос медиафайлов ({current}/{total})...</b>",
        
        # Help
        'help_title': "ℹ️ <b>Помощь и информация</b>",
        'help_text': (
            "ℹ️ <b>Руководство и Сценарии Управления</b>\n\n"
            "Этот бот предназначен для создания и управления ботами-постерами.\n\n"
            "📋 <b>Пошаговые Сценарии Действий:</b>\n\n"
            "1️⃣ <b>Как добавить нового бота-постера:</b>\n"
            "1. Перейдите в @BotFather, создайте бота и скопируйте его <b>Токен</b>. В настройках бота (Bot Settings) обязательно включите добавление в группы (<b>Allow Groups?</b> -> Enabled), а также зайдите в разделы <b>Group Admin Rights</b> и <b>Channel Admin Rights</b> и предоставьте боту все права администратора, включая право добавления других администраторов (Add New Admins).\n"
            "2. В этом боте нажмите <b>Список ботов</b> -> <b>➕ Добавить бота</b>.\n"
            "3. Отправьте Telegram ID пользователя, который будет админом бота.\n"
            "4. Отправьте его Юзернейм (без символа @).\n"
            "5. Отправьте API Токен бота.\n"
            "6. Отправьте прокси (http:// или socks5://) либо нажмите <b>Пропустить</b>.\n"
            "<i>Бот проверит соединение и запустит постер!</i>\n\n"
            "2️⃣ <b>Как синхронизировать контент между ботами:</b>\n"
            "1. В главном меню выберите <b>🔄 Синхронизация ботов</b>.\n"
            "2. Выберите <b>Исходный бот</b> (откуда копировать настройки и посты).\n"
            "3. Выберите <b>Целевой бот</b> (куда копировать контент).\n"
            "4. Подтвердите синхронизацию.\n"
            "<i>(Группы на целевом боте будут отключены по умолчанию, чтобы избежать двойного постинга).</i>\n\n"
            "💡 <b>Полезные команды:</b>\n"
            "• `/start` или `/menu` — открывает главное меню и сбрасывает текущее состояние диалога.\n"
            "• `/reset` — принудительно сбрасывает состояние диалога, если вы застряли на каком-то шаге."
        ),
        
        # Language Selection
        'select_language': "🌐 <b>Выберите язык интерфейса:</b>",
        'lang_changed': "🟢 Язык успешно изменен!",
        
        # Add Bot FSM
        'add_bot_start': "👤 <b>Шаг 1/4:</b> Отправьте Telegram ID пользователя, который будет администратором/владельцем постбота:",
        'add_bot_admin_username': "👤 <b>Шаг 2/4:</b> Отправьте юзернейм (Username) администратора постбота:",
        'invalid_admin_id': "❌ Неверный ID! ID должен состоять только из цифр. Пожалуйста, попробуйте еще раз.",
        'add_bot_token': "🔑 <b>Шаг 3/4:</b> Отправьте API Токен постбота (от @BotFather):",
        'invalid_token': "❌ Неверный формат токена! Пример: <code>123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ</code>. Попробуйте еще раз.",
        'add_bot_proxy': (
            "🌐 <b>Шаг 4/4:</b> Отправьте URL прокси.\n"
            "Формат:\n"
            "• <code>socks5://username:password@ip:port</code>\n"
            "• <code>http://username:password@ip:port</code>\n\n"
            "Нажмите <b>Пропустить</b>, если прокси не требуется."
        ),
        'invalid_proxy': "❌ Неверный формат прокси! URL должен начинаться с <code>http://</code> или <code>socks5://</code> (или нажмите Пропустить).",
        'testing_connection': "🔄 Проверка подключения к Telegram API и отправка тестового сообщения...",
        'test_msg_failed': "❌ Не удалось отправить тестовое сообщение администратору постбота! Убедитесь, что он запустил чат с постботом.",
        'invalid_token_error': "❌ Указанный токен недействителен или прокси заблокировал запрос.",
        'bot_added_success': "🟢 <b>Постбот успешно добавлен и запущен!</b>\n🤖 Бот: @{username}",
        
        # Bot List
        'bot_list_title': "🤖 <b>Список настроенных постботов:</b>",
        'no_bots': "🤖 <b>Список настроенных постботов:</b>\n\n📭 Нет настроенных постботов.",
        'bot_card': (
            "🤖 <b>Юзернейм бота:</b> @{username}\n"
            "👑 <b>Владелец:</b> @{owner}\n"
            "🔑 <b>Токен:</b> <code>{token}</code>\n"
            "🌐 <b>Прокси:</b> <code>{proxy}</code>"
        ),
        'btn_update_data': "🔄 Обновить данные",
        'btn_delete_bot': "🗑️ Удалить бота",
                'delete_confirm': "⚠️ Вы уверены, что хотите удалить <b>@{username}</b> из базы данных? Это остановит его работу и удалит все его настройки.",
        'bot_deleted': "🗑️ Постбот успешно удален.",
        
        # Admin Management (Control Bot & PostBot Admins)
        'admin_list_title': "👥 <b>Администраторы:</b>",
        'btn_add_new_admin': "➕ Добавить админа",
        'enter_admin_id': "👤 Отправьте Telegram ID нового администратора:",
        'admin_added': "🟢 Администратор успешно добавлен!",
        'admin_removed': "🗑️ Администратор успешно удален.",
        'cannot_remove_self': "❌ Вы не можете удалить самого себя.",
        'cannot_remove_superadmin': "❌ Вы не можете удалить Суперадмина.",
        'btn_manage_bot_admins': "👥 Админы бота",
        'postbot_admin_list_title': "👥 <b>Администраторы постбота @{username}:</b>",
        'cannot_remove_owner': "❌ Вы не можете удалить первоначального Владельца.",
        'enter_admin_username': "🏷️ Отправьте юзернейм (Username) нового администратора:",
        'admin_card_title': "👤 <b>Карточка администратора</b>",
        'admin_card_details': "🆔 <b>ID:</b> <code>{user_id}</code>\n🏷️ <b>Username:</b> @{username}\n👑 <b>Role:</b> {role}",
        'btn_refresh_admin': "🔄 Обновить данные",
        'btn_delete_admin': "🗑️ Удалить администратора",
        'admin_refreshed': "🟢 Юзернейм администратора обновлен на @{username}!",
        'admin_refresh_failed': "❌ Не удалось получить данные пользователя из Telegram: {error}",
        
        # PostGroups Translations
        'btn_postgroups': "📦 Пост-группы",
        'btn_create_group': "➕ Создать пост-группу",
        'pg_list_title': "📋 <b>Пост-группы для @{username}:</b>",
        'pg_no_groups': "📭 Нет настроенных пост-групп.",
                'pg_card': (
            "📦 <b>Пост-группа:</b> {name}\n"
            "🔑 <b>Пароль:</b> <code>{passcode}</code>\n"
            "⚡ <b>Статус постинга:</b> {status}\n"
            "🎁 <b>Привлечение внимания:</b> {promo_status}\n"
            "📝 <b>Кол-во постов:</b> <code>{post_count}</code>\n"
            "⏱️ <b>Интервал постинга:</b> <code>{interval}</code> сек\n"
            "🕒 <b>Время постинга (Израиль):</b> <code>{time_range}</code>\n"
            "👥 <b>Кол-во подключенных чатов:</b> <code>{chat_count}</code>\n\n"
            "🎹 <b>Клавиатура по умолчанию:</b>\n{kb_schema}"
        ),
        'btn_delete_group': "🗑️ Удалить группу",
        'btn_add_post': "➕ Добавить пост",
        'btn_del_all_posts': "🗑️ Удалить все посты",
        'btn_del_any_post': "🗑️ Удалить конкретный пост",
        'btn_edit_settings': "⚙️ Настройки",
        'create_group_name': "✏️ Введите название для новой пост-группы:",
        'create_group_layout': "📱 <b>Настройка клавиатуры по умолчанию:</b>\n\nСхема клавиатуры задается цифрами через дефис. Каждая цифра указывает количество кнопок в соответствующем ряду.\nПример: <code>1-3-1-2</code> означает:\n• 1-й ряд: 1 кнопка\n• 2-й ряд: 3 кнопки\n• 3-й ряд: 1 кнопка\n• 4-й ряд: 2 кнопки\n\nОтправьте схему клавиатуры (например, <code>1-3-1-2</code>) или <b><code>0</code></b>, если клавиатура не нужна.",
        'create_group_kb_intro': "⌨️ Настроим клавиатуру по умолчанию. Отправьте текст/название кнопки:",
        'create_group_kb_url': "🔗 Отправьте ссылку (URL) для этой кнопки:",
        'create_group_kb_status': "✅ Кнопка добавлена. Вы можете добавить еще одну кнопку или завершить настройку:",
        'btn_add_more_buttons': "➕ Добавить еще кнопку",
        'btn_finish_kb': "🟢 Завершить настройку клавиатуры",
        'create_group_passcode': "🔑 Введите уникальный пароль/парокод для подключения чатов к этой группе:",
        'create_group_interval': "⏱️ Введите интервал постинга в секундах (минимум 60 секунд).\n\n💡 Время указывается в секундах. Например:\n• 30 минут = 1800 секунд\n• 1 час = 3600 секунд",
        'create_group_timerange': "🕒 Введите израильский диапазон времени постинга (ЧЧ:ММ-ЧЧ:ММ, например 08:00-22:00):",
        'invalid_interval': "❌ Неверный интервал! Должно быть целое число >= 60.",
        'invalid_time_range': "❌ Неверный формат времени! Пожалуйста, используйте формат ЧЧ:ММ-ЧЧ:ММ.",
        'duplicate_passcode': "❌ Этот пароль уже занят. Пожалуйста, придумайте другой.",
        'create_group_confirm': (
            "📋 <b>Подтвердите создание пост-группы:</b>\n\n"
            "📦 <b>Название:</b> {name}\n"
            "📱 <b>Кнопок в ряду:</b> {layout}\n"
            "🔑 <b>Парокод:</b> <code>{passcode}</code>\n"
            "⏱️ <b>Интервал:</b> {interval} сек\n"
            "🕒 <b>Диапазон времени (Израиль):</b> {time_range}\n"
            "🎹 <b>Кнопки клавиатуры:</b> {buttons}"
        ),
        'group_added_success': "🟢 Пост-группа успешно создана!",
        'confirm_delete_group': "⚠️ Вы уверены, что хотите удалить пост-группу <b>{name}</b>? Это удалит все её посты и привязанные чаты.",
        'group_deleted': "🗑️ Пост-группа успешно удалена.",
        
        # Post Creation inside PostGroup
        'add_post_start': "📝 Отправьте содержимое поста (фото, видео, анимацию/гифку или текст):",
        'add_post_confirm': "❓ Вы хотите сохранить и добавить этот пост в группу?",
        'post_added_to_group': "🟢 Пост успешно добавлен в группу!",
        
        # PostGroup settings editing
        'edit_settings_menu': "⚙️ <b>Редактирование настроек пост-группы:</b>",
        'btn_edit_interval': "⏱️ Изменить интервал",
        'btn_edit_timerange': "🕒 Изменить время",
        'btn_edit_kb': "⌨️ Изменить клавиатуру",
        'enter_interval': "⏱️ Введите интервал постинга в секундах (минимум 60 секунд).\n\n💡 Время указывается в секундах. Например:\n• 30 минут = 1800 секунд\n• 1 час = 3600 секунд",
        'interval_updated': "🟢 Интервал успешно изменен!",
        'enter_timerange': "🕒 Введите диапазон времени постинга по Израилю (ЧЧ:ММ-ЧЧ:ММ):",
        'timerange_updated': "🟢 Диапазон времени постинга успешно изменен!",
        
        # Postbot Help
        'pb_help_text': (
            "ℹ️ <b>Руководство и Сценарии Пост-Бота</b>\n\n"
            "Этот бот автоматически публикует контент в ваших каналах и группах.\n\n"
            "📋 <b>Пошаговые Сценарии Действий:</b>\n\n"
            "1️⃣ <b>Как настроить автопостинг в канал/группу:</b>\n"
            "1. Нажмите <b>📦 Группы постов</b> -> <b>➕ Создать группу</b>.\n"
            "2. Укажите название, шаблон клавиатуры (или 0) и уникальный пароль (например, <code>mycode123</code>).\n"
            "3. Задайте интервал (в секундах) и время работы (например, <code>09:00-22:00</code>). Подтвердите создание.\n"
            "4. Добавьте этого бота в ваш канал/группу в качестве <b>Администратора</b> (с правами на публикацию и удаление сообщений).\n"
            "5. Отправьте секретный пароль (например, <code>mycode123</code>) сообщением прямо в канал или группу.\n"
            "<i>Бот удалит это сообщение и успешно привяжет чат к вашей группе постов!</i>\n\n"
            "2️⃣ <b>Как добавить новый пост в очередь:</b>\n"
            "1. Откройте <b>📦 Группы постов</b> -> Выберите группу -> <b>➕ Добавить пост</b>.\n"
            "2. Отправьте контент (текст, фото, видео или GIF).\n"
            "3. При необходимости прикрепите кнопки и нажмите <b>Подтвердить</b>.\n"
            "<i>Пост добавится в очередь и опубликуется согласно настройкам интервала.</i>\n\n"
            "3️⃣ <b>Как настроить промокоды за реакции (Attention Grabber):</b>\n"
            "1. Откройте вашу Группу -> <b>🛠️ Настройки</b> -> <b>📢 Промокоды</b> -> <b>⚙️ Настроить промо</b>.\n"
            "2. Задайте размер скидки, эмодзи-триггер, длительность и тексты уведомлений.\n"
            "3. Нажмите <b>Включить</b> для активации.\n"
            "<i>Бот будет отслеживать реакции и автоматически выдавать скидочные коды при достижении цели!</i>\n\n"
            "💡 <b>Полезные команды:</b>\n"
            "• `/start` или `/menu` — открывает главное меню и сбрасывает текущее состояние диалога.\n"
            "• `/reset` — принудительно сбрасывает состояние диалога, если вы застряли на каком-то шаге."
        ),
        
        # Toggle Posting
        'btn_toggle_posting_on': "🟢 Включить постинг",
        'btn_toggle_posting_off': "🔴 Выключить постинг",
        'btn_promo_enable': "🟢 Включить",
        'btn_promo_disable': "🔴 Выключить",
        'posting_status': "⚡ <b>Статус постинга:</b> {status}",
        'status_enabled': "🟢 Включен",
        'status_disabled': "🔴 Выключен",
        'chat_removed_alert': "⚠️ <b>Доступ к чату утерян!</b>\n\nСвязь с каналом/группой <b>{title}</b> (ID: <code>{chat_id}</code>) в пост-группе <b>{group_name}</b> была удалена, так как бот был заблокирован или чат больше не существует.",
        
        # Chats Tab
        'btn_chats': "👥 Чаты",
        'btn_transfer': "🔄 Перенести",
        'btn_unlink': "🗑️ Отвязать",
        'btn_refresh_chats': "🔄 Обновить информацию",
        'chats_list_title': "👥 <b>Подключенные чаты для {group_name}:</b>",
        'chat_details_title': (
            "👥 <b>Детали чата:</b>\n\n"
            "📝 <b>Название:</b> {title}\n"
            "🏷️ <b>Юзернейм:</b> {username}\n"
            "🆔 <b>ID:</b> <code>{chat_id}</code>\n"
            "👥 <b>Участники/Подписчики:</b> <code>{member_count}</code>"
        ),
        'chat_transferred': "🟢 Чат успешно перенесен в {group_name}!",
        'chat_unlinked': "🗑️ Чат успешно отвязан.",
        'select_transfer_group': "🔄 <b>Выберите пост-группу для переноса чата:</b>",
                'no_other_groups': "❌ Нет других пост-групп для переноса.",
        'btn_settings': "⚙️ Настройки",
        'settings_menu_title': "⚙️ <b>Настройки Постбота</b>\n\n📋 <b>Статус групп:</b>\n{group_list}",
        'btn_stop_all_groups': "🔴 Выключить все группы",
        'btn_start_all_groups': "🟢 Включить все группы",
        'all_groups_stopped': "🔴 Все пост-группы успешно выключены.",
        'all_groups_started': "🟢 Все пост-группы успешно включены.",
        'create_group_kb_btn_text_prompt': "⌨️ <b>Ряд {row}, Кнопка {col}:</b>\nОтправьте текст/название для этой кнопки:",
        'create_group_kb_btn_url_prompt': "🔗 <b>Ряд {row}, Кнопка {col}:</b>\nОтправьте ссылку (URL) для этой кнопки:",
        'invalid_layout_schema': "❌ Неверный формат схемы клавиатуры! Пожалуйста, используйте цифры через дефис (например, 1-3-1-2) или введите 0.",
        'btn_edit_kb_success': "🟢 Клавиатура по умолчанию успешно обновлена!",
        'no_keyboard_configured': "Нет клавиатуры",
        'btn_promo_settings': "🎁 Привлечение внимания",
        'promo_settings_title': "🎁 <b>Настройки привлечения внимания (Промо)</b>\n\n⚡ <b>Статус:</b> {status}\n🎯 <b>Реакция-триггер:</b> {trigger_emoji}\n💰 <b>Диапазон скидки:</b> <code>{discount_range}%</code>\n⏱️ <b>Время кода:</b> <code>{duration_hours} ч.</code>\n⏳ <b>Время предложения на посте:</b> <code>{post_duration_hours} ч.</code>\n📊 <b>Периодичность:</b> <code>Каждые {post_frequency} постов</code>\n📝 <b>Текст привлечения:</b> <i>{text_instruction}</i>\n🎉 <b>Текст успеха:</b> <i>{text_success}</i>\n⏳ <b>Текст времени:</b> <i>{text_duration}</i>",
        'btn_setup_promo': "⚙️ Настроить все поля",
        'promo_discount_range_prompt': "💰 <b>Шаг 1/8:</b> Введите диапазон скидки в процентах (например, <code>5-10</code>):",
        'promo_trigger_emoji_prompt': "🎯 <b>Шаг 2/8:</b> Выберите смайлик-реакцию, которая будет запускать выдачу скидки:",
        'promo_post_duration_hours_prompt': "⏱️ <b>Шаг 3/8:</b> Введите время действия предложения на посте в часах (например, <code>12</code>):",
        'promo_post_frequency_prompt': "📊 <b>Шаг 4/8:</b> Введите периодичность постов (выдавать скидку раз в N постов, например, <code>10</code>):",
        'promo_text_instruction_prompt': "📝 <b>Шаг 5/8:</b> Введите текст привлечения внимания.\nПример:\n<code>Нажми {emoji} и получи скидку от {discount_range}%. Предложение действует {post_duration} час.</code>",
        'promo_text_success_prompt': "🎉 <b>Шаг 6/8:</b> Введите текст получения скидки.\nПример:\n<code>Вы получили скидку. Поздравляю!</code>",
        'promo_duration_hours_prompt': "⏱️ <b>Шаг 7/8:</b> Введите время действия промокода в часах (например, <code>3</code>):",
        'promo_text_duration_prompt': "⏳ <b>Шаг 8/8:</b> Введите сообщение под время действия.\nПример:\n<code>Скидка действует 3 часа! Заказывай прямо сейчас</code>",
        'invalid_discount_range': "❌ Неверный формат диапазона! Введите два числа через дефис (например, 5-10).",
        'invalid_duration_hours': "❌ Неверное время действия! Должно быть положительное целое число часов.",
        'setup_promo_first_alert': "⚠️ Сначала необходимо настроить привлечение внимания!" 
    },
    'he': {
        'start_welcome': "👋 ברוכים הבאים ל-Control Aya Bot",
        'start_info': (
            "📋 <b>פרטי הפרופיל שלך:</b>\n\n"
            "👤 <b>שם:</b> {name}\n"
            "🏷️ <b>שם משתמש:</b> {username}\n"
            "🆔 <b>מזהה (ID):</b> <code>{user_id}</code> <i>(לחץ להעתקה)</i>\n"
            "🌐 <b>שפת פרופיל:</b> {lang_code}\n\n"
            "השתמש בתפריט למטה כדי לנווט."
        ),
        'enter_password': "🔑 <b>ברוכים הבאים!</b> כדי להפוך ל-<b>Superadmin</b>, אנא הזן את סיסמת המערכת:",
        'success_superadmin': "🟢 <b>הצלחה!</b> כעת אתה ה-<b>Superadmin</b>. אף משתמש אחר לא יוכל לתושב לתפקיד זה.",
        'already_has_superadmin': "🚫 <b>הגישה נדחתה!</b> מנהל-על (Superadmin) כבר הוגדר במערכת.",
        'wrong_password': "❌ <b>סיסמה שגויה!</b> הגישה נדחתה.",
        'not_authorized': "🚫 <b>הגישה נדחתה!</b> אינך מנהל במערכת זו.",
        
        # Menu & Navigation
        'menu_title': "🤖 <b>תפריט ראשי</b>",
        'btn_add_bot': "➕ הוסף בוט",
        'btn_bot_list': "📋 רשימת בוטים",
        'btn_add_admin': "👥 ניהול מנהלים",
        'btn_language': "🌐 שפה",
        'btn_help': "ℹ️ עזרה",
        'btn_back': "⬅️ חזור",
        'btn_cancel': "❌ ביטול",
        'btn_skip': "⏭️ דלג",
        'fsm_reset_success': "🧹 המצב אופס בהצלחה! תוכל להתחיל מחדש.",
        'btn_confirm_delete': "🗑️ כן, מחק",
        'btn_confirm': "✅ אישור",
        'btn_posts': "📋 פוסטים",
        'btn_sync_bots': "🔄 סנכרון בוטים",
        
        # Bot Sync
        'sync_select_source': "🔄 <b>בחר בוט מקור:</b>\n\nבחר את הבוט שממנו תרצה להעתיק את כל ההגדרות, הקבוצות והפוסטים.",
        'sync_select_target': "🔄 <b>בחר בוט יעד:</b>\n\nבחר את בוט הגיבוי שאליו תרצה להעתיק את כל התוכן.",
        'sync_confirm': "🔄 <b>אישור סנכרון</b>\n\n<b>בוט מקור:</b> @{source}\n<b>בוט יעד:</b> @{target}\n\n<i>הערה: כל הקבוצות שיועתקו לבוט היעד יהיו כבויות (לא פעילות) בתחילה כדי למנוע פרסום כפול. פוסטים עם מדיה יועברו עם השהיה של 3 שניות.</i>",
        'sync_in_progress': "🔄 <b>הסנכרון מתבצע...</b>\n\nבודק חיבור לקבוצות, מעתיק הגדרות ומעביר קבצים. נא להמתין, זה עשוי לקחת מספר דקות.",
        'sync_success': "✅ <b>הסנכרון הושלם בהצלחה!</b>\n\nהקבוצות, ההגדרות והפוסטים הועתקו ל-@{target} (כבויים כברירת מחדל).\n\nקבוצות שסונכרנו: {groups}\nפוסטים שהועתקו: {posts}",
        'sync_error_missing_chats': "❌ <b>הסנכרון נכשל!</b>\n\nבוט היעד @{target} אינו מוגדר כמנהל או חסר הרשאות בקבוצות הבאות:\n\n{chats}\n\nנא להוסיף את בוט היעד לקבוצות אלו ולנסות שוב.",
        'sync_error_same_bot': "❌ לא ניתן לבחור באותו בוט כמקור וכיעד כאחד.",
        'sync_error_no_groups': "❌ לבוט המקור אין קבוצות מוגדרות להעתקה.",
        'sync_error_not_owner': "❌ עליך להיות הבעלים של שני הבוטים כדי לסנכרן אותם.",
        'sync_step_check': "🔄 <b>שלב 1/3: בודק נוכחות של בוט היעד בקבוצות...</b>",
        'sync_step_groups': "🔄 <b>שלב 2/3: מעתיק קבוצות והגדרות...</b>",
        'sync_step_posts': "🔄 <b>שלב 3/3: מעתיק פוסטים ומעביר קבצים ({current}/{total})...</b>",
        
        # Help
        'help_title': "ℹ️ <b>עזרה ומידע</b>",
        'help_text': (
            "ℹ️ <b>מדריך ותסריטי פעולה של בוט הבקרה</b>\n\n"
            "בוט זה מיועד ליצירה וניהול מלא של בוטי פרסום לווייניים.\n\n"
            "📋 <b>תסריטי פעולה שלב אחר שלב:</b>\n\n"
            "1️⃣ <b>כיצד להוסיף בוט פרסום חדש:</b>\n"
            "1. היכנס ל-@BotFather, צור בוט חדש והעתק את ה-<b>Token</b> שלו. בהגדרות הבוט (Bot Settings), ודא שמאופשרת הוספה לקבוצות (<b>Allow Groups?</b> -> Enabled), והגדר ב-<b>Group Admin Rights</b> וב-<b>Channel Admin Rights</b> את כל הרשאות הניהול עבור הבוט, כולל הרשאת הוספת מנהלים חדשים (Add New Admins).\n"
            "2. בבוט הבקרה הנוכחי, לחץ על <b>רשימת בוטים</b> -> <b>➕ הוסף בוט</b>.\n"
            "3. שלח את מזהה הטלגרם (ID) של מנהל הבוט.\n"
            "4. שלח את שם המשתמש שלו (ללא הסימן @).\n"
            "5. שלח את ה-API Token של הבוט.\n"
            "6. שלח כתובת פרוקסי (http:// או socks5://) או לחץ על <b>דלג</b>.\n"
            "<i>הבוט יבדוק את החיבור ויפעיל את בוט הפרסום!</i>\n\n"
            "2️⃣ <b>כיצד לסנכרן הגדרות ותוכן בין בוטים:</b>\n"
            "1. בתפריט הראשי לחץ על <b>🔄 סנכרון בוטים</b>.\n"
            "2. בחר את <b>בוט המקור</b> (שממנו יועתקו ההגדרות והפוסטים).\n"
            "3. בחר את <b>בוט היעד</b> (שאליו יועתקו הנתונים).\n"
            "4. אשר את הסנכרון.\n"
            "<i>(כל הקבוצות שיסונכרנו לבוט היעד יהיו כבויות כברירת מחדל כדי למנוע פרסום כפול).</i>\n\n"
            "💡 <b>פקודות שימושיות:</b>\n"
            "• `/start` או `/menu` — פותח את התפריט הראשי ומאפס את מצב השיחה הנוכחי.\n"
            "• `/reset` — מאפס באופן יזום את מצב השיחה אם נתקעת בשלב כלשהו."
        ),
        
        # Language Selection
        'select_language': "🌐 <b>בחר את שפת הממשק שלך:</b>",
        'lang_changed': "🟢 השפה שונתה בהצלחה!",
        
        # Add Bot FSM
        'add_bot_start': "👤 <b>שלב 1/4:</b> שלח את מזהה הטלגרם של משתמש שיהיה מנהל בוט הפוסטים:",
        'add_bot_admin_username': "👤 <b>שלב 2/4:</b> שלח את שם המשתמש בטלגרם של מנהל בוט הפוסטים:",
        'invalid_admin_id': "❌ מזהה לא תקין! מזהה חייב להיות מספר. נסה שוב.",
        'add_bot_token': "🔑 <b>שלב 3/4:</b> שלח את טוקן ה-API של הבוט (מ-@BotFather):",
        'invalid_token': "❌ פורמט טוקן לא תקין! נסה שוב.",
        'add_bot_proxy': (
            "🌐 <b>שלב 4/4:</b> שלח את כתובת הפרוקסי.\n"
            "פורמט:\n"
            "• <code>socks5://username:password@ip:port</code>\n"
            "• <code>http://username:password@ip:port</code>\n\n"
            "לחץ על <b>דלג</b> אם אינך מעוניין בפרוקסי."
        ),
        'invalid_proxy': "❌ פורמט פרוקסי לא תקין. ודא שהוא מתחיל ב- <code>http://</code> או <code>socks5://</code> (או לחץ דלג).",
        'testing_connection': "🔄 בודק חיבור ל-Telegram API ושולח הודעת אימות...",
        'test_msg_failed': "❌ נכשל שליחת הודעת בדיקה למנהל בוט הפוסטים! ודא שהוא הפעיל את הבוט.",
        'invalid_token_error': "❌ הטוקן שסופק אינו תקין או שהפרוקסי חסם את הבקשה.",
        'bot_added_success': "🟢 <b>בוט הפוסטים נוסף והופעל בהצלחה!</b>\n🤖 בוט: @{username}",
        
        # Bot List
        'bot_list_title': "🤖 <b>רשימת בוטים מוגדרים:</b>",
        'no_bots': "🤖 <b>רשימת בוטים מוגדרים:</b>\n\n📭 אין בוטים מוגדרים עדיין.",
        'bot_card': (
            "🤖 <b>שם משתמש של הבוט:</b> @{username}\n"
            "👑 <b>בעלים:</b> @{owner}\n"
            "🔑 <b>טוקן:</b> <code>{token}</code>\n"
            "🌐 <b>פרוקסי:</b> <code>{proxy}</code>"
        ),
        'btn_update_data': "🔄 עדכן נתונים",
        'btn_delete_bot': "🗑️ מחק בוט",
        'delete_confirm': "⚠️ האם אתה בטוח שברצונך למחוק את <b>@{username}</b> מהמסד נתונים? פעולה זו תעצור את הבוט ותמחק את הגדרותיו.",
        'bot_deleted': "🗑️ הבוט נמחק בהצלחה.",
        
        # Admin Management
        'admin_list_title': "👥 <b>מנהלי המערכת:</b>",
        'btn_add_new_admin': "➕ הוסף מנהל",
        'enter_admin_id': "👤 שלח את מזהה הטלגרם של המנהל החדש:",
        'admin_added': "🟢 המנהל נוסף בהצלחה!",
        'admin_removed': "🗑️ המנהל הוסר בהצלחה.",
        'cannot_remove_self': "❌ אינך יכול להסיר את עצמך.",
        'cannot_remove_superadmin': "❌ אינך יכול להסיר את ה-Superadmin.",
        'btn_manage_bot_admins': "👥 מנהלי הבוט",
        'postbot_admin_list_title': "👥 <b>מנהלי בוט הפוסטים @{username}:</b>",
        'cannot_remove_owner': "❌ אינך יכול להסיר את הבעלים המקורי.",
        'enter_admin_username': "🏷️ שלח את שם המשתמש של המנהל החדש:",
        'admin_card_title': "👤 <b>כרטיס מנהל</b>",
        'admin_card_details': "🆔 <b>מזהה:</b> <code>{user_id}</code>\n🏷️ <b>שם משתמש:</b> @{username}\n👑 <b>תפקיד:</b> {role}",
        'btn_refresh_admin': "🔄 עדכן נתונים",
        'btn_delete_admin': "🗑️ מחק מנהל",
        'admin_refreshed': "🟢 שם המשתמש עודכן ל-@{username}!",
        'admin_refresh_failed': "❌ לא ניתן לאחזר מידע מטלגרם: {error}",
        
        # PostGroups Translations
        'btn_postgroups': "📦 קבוצות פרסום",
        'btn_create_group': "➕ צור קבוצת פרסום",
        'pg_list_title': "📋 <b>קבוצות פרסום עבור @{username}:</b>",
        'pg_no_groups': "📭 אין קבוצות פרסום מוגדרות עדיין.",
                'pg_card': (
            "📦 <b>קבוצת פרסום:</b> {name}\n"
            "🔑 <b>סיסמה:</b> <code>{passcode}</code>\n"
            "⚡ <b>סטטוס פרסום:</b> {status}\n"
            "🎁 <b>משיכת תשומת לב:</b> {promo_status}\n"
            "📝 <b>מספר פוסטים:</b> <code>{post_count}</code>\n"
            "⏱️ <b>מרווח פרסום:</b> <code>{interval}</code> שניות\n"
            "🕒 <b>שעון ישראל לפרסום:</b> <code>{time_range}</code>\n"
            "👥 <b>כמות צ'אטים מחוברים:</b> <code>{chat_count}</code>\n\n"
            "🎹 <b>מקלדת ברירת מחדל:</b>\n{kb_schema}"
        ),
        'btn_delete_group': "🗑️ מחק קבוצה",
        'btn_add_post': "➕ הוסף פוסט",
        'btn_del_all_posts': "🗑️ מחק את כל הפוסטים",
        'btn_del_any_post': "🗑️ מחק פוסט ספציפי",
        'btn_edit_settings': "⚙️ הגדרות",
        'create_group_name': "✏️ הזן שם עבור קבוצת הפרסום החדשה:",
        'create_group_layout': "📱 <b>הגדרת מקלדת ברירת מחדל:</b>\n\nמבנה המקלדת נקבע על ידי ספרות מופרדות במקף. כל ספרה מייצגת את מספר הכפתורים בשורה המתאימה.\nדוגמה: <code>1-3-1-2</code> פירושו:\n• שורה 1: כפתור 1\n• שורה 2: 3 כפתורים\n• שורה 3: כפתור 1\n• שורה 4: 2 כפתורים\n\nשלח את פריסת המקלדת (לדוגמה, <code>1-3-1-2</code>) או שלח <b><code>0</code></b> אם אין צורך במקלדת.",
        'create_group_kb_intro': "⌨️ כעת נגדיר את מקלדת ברירת המחדל לפוסטים. שלח את הטקסט של הכפתור:",
        'create_group_kb_url': "🔗 שלח את כתובת הקישור (URL) של הכפתור הזה:",
        'create_group_kb_status': "✅ הכפתור נוסף. באפשרותך להוסיף כפתור נוסף או לסיים את הגדרת המקלדת:",
        'btn_add_more_buttons': "➕ הוסף כפתור",
        'btn_finish_kb': "🟢 סיים הגדרת מקלדת",
        'create_group_passcode': "🔑 בחר סיסמה ייחודית לחיבור קבוצות/ערוצים לקבוצת פרסום זו:",
        'create_group_interval': "⏱️ הזן מרווח זמן לפרסום בשניות (מינימום 60 שניות).\n\n💡 הזמן מצוין בשניות. לדוגמה:\n• 30 דקות = 1800 שניות\n• שעה 1 = 3600 שניות",
        'create_group_timerange': "🕒 הזן טווח שעות לפרסום לפי שעון ישראל (HH:MM-HH:MM, לדוגמה 08:00-22:00):",
        'invalid_interval': "❌ מרווח זמן לא תקין! חייב להיות מספר שלם גדול או שווה ל-60.",
        'invalid_time_range': "❌ פורמט זמן לא תקין! אנא השתמש בפורמט HH:MM-HH:MM.",
        'duplicate_passcode': "❌ סיסמה זו כבר תפוסה. אנא בחר סיסמה אחרת.",
        'create_group_confirm': (
            "📋 <b>אשר את פרטי קבוצת הפרסום:</b>\n\n"
            "📦 <b>שם:</b> {name}\n"
            "📱 <b>כפתורים בשורה:</b> {layout}\n"
            "🔑 <b>סיסמה:</b> <code>{passcode}</code>\n"
            "⏱️ <b>מרווח פרסום:</b> {interval} שניות\n"
            "🕒 <b>טווח שעות (ישראל):</b> {time_range}\n"
            "🎹 <b>כפתורי המקלדת:</b> {buttons}"
        ),
        'group_added_success': "🟢 קבוצת הפרסום נוצרה בהצלחה!",
        'confirm_delete_group': "⚠️ האם אתה בטוח שברצונך למחוק את קבוצת הפרסום <b>{name}</b>? זה ימחק את כל הפוסטים וינתק את הצ'אטים המחוברים.",
        'group_deleted': "🗑️ קבוצת הפרסום נמחקה בהצלחה.",
        
        # Post Creation inside PostGroup
        'add_post_start': "📝 שלח את תוכן הפוסט (תמונה, סרטון, אנימציה/גיף, או טקסט):",
        'add_post_confirm': "❓ האם ברצונך לשמור ולהוסיף את הפוסט הזה לקבוצה?",
        'post_added_to_group': "🟢 הפוסט נוסף בהצלחה לקבוצה!",
        
        # PostGroup settings editing
        'edit_settings_menu': "⚙️ <b>עריכת הגדרות קבוצת הפרסום:</b>",
        'btn_edit_interval': "⏱️ ערוך מרווח זמן",
        'btn_edit_timerange': "🕒 ערוך טווח שעות",
        'btn_edit_kb': "⌨️ ערוך מקלדת",
        'enter_interval': "⏱️ הזן מרווח זמן לפרסום בשניות (מינימום 60 שניות).\n\n💡 הזמן מצוין בשניות. לדוגמה:\n• 30 דקות = 1800 שניות\n• שעה 1 = 3600 שניות",
        'interval_updated': "🟢 מרווח הזמן לפרסום עודכן בהצלחה!",
        'enter_timerange': "🕒 הזן טווח שעות לפרסום לפי שעון ישראל (HH:MM-HH:MM):",
        'timerange_updated': "🟢 טווח השעות לפרסום עודכן בהצלחה!",
        
        # Postbot Help
        'pb_help_text': (
            "ℹ️ <b>מדריך ותסריטי פעולה של בוט הפרסום</b>\n\n"
            "בוט זה מבצע פרסום אוטומטי של תוכן בערוצים ובקבוצות הטלגרם שלך.\n\n"
            "📋 <b>תסריטי פעולה שלב אחר שלב:</b>\n\n"
            "1️⃣ <b>כיצד להגדיר פרסום לערוץ/קבוצה:</b>\n"
            "1. לחץ על <b>📦 קבוצות פוסטים</b> -> <b>➕ צור קבוצה</b>.\n"
            "2. הזן שם, פריסת כפתורים (או 0) וסיסמה ייחודית (למשל, <code>mycode123</code>).\n"
            "3. הגדר את מרווח הפרסום (בשניות) ואת חלון הזמנים (למשל, <code>09:00-22:00</code>). אשר את היצירה.\n"
            "4. הוסף את הבוט הנוכחי כ-<b>מנהל</b> (Administrator) בערוץ/קבוצה שלך (עם הרשאות לפרסום ומחיקת הודעות).\n"
            "5. שלח את הסיסמה שלך (למשל, <code>mycode123</code>) כהודעה ישירות בתוך הערוץ/קבוצה.\n"
            "<i>הבוט ימחק את הודעת הסיסמה ויקשר את הצ'אט בהצלחה!</i>\n\n"
            "2️⃣ <b>כיצד להוסיף פוסט חדש לתור:</b>\n"
            "1. לחץ על <b>📦 קבוצות פוסטים</b> -> בחר את הקבוצה שלך -> <b>➕ הוסף פוסט</b>.\n"
            "2. שלח את התוכן (טקסט, תמונה, סרטון או GIF).\n"
            "3. צרף כפתורים מותאמים אישית במידת הצורך ולחץ על <b>אישור</b>.\n"
            "<i>הפוסט יתווסף לתור ויפורסם בהתאם למרווח הזמנים שהוגדר.</i>\n\n"
            "3️⃣ <b>כיצד להגדיר מבצעי תגובות (Attention Grabber):</b>\n"
            "1. בחר בקבוצה שלך -> <b>🛠️ הגדרות</b> -> <b>📢 הגדרות קופונים</b> -> <b>⚙️ הגדרת מבצע</b>.\n"
            "2. בצע את השלבים: הגדר טווח הנחה, אימוג'י להפעלה, משך זמן וטקסטים.\n"
            "3. לחץ על <b>הפעל</b> כדי להתחיל לעקוב אחר תגובות.\n"
            "<i>הבוט יפרסם קודי קופון באופן אוטומטי כאשר יעד התגובות יושג!</i>\n\n"
            "💡 <b>פקודות שימושיות:</b>\n"
            "• `/start` או `/menu` — פותח את התפריט הראשי ומאפס את מצב השיחה הנוכחי.\n"
            "• `/reset` — מאפס באופן יזום את מצב השיחה אם נתקעת בשלב כלשהו."
        ),
        
        # Toggle Posting
        'btn_toggle_posting_on': "🟢 הפעל פרסום",
        'btn_toggle_posting_off': "🔴 השבת פרסום",
        'btn_promo_enable': "🟢 הפעל",
        'btn_promo_disable': "🔴 כבה",
        'posting_status': "⚡ <b>סטטוס פרסום:</b> {status}",
        'status_enabled': "🟢 פעיל",
        'status_disabled': "🔴 מושבת",
        'chat_removed_alert': "⚠️ <b>אבדת הגישה לצ'אט!</b>\n\nהחיבור לערוץ/קבוצה <b>{title}</b> (ID: <code>{chat_id}</code>) בקבוצת הפרסום <b>{group_name}</b> הוסר מכיוון שהבוט נחסם או שהצ'אט אינו קיים יותר.",
        
        # Chats Tab
        'btn_chats': "👥 צ'אטים",
        'btn_transfer': "🔄 העבר",
        'btn_unlink': "🗑️ נתק",
        'btn_refresh_chats': "🔄 עדכן מידע",
        'chats_list_title': "👥 <b>צ'אטים מחוברים עבור {group_name}:</b>",
        'chat_details_title': (
            "👥 <b>פרטי צ'אט:</b>\n\n"
            "📝 <b>שם:</b> {title}\n"
            "🏷️ <b>שם משתמש:</b> {username}\n"
            "🆔 <b>מזהה ID:</b> <code>{chat_id}</code>\n"
            "👥 <b>רשומים/חברים:</b> <code>{member_count}</code>"
        ),
        'chat_transferred': "🟢 הצ'אט הועבר בהצלחה לקבוצה {group_name}!",
        'chat_unlinked': "🗑️ הצ'אט נותק בהצלחה.",
        'select_transfer_group': "🔄 <b>בחר קבוצת יעד להעברת הצ'אט:</b>",
                'no_other_groups': "❌ אין קבוצות פרסום אחרות להעברה.",
        'btn_settings': "⚙️ הגדרות",
        'settings_menu_title': "⚙️ <b>הגדרות בוט הפוסטים</b>\n\n📋 <b>סטטוס קבוצות:</b>\n{group_list}",
        'btn_stop_all_groups': "🔴 השבת את כל הקבוצות",
        'btn_start_all_groups': "🟢 הפעל את כל הקבוצות",
        'all_groups_stopped': "🔴 כל קבוצות הפרסום הושבתו בהצלחה.",
        'all_groups_started': "🟢 כל קבוצות הפרסום הופעלו בהצלחה.",
        'create_group_kb_btn_text_prompt': "⌨️ <b>שורה {row}, כפתור {col}:</b>\nשלח את הטקסט עבור כפתור זה:",
        'create_group_kb_btn_url_prompt': "🔗 <b>שורה {row}, כפתור {col}:</b>\nשלח את הקישור (URL) עבור כפתור זה:",
        'invalid_layout_schema': "❌ פורמט פריסת מקלדת לא תקין! יש להשתמש בספרות מופרדות במקפים (לדוגמה, 1-3-1-2) או להזין 0.",
        'btn_edit_kb_success': "🟢 מקלדת ברירת המחדל עודכנה בהצלחה!",
        'no_keyboard_configured': "אין מקלדת",
        'btn_promo_settings': "🎁 משיכת תשומת לב",
        'promo_settings_title': "🎁 <b>הגדרות משיכת תשומת לב (פרומו)</b>\n\n⚡ <b>סטטוס:</b> {status}\n🎯 <b>תגובת טריגר:</b> {trigger_emoji}\n💰 <b>טווח הנחה:</b> <code>{discount_range}%</code>\n⏱️ <b>זמן קוד:</b> <code>{duration_hours} שעות</code>\n⏳ <b>תוקף הצעה בפוסט:</b> <code>{post_duration_hours} שעות</code>\n📊 <b>תדירות:</b> <code>כל {post_frequency} פוסטים</code>\n📝 <b>טקסט הנחיה:</b> <i>{text_instruction}</i>\n🎉 <b>טקסט הצלחה:</b> <i>{text_success}</i>\n⏳ <b>טקסט תוקף:</b> <i>{text_duration}</i>",
        'btn_setup_promo': "⚙️ הגדר את כל השדות",
        'promo_discount_range_prompt': "💰 <b>שלב 1/8:</b> הזן את טווח אחוז ההנחה (לדוגמה, <code>5-10</code>):",
        'promo_trigger_emoji_prompt': "🎯 <b>שלב 2/8:</b> בחר את אימוג'י התגובה שיפעיל את ההנחה:",
        'promo_post_duration_hours_prompt': "⏱️ <b>שלב 3/8:</b> הזן את משך תוקף ההצעה בפוסט בשעות (לדוגמה, <code>12</code>):",
        'promo_post_frequency_prompt': "📊 <b>שלב 4/8:</b> הזן תדירות פוסטים (צרף פרומו פעם ב-N פוסטים, לדוגמה, <code>10</code>):",
        'promo_text_instruction_prompt': "📝 <b>שלב 5/8:</b> הזן את טקסט ההנחיה.\nדוגמה:\n<code>לחץ על {emoji} וקבל הנחה של {discount_range}%. ההצעה תקפה ל-{post_duration} שעות.</code>",
        'promo_text_success_prompt': "🎉 <b>שלב 6/8:</b> הזן את טקסט ההצלחה.\nדוגמה:\n<code>קיבלת הנחה. כל הכבוד!</code>",
        'promo_duration_hours_prompt': "⏱️ <b>שלב 7/8:</b> הזן את משך תוקף קוד הפרומו בשעות (לדוגמה, <code>3</code>):",
        'promo_text_duration_prompt': "⏳ <b>שלב 8/8:</b> הזן את הודעת משך התוקף.\nדוגמה:\n<code>ההנחה תקפה ל-3 שעות! הזמן עכשיו</code>",
        'invalid_discount_range': "❌ פורמט טווח לא תקין! הזן שני מספרים מופרדים במקף (לדוגמה, 5-10).",
        'invalid_duration_hours': "❌ משך תוקף לא תקין! חייב להיות מספר שלם וחיובי של שעות.",
        'setup_promo_first_alert': "⚠️ עליך להגדיר תחילה את משיכת תשומת הלב!" 
    }
}

def t(key, lang='en', **kwargs):
    text = LOCALES.get(lang, LOCALES['en']).get(key, LOCALES['en'].get(key, f"[{key}]"))
    return text.format(**kwargs)
