import importlib
import re
import time
from platform import python_version as y
from sys import argv 
from typing import Optional

from pyrogram import __version__ as pyrover   
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever  
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import ( 
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown 
from telethon import __version__ as tlhver
from MukeshRobot import pbot as app
import MukeshRobot.modules.no_sql.users_db as sql
from MukeshRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from MukeshRobot.modules import ALL_MODULES
from MukeshRobot.modules.helper_funcs.chat_status import is_user_admin
from MukeshRobot.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["detik", "menit", "jam", "hari"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time
PM_START_TEX = """
ʜᴇʟʟᴏ {} !! ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ ʏᴀʜ sᴇᴅᴀɴɢ ᴍᴇᴍᴜᴀᴛ ᴍᴏᴅᴜʟᴇ ...
"""

PM_START_TEXT = """
*❏──────────────────────❏*
*├ ʜᴇʏ* {} 👋 
*├ ɪ'ᴍ sʏɴᴄ ꭙ͢ ꝛσʙσᴛ*
*├ ᴜᴩᴛɪᴍᴇ* `{}`
*├ ᴜsᴇʀs* `{}`
*├ ᴄʜᴀᴛs* `{}`
*❏──────────────────────❏*
*├ ᴘᴏᴡᴇʀꜰᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇ*
*├ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ꜰᴇᴀᴛᴜʀᴇs* 
*├ ᴄʟɪᴄᴋ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ* 
*├ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ*
*├ ᴄᴏᴍᴍᴀɴᴅs*
*❏──────────────────────❏*
"""


buttons = [
    [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴍᴇ",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    
        InlineKeyboardButton(text="ʜᴇʟᴘ", callback_data="Main_help"),
    
    ],
]

HELP_STRINGS = f"""
❏ *ᴄʜᴏᴏsᴇ ᴏɴᴇ ᴏꜰ ᴛʜᴇ ᴄᴀᴛᴇɢᴏʀɪᴇs ʙᴇʟᴏᴡ
├ ᴛᴏ sᴇᴇ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs
╰ ᴜsᴇᴀʙʟᴇ ʜᴀɴᴅʟᴇʀ* : / , !."""



IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MukeshRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMG,
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name       
            x=update.effective_message.reply_sticker(
                "CAACAgQAAx0CfHUiYgACK3Vli69lU3OpIt9dBlGBcrUM3HBvhQAC3BEAApVqGFH_E0OKjWulgzME") 
            time.sleep(0.8)
            x.delete()
            usr = update.effective_user
            lol = update.effective_message.reply_text(
                PM_START_TEX.format(usr.first_name), parse_mode=ParseMode.MARKDOWN
            )
            time.sleep(0.8)
            lol.edit_text("😂") 
            time.sleep(0.8)
            lol.edit_text("🫵") 
            time.sleep(0.8) 
            lol.edit_text("🤣") 
            time.sleep(0.8) 
            lol.edit_text("🦶") 
            time.sleep(0.8) 
            lol.edit_text("sʏɴᴄ ꜱᴛᴀʀᴛɪɴɢ... ")
            time.sleep(0.4)
            lol.delete() 
            uptime = get_readable_time((time.time() - StartTime)) 
            update.effective_message.reply_photo(            
                photo=START_IMG,
                caption=PM_START_TEXT.format(escape_markdown(first_name), escape_markdown(uptime), sql.num_users(), sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ !\n<b>ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors

def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "» *ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ​​* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_caption(text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def Harlay_ngontol_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "harlay_":      
        query.message.edit_caption(f"*❏ ᴍᴜsɪᴄ ʜᴇʟᴘ ᴍᴇɴᴜ*"
            "\n*├ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ꜰᴏʀ ᴍᴏʀᴇ*"
            "\n*├ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ. ɪꜰ ʏᴏᴜ ꜰᴀᴄᴇ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ*"
            "\n*├ ɪɴ ᴄᴏᴍᴍᴀɴᴅ ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ʙᴏᴛ*"
            "\n*├ ᴏᴡɴᴇʀ ᴏʀ ᴀsᴋ ɪɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ*"
            "\n*╰ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /*",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴀᴅᴍɪɴ", callback_data="jurig_"
                        ),
                        InlineKeyboardButton(
                            text="ᴀᴜᴛʜ", callback_data="minum_"
                        ),
                    
                        InlineKeyboardButton(
                            text="ʙʟᴀᴄᴋʟɪsᴛ", callback_data="makan_"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="gagah_"
                        ),
                        InlineKeyboardButton(
                            text="ɢʙᴀɴ", callback_data="babi_"
                        ),
                        InlineKeyboardButton(
                            text="ʟʏʀɪᴄs", callback_data="manuk_"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ᴘɪɴɢ", callback_data="kecoa_"
                        ),
                        InlineKeyboardButton(
                            text="ᴘʟᴀʏ", callback_data="tapai_"
                        ),
                        InlineKeyboardButton(
                            text="ᴘʟᴀʏʟɪsᴛ", callback_data="kacang_"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ᴠɪᴅᴇᴏᴄʜᴀᴛs", callback_data="rangu_"
                        ),
                        InlineKeyboardButton(
                            text="sᴛᴀʀᴛ", callback_data="berak_"
                        ),
                        InlineKeyboardButton(
                            text="sᴜᴅᴏ", callback_data="mati_"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="Main_help"), 
                    ],
                ]
            ),
        )        
        
def Pasti_sabi_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "mati_":      
        query.message.edit_caption(f"*🥀 sᴜᴅᴏᴇʀs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅs :*"
            "\n\n🥺 ᴀᴅᴅ & ʀᴇᴍᴏᴠᴇ sᴜᴅᴏᴇʀs :"
            "\n\n/addsudo [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ]"
            "\n/delsudo [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴄʜᴜᴛɪʏᴀ.]"
            "\n\n🥶 ʜᴇʀᴏᴋᴜ :"
            "\n\n/usage : sʜᴏᴡs ᴛʜᴇ ᴅʏɴᴏ ᴜsᴀɢᴇ ᴏғ ᴛʜᴇ ᴍᴏɴᴛʜ."
            "\n\n🤯 ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs:"
            "\n\n/get_var : ɢᴇᴛ ᴀ ᴄᴏɴғɪɢ ᴠᴀʀ ғʀᴏᴍ ʜᴇʀᴏᴋᴜ ᴏʀ .ᴇɴᴠ."
            "\n/del_var : ᴅᴇʟᴇᴛᴇ ᴀ ᴄᴏɴғɪɢ ᴠᴀʀ ᴏɴ ʜᴇʀᴏᴋᴜ ᴏʀ .ᴇɴᴠ."
            "\n/set_var [ᴠᴀʀ ɴᴀᴍᴇ] [ᴠᴀʟᴜᴇ] : sᴇᴛ ᴏʀ ᴜᴩᴅᴀᴛᴇ ᴀ ᴄᴏɴғɪɢ ᴠᴀʀ ᴏɴ ʜᴇʀᴏᴋᴜ ᴏʀ .ᴇɴᴠ."
            "\n\n🤓 ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs:"
            "\n\n/restart : ʀᴇsᴛᴀʀᴛs ʏᴏᴜʀ ʙᴏᴛ."
            "\n\n/update : ᴜᴩᴅᴀᴛᴇs ᴛʜᴇ ʙᴏᴛ ғʀᴏᴍ ᴛʜᴇ ᴜᴩsᴛʀᴇᴀᴍ ʀᴇᴩᴏ."
            "\n\n/speedtest : ᴄʜᴇᴄᴋ ʙᴏᴛ's sᴇʀᴠᴇʀ sᴩᴇᴇᴅ."
            "\n\n/maintenance [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴏғ ʏᴏᴜʀ ʙᴏᴛ."
            "\n\n/logger [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ʙᴏᴛ ᴡɪʟʟ sᴛᴀʀᴛ ʟᴏɢɢɪɴɢ ᴛʜᴇ ᴀᴄᴛɪᴠɪᴛɪᴇs ʜᴀᴩᴩᴇɴ ᴏɴ ʙᴏᴛ."
            "\n\n/get_log [ɴᴜᴍʙᴇʀ ᴏғ ʟɪɴᴇs] : ɢᴇᴛ ʟᴏɢs ᴏғ ʏᴏᴜʀ ʙᴏᴛ [ᴅᴇғᴀᴜʟᴛ ᴠᴀʟᴜᴇ ɪs 100 ʟɪɴᴇs]"
            "\n\n💔 ғᴏʀ ᴩʀɪᴠᴀᴛᴇ ʙᴏᴛ ᴏɴʟʏ :"
            "\n\n/authorize [ᴄʜᴀᴛ ɪᴅ] : ᴀʟʟᴏᴡs ᴀ ᴄʜᴀᴛ ғᴏʀ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ."
            "\n/unauthorize [ᴄʜᴀᴛ ɪᴅ] : ᴅɪsᴀʟʟᴏᴡs ᴛʜᴇ ᴀʟʟᴏᴡᴇᴅ ᴄʜᴀᴛ."
            "\n/authorized : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ᴀʟʟᴏᴡᴇᴅ ᴄʜᴀᴛs.",
            parse_mode=ParseMode.MARKDOWN,           
            reply_markup=InlineKeyboardMarkup( 
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"), 
                    ],
                ]
            ),
        )
        
def Bacot_lo_callback(update: Update, context: CallbackContext):
    query = update.callback_query  
    if query.data == "berak_":  
        query.message.edit_caption(f"*😅ɢᴇᴛ sᴛᴀʀᴛᴇᴅ ᴡɪᴛʜ ʙᴏᴛ.*"
            "\n\n/start : sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ."
            "\n\n/help : ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ ᴏғ ᴄᴏᴍᴍᴀɴᴅs."
            "\n\n/reboot : ʀᴇʙᴏᴏᴛs ᴛʜᴇ ʙᴏᴛ ғᴏʀ ʏᴏᴜʀ ᴄʜᴀᴛ."
            "\n\n/settings : sʜᴏᴡs ᴛʜᴇ ɢʀᴏᴜᴩ sᴇᴛᴛɪɴɢs ᴡɪᴛʜ ᴀɴ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ɪɴʟɪɴᴇ ᴍᴇɴᴜ."
            "\n\n/sudolist : sʜᴏᴡs ᴛʜᴇ sᴜᴅᴏ ᴜsᴇʀs ᴏғ ᴍᴜsɪᴄ ʙᴏᴛ.",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup( 
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"), 
                    ]
                ]
            ),
        )
def Monyet_to_callback(update: Update, context: CallbackContext):
    query = update.callback_query        
    if query.data == "rangu_": 
        query.message.edit_caption(f"*🤑 ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛs :*"
            "\n\n/activevoice : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇᴄʜᴀᴛs ᴏɴ ᴛʜᴇ ʙᴏᴛ."
            "\n/activevideo : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ."
            "\n/autoend [ᴇɴᴀʙʟᴇ|ᴅɪsᴀʙʟᴇ] : ᴇɴᴀʙʟᴇ sᴛʀᴇᴀᴍ ᴀᴜᴛᴏ ᴇɴᴅ ɪғ ɴᴏ ᴏɴᴇ ɪs ʟɪsᴛᴇɴɪɴɢ.",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup( 
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        )
def Viral_ya_callback(update: Update, context: CallbackContext):
    query = update.callback_query      
    if query.data == "kacang_":
        query.message.edit_caption(f"*🤨 sᴇʀᴠᴇʀ ᴩʟᴀʏʟɪsᴛs :*"
            "\n\n/playlist : ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴩʟᴀʏʟɪsᴛ ᴏɴ sᴇʀᴠᴇʀs."
            "\n\n/deleteplaylist : ᴅᴇʟᴇᴛᴇ ᴀɴʏ sᴀᴠᴇᴅ ᴛʀᴀᴄᴋ ɪɴ ʏᴏᴜʀ ᴩʟᴀʏʟɪsᴛ."
            "\n\n/play : sᴛᴀʀᴛs ᴩʟᴀʏɪɴɢ ғʀᴏᴍ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴩʟᴀʏʟɪsᴛ ᴏɴ sᴇʀᴠᴇʀ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup( 
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        )
        
def Aku_suka_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "tapai_":
        query.message.edit_caption(f"*💞 ᴩʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs:.*"
            "\n\nc sᴛᴀɴᴅs ғᴏʀ ᴄʜᴀɴɴᴇʟ ᴩʟᴀʏ."
            "\nv sᴛᴀɴᴅs ғᴏʀ ᴠɪᴅᴇᴏ ᴩʟᴀʏ."
            "\nforce sᴛᴀɴᴅs ғᴏʀ ғᴏʀᴄᴇ ᴩʟᴀʏ."
            "\n\n/play ᴏʀ /vplay ᴏʀ /cplay : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
            "\n\n/playforce ᴏʀ /vplayforce ᴏʀ /cplayforce : ғᴏʀᴄᴇ ᴩʟᴀʏ sᴛᴏᴩs ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ."
            "\n\n/channelplay [ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ] ᴏʀ [ᴅɪsᴀʙʟᴇ] : ᴄᴏɴɴᴇᴄᴛ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀ ɢʀᴏᴜᴩ ᴀɴᴅ sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʀᴀᴄᴋs ʙʏ ᴛʜᴇ ʜᴇʟᴩ ᴏғ ᴄᴏᴍᴍᴀɴᴅs sᴇɴᴛ ɪɴ ɢʀᴏᴜᴩ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        ) 
        
def Siap_bos_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "kecoa_":
        query.message.edit_caption(f"*🍑 ᴩɪɴɢ ᴄᴏᴍᴍᴀɴᴅ :.*"
            "\n\n/ping : sʜᴏᴡ ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ."
            "\n\n/stats : ɢᴇᴛ ᴛᴏᴩ 10 ᴛʀᴀᴄᴋ ɢʟᴏʙᴀʟ sᴛᴀᴛs, ᴛᴏᴩ 10 ᴜsᴇʀs ᴏғ ᴛʜᴇ ʙᴏᴛ, ᴛᴏᴩ 10 ᴄʜᴀᴛs ᴏɴ ᴛʜᴇ ʙᴏᴛ, ᴛᴏᴩ 10 ᴩʟᴀʏᴇᴅ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ᴍᴀɴʏ ᴍᴏʀᴇ..",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup( 
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        )
def Gak_peduli_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "manuk_":
        query.message.edit_caption(f"*😉 ᴇxᴛʀᴀs :.*"
            "\n\n/loop [ᴅɪsᴀʙʟᴇ/ᴇɴᴀʙʟᴇ] ᴏʀ [ʙᴇᴛᴡᴇᴇɴ 1:10]"
            "\n: ᴡʜᴇɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ʙᴏᴛ ᴡɪʟʟ ᴩʟᴀʏ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ɪɴ ʟᴏᴏᴩ ғᴏʀ 10 ᴛɪᴍᴇs ᴏʀ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ʀᴇǫᴜᴇsᴛᴇᴅ ʟᴏᴏᴩs."
            "\n\n/shuffle : sʜᴜғғʟᴇ ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs."
            "\n\n/seek : sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ."
            "\n\n/seekback : ʙᴀᴄᴋᴡᴀʀᴅ sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ."
            "\n\n/lyrics [sᴏɴɢ ɴᴀᴍᴇ] : sᴇᴀʀᴄʜ ʟʏʀɪᴄs ғᴏʀ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ sᴏɴɢ ᴀɴᴅ sᴇɴᴅ ᴛʜᴇ ʀᴇsᴜʟᴛs.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        ) 
        
def Muhun_nuhun_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "babi_":
        query.message.edit_caption(f"*🤬 ɢʙᴀɴ ғᴇᴀᴛᴜʀᴇ [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :.*" 
            "\n\n/gban [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴄʜᴜᴛɪʏᴀ] : ɢʟᴏʙᴀʟʟʏ ʙᴀɴs ᴛʜᴇ ᴄʜᴜᴛɪʏᴀ ғʀᴏᴍ ᴀʟʟ ᴛʜᴇ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴀɴᴅ ʙʟᴀᴄᴋʟɪsᴛ ʜɪᴍ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ."
            "\n\n/ungban [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] : ɢʟᴏʙᴀʟʟʏ ᴜɴʙᴀɴs ᴛʜᴇ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ᴜsᴇʀ."
            "\n\n/gbannedusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇʀ ᴜsᴇʀs.",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        )
        
def Tidak_habis_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "gagah_":   
        query.message.edit_caption(f"*🍒 ʙʀᴏᴀᴅᴄᴀsᴛ ғᴇᴀᴛᴜʀᴇ [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :.*"
            "\n\n/broadcast [ᴍᴇssᴀɢᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ] : ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ."
            "\n\nʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴍᴏᴅᴇs:"
            "\n-pin : ᴩɪɴs ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇs ɪɴ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs."
            "\n-pinloud : ᴩɪɴs ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴀɴᴅ sᴇɴᴅ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴛᴏ ᴛʜᴇ ᴍᴇᴍʙᴇʀs."
            "\n-user : ʙʀᴏᴀᴅᴄᴀsᴛs ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴛʜᴇ ᴜsᴇʀs ᴡʜᴏ ʜᴀᴠᴇ sᴛᴀʀᴛᴇᴅ ʏᴏᴜʀ ʙᴏᴛ."
            "\n-assistant : ʙʀᴏᴀᴅᴄᴀsᴛ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ᴀssɪᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ ᴏғ ᴛʜᴇ ʙᴏᴛ."
            "\n-nobot : ғᴏʀᴄᴇs ᴛʜᴇ ʙᴏᴛ ᴛᴏ ɴᴏᴛ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛʜᴇ ᴍᴇssᴀɢᴇ."
            "\n\n**ᴇxᴀᴍᴩʟᴇ:** `/broadcast -user -assistant -pin ᴛᴇsᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ`.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        )

def Diluar_nurul_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "makan_":        
        query.message.edit_caption(f"*😒 ʙʟᴀᴄᴋʟɪsᴛ ᴄʜᴀᴛ :*"
            "\nʙʟᴀᴄᴋʟɪsᴛ ғᴇᴀᴛᴜʀᴇ [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs]."
            "\n\n/blacklistchat [ᴄʜᴀᴛ ɪᴅ] : ʙʟᴀᴄᴋʟɪsᴛ ᴀ ᴄʜᴀᴛ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ."
            "\n\n/whitelistchat [ᴄʜᴀᴛ ɪᴅ] : ᴡʜɪᴛᴇʟɪsᴛ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴄʜᴀᴛ."
            "\n\n/blacklistedchat : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴄʜᴀᴛs."
            "\n\n\n😤 ʙʟᴏᴄᴋ ᴜsᴇʀs:."
            "\n\n/block [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴄʜᴜᴛɪʏᴀ] : sᴛᴀʀᴛs ɪɢɴᴏʀɪɴɢ ᴛʜᴇ ᴄʜᴜᴛɪʏᴀ, sᴏ ᴛʜᴀᴛ ʜᴇ ᴄᴀɴ'ᴛ ᴜsᴇ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs."
            "\n\n/unblock [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] : ᴜɴʙʟᴏᴄᴋs ᴛʜᴇ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀ."
            "\n\n/blockedusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs.",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup( 
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"),
                    ],
                ]
            ),
        )
        
def Enoh_ken_callback(update: Update, context: CallbackContext):
    query = update.callback_query                     
    if query.data == "minum_":       
        query.message.edit_caption(f"*😜 ᴀᴜᴛʜ ᴜsᴇʀs :*"
            "\nᴀᴜᴛʜ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴛʜᴇ ʙᴏᴛ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ. [ᴀᴅᴍɪɴs ᴏɴʟʏ]."
            "\n\n/auth [ᴜsᴇʀɴᴀᴍᴇ] : ᴀᴅᴅ ᴀ ᴜsᴇʀ ᴛᴏ ᴀᴜᴛʜ ʟɪsᴛ ᴏғ ᴛʜᴇ ʙᴏᴛ."
            "\n\n/unauth [ᴜsᴇʀɴᴀᴍᴇ] : ʀᴇᴍᴏᴠᴇ ᴀ ᴀᴜᴛʜ ᴜsᴇʀs ғʀᴏᴍ ᴛʜᴇ ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ."
            "\n\n/authusers : sʜᴏᴡs ᴛʜᴇ ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴩ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"), 
                    ],
                ]
            ),
        )
        
def Jurig_atah_callback(update: Update, context: CallbackContext):
    query = update.callback_query        
    if query.data == "jurig_":       
        query.message.edit_caption(f"*🙄 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:*"
            "\n\n*nᴊᴜsᴛ ᴀᴅᴅ ᴄ ɪɴ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴜsᴇ ᴛʜᴇᴍ ғᴏʀ ᴄʜᴀɴɴᴇʟ.*"
            "\n\n/pause : ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."
            "\n\n/resume : ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ."
            "\n\n/skip : sᴋɪᴩ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ."
            "\n\n/end ᴏʀ /stop : ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."
            "\n\n/player : ɢᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩʟᴀʏᴇʀ ᴩᴀɴᴇʟ."
            "\n\n/queue : sʜᴏᴡs ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ʟɪsᴛ.",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup(
                [ 
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="harlay_"), 
                    ],
                ]
            ),
        ) 
        
def Waduh_pusing_callback(update: Update, context: CallbackContext):
    query = update.callback_query        
    if query.data == "waduh_":       
        query.message.edit_caption(f"* ᴘᴇʀʜᴀᴛɪᴀɴ!*"
            "\n\n*ʙᴜᴀᴛ ᴋᴀʟɪᴀɴ ʏᴀɴɢ ʟᴀɢɪ ɴʏᴀʀɪ ʀᴇᴘᴏꜱɪᴛᴏʀʏ ʙᴏᴛ ᴍᴀɴᴀɢᴇ ʙᴇꜱᴇʀᴛᴀ ʀᴇᴘᴏꜱɪᴛᴏʀʏ ᴍᴜꜱɪᴄ ꜱᴇᴘᴇʀᴛɪ ʙᴏᴛ ⬇️*"
            "\n\n[sʏɴᴄ ᴘʀᴏᴊᴇᴄᴛ](https://t.me/LitleePrince)" 
            "\n\n*sᴀʏᴀ ᴍᴇɴᴊᴜᴀʟ ʀᴇᴘᴏ ᴘʀɪᴠᴀᴛᴇ sʏɴᴄ ꭙ͢ ꝛσʙσᴛ*" 
            "\n\n*sɪʟᴀʜᴋᴀɴ ʜᴜʙᴜɴɢɪ ᴏᴡɴᴇʀ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ☎️*",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup(
                [ 
                    [
                        InlineKeyboardButton(text="ᴏᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}"),
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="Main_help"), 
                    ],
                ]
            ),
        ) 

def MukeshRobot_Main_Callback(update: Update, context: CallbackContext):  
    query = update.callback_query 
    if query.data == "Main_help": 
        uptime = get_readable_time((time.time() - StartTime)) 
        query.message.edit_caption(f"*❏ sʏɴᴄ ꭙ͢ ꝛσʙσᴛ ʜᴇʟᴘ ᴍᴇɴᴜ*"
            "\n*├ sᴇʟᴇᴄᴛ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ*"
            "\n*├ ʜᴇʟᴘ ᴍᴀɴᴀɢᴇ ᴀɴᴅ ᴍᴜsɪᴄ ᴄᴏᴍᴍᴀɴᴅs*"
            "\n*╰ /bug : ᴛᴏ ʀᴇᴘᴏʀᴛ ᴀɴ ᴇʀʀᴏʀ ᴘʀᴏʙʟᴇᴍ*",
            parse_mode=ParseMode.MARKDOWN, 
            reply_markup=InlineKeyboardMarkup( 
                [ 
                    [ 
                        InlineKeyboardButton( 
                            text="ᴍᴀɴᴀɢᴇ", callback_data="help_back"
                        ),
                        InlineKeyboardButton(
                            text="ᴍᴜsɪᴋ", callback_data="harlay_"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ᴅᴏɴᴀᴛᴇ", callback_data="fallen_"
                        ), 
                        InlineKeyboardButton(
                            text="sᴇssɪᴏɴ", callback_data="generate"
                        ),
                    ], 
                    [
                        InlineKeyboardButton(text="ᴊᴀsᴀ ʙᴏᴛ", callback_data="source_"),
                    
                    
                        
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="fallen_back")
                    ],
                ]
            ),
        )
                                            
                      
def Fallen_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "fallen_":
        query.message.edit_caption(f"*ʜᴇʏ,*👋"
            "\n*ᴛʜɪs ɪs sʏɴᴄ ꭙ͢ ꝛσʙσᴛ*"
            "\n\n*❏ ɪꜰ ʏᴏᴜ ʟɪᴋᴇ sʏɴᴄ ꭙ͢ ꝛσʙσᴛ ᴀɴᴅ ᴡᴀɴᴛ ᴛᴏ*"
            "\n*╰ ᴅᴏɴᴀᴛᴇ ᴛᴏ ᴋᴇᴇᴘ sʏɴᴄ ꭙ͢ ꝛσʙσᴛ ᴀᴄᴛɪᴠᴇ*"
            "\n\n*❏ ʏᴏᴜ ᴄᴀɴ ᴅᴏɴᴀᴛᴇ ᴠɪᴀ ᴅᴀɴᴀ : ᴄᴏᴏᴍɪɴɢ sᴏᴏɴ*"
            "\n*╰ ᴏʀ ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴏᴡɴᴇʀ ʙᴇʟᴏᴡ*"
            "\n\n*❏ ᴀɴᴅ ꜰᴏʀ ᴛʜᴏsᴇ ᴡʜᴏ ʜᴀᴠᴇ ᴅᴏɴᴀᴛᴇᴅ, ɪ*"
            "\n*╰ ᴛʜᴀɴᴋ ʏᴏᴜ ᴠᴇʀʏ ᴍᴜᴄʜ 🙏*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ᴅᴏɴᴀsɪ", url="https://t.me/LitleePrince"),
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="Main_help"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_caption(
            PM_START_TEXT.format(escape_markdown(first_name), escape_markdown(uptime), sql.num_users(), sql.num_chats()),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )


def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_caption(f"""
            
*ʜᴇʏ,
 ᴛʜɪs ɪs {BOT_NAME}, 
 
𝙅𝘼𝙎𝘼 𝘿𝙀𝙋𝙇𝙊𝙔 𝘽𝙊𝙏 𝙏𝙀𝙇𝙀𝙂𝙍𝘼𝙈*

❏ ᴜsᴇʀʙᴏᴛ ᴘʀᴇᴍɪᴜᴍ
├ ᴄᴏɴᴛᴏʜ ʙᴏᴛ @sellerzyricbot
├ ʜᴀʀɢᴀ 𝟸𝟻.𝟶𝟶𝟶 / ʙᴜʟᴀɴ
╰ sɪsᴛᴇᴍ ᴛᴇʀɪᴍᴀ ɪᴀᴅɪ

❏ ʙᴏᴛ ᴍᴜsɪᴄ + ᴍᴀɴᴀɢᴇ 
├ ʜᴀʀɢᴀ 𝟸𝟻𝟶.000 ᴅᴇᴘʟᴏʏ ʜᴇʀᴏᴋᴜ + ᴠᴘs. sɪsᴛᴇᴍ ᴛᴇʀɪᴍᴀ ɪᴀᴅɪ
╰ sɪsᴛᴇᴍ ᴛᴇʀɪᴍᴀ ɪᴀᴅɪ

❏ ʙᴏᴛ ᴍᴀɴᴀɢᴇ 
├ ʜᴀʀɢᴀ 𝟾𝟶.𝟶𝟶𝟶 
╰ sɪsᴛᴇᴍ ᴛᴇʀɪᴍᴀ ɪᴀᴅɪ

❏ *ᴄᴀᴛᴀᴛᴀɴ 

❏ ᴀᴘᴀʙɪʟᴀ ʙᴏᴛ ʏᴀɴɢ ᴀɴᴅᴀ ɪɴɢɪɴᴋᴀɴ 
├ ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴅɪ ʟɪsᴛ sɪʟᴀʜᴋᴀɴ ʙᴇʀᴛᴀɴʏᴀ 
╰ ᴏᴡɴᴇʀ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ*

❏ *ᴄᴀᴛᴀᴛᴀɴ ʜᴇʀᴏᴋᴜ ʀᴀᴡᴀɴ sᴜsᴘᴇɴ ᴊᴀᴅɪ 
╰ sᴀʏᴀ ᴅᴇᴘʟᴏʏ ᴅɪ ᴠᴘs*

❏ *sɪʟᴀʜᴋᴀɴ ʜᴜʙᴜɴɢɪ ᴏᴡɴᴇʀ ᴜɴᴛᴜᴋ / 
╰ ᴍᴇʟɪʜᴀᴛ ᴍᴇɴᴀɴʏᴀᴋᴀɴ ᴄᴏɴᴛᴏʜ ʙᴏᴛ

𝗦𝗘𝗞𝗜𝗔𝗡 𝗧𝗘𝗥𝗜𝗠𝗔 𝗞𝗔𝗦𝗜𝗛 𝗕𝗔𝗡𝗬𝗔𝗞 🙏*




""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="sᴏᴜʀᴄᴇ", callback_data="waduh_"),
                        InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url="https://t.me/SyncPublick"), 
                    ],
                    [
                        InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="Main_help")]]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name 
        query.message.edit_caption(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )

def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_photo(START_IMG,
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=" ʜᴇʟᴘ ​",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_photo(START_IMG,"» Wʜᴇʀᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ?.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 ᴏᴩᴇɴ ɪɴ ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ",
                            url="https://t.me/{}?start=help".format(context.bot.username),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="👥 ᴏᴩᴇɴ ʜᴇʀᴇ",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="help_back"),InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", callback_data="mukesh_support")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)

def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs​",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)



def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@{SUPPORT_CHAT}",
                photo=START_IMG,
                caption=f"""

〄 {BOT_NAME} *ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ* ☕
┏━━━━━━━━━━━━━━━━━━━━━
┠ ➻ *ᴘʏᴛʜᴏɴ* `{y()}`
┠ ➻ *ʟɪʙʀᴀʀʏ* `{telever}`
┠ ➻ *ᴛᴇʟᴇᴛʜᴏɴ* `{tlhver}`
┠ ➻ *ᴩʏʀᴏɢʀᴀᴍ* `{pyrover}`
┗━━━━━━━━━━━━━━━━━━━━━""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*", run_async=True)

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_", run_async=True)

    about_callback_handler = CallbackQueryHandler(
        Fallen_about_callback, pattern=r"fallen_", run_async=True
    )
    lo_callback_handler = CallbackQueryHandler(
        Bacot_lo_callback, pattern=r"berak_", run_async=True
    )
    habis_callback_handler = CallbackQueryHandler(
        Tidak_habis_callback, pattern=r"gagah_", run_async=True
    )
    bos_callback_handler = CallbackQueryHandler(
        Siap_bos_callback, pattern=r"kecoa_", run_async=True
    )
    ken_callback_handler = CallbackQueryHandler(
        Enoh_ken_callback, pattern=r"minum_", run_async=True
    )
    nurul_callback_handler = CallbackQueryHandler(
        Diluar_nurul_callback, pattern=r"makan_", run_async=True
    ) 
    atah_callback_handler = CallbackQueryHandler(
        Jurig_atah_callback, pattern=r"jurig_", run_async=True
    )
    nuhun_callback_handler = CallbackQueryHandler(
        Muhun_nuhun_callback, pattern=r"babi_", run_async=True
    )
    peduli_callback_handler = CallbackQueryHandler(
        Gak_peduli_callback, pattern=r"manuk_", run_async=True
    )
    suka_callback_handler = CallbackQueryHandler(
        Aku_suka_callback, pattern=r"tapai_", run_async=True
    )
    ya_callback_handler = CallbackQueryHandler(
        Viral_ya_callback, pattern=r"kacang_", run_async=True
    )
    pusing_callback_handler = CallbackQueryHandler(
        Waduh_pusing_callback, pattern=r"waduh_", run_async=True 
    )
    to_callback_handler = CallbackQueryHandler(   
        Monyet_to_callback, pattern=r"rangu_", run_async=True
    )
    sabi_callback_handler = CallbackQueryHandler(   
        Pasti_sabi_callback, pattern=r"mati_", run_async=True
    )
    ngontol_callback_handler = CallbackQueryHandler(
        Harlay_ngontol_callback, pattern=r"harlay_", run_async=True
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )
    mukeshrobot_main_handler = CallbackQueryHandler(
        MukeshRobot_Main_Callback, pattern=r".*_help",run_async=True
    )
    
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)   
    dispatcher.add_handler(atah_callback_handler)
    dispatcher.add_handler(ken_callback_handler)
    dispatcher.add_handler(nurul_callback_handler)
    dispatcher.add_handler(habis_callback_handler)
    dispatcher.add_handler(bos_callback_handler)
    dispatcher.add_handler(ya_callback_handler) 
    dispatcher.add_handler(pusing_callback_handler)
    dispatcher.add_handler(nuhun_callback_handler)
    dispatcher.add_handler(suka_callback_handler)
    dispatcher.add_handler(peduli_callback_handler)
    dispatcher.add_handler(to_callback_handler)
    dispatcher.add_handler(lo_callback_handler)
    dispatcher.add_handler(mukeshrobot_main_handler)
    dispatcher.add_handler(sabi_callback_handler)
    dispatcher.add_handler(about_callback_handler)               
    dispatcher.add_handler(ngontol_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
   

    dispatcher.add_error_handler(error_callback)

    
    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
