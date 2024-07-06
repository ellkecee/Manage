import asyncio
import random
from pyrogram import *
from pyrogram.errors import *  
from functools import wraps
from traceback import format_exc as err
import asyncio
import re
from contextlib import suppress
from time import time
from pyrogram.errors.exceptions.forbidden_403 import *
from pyrogram.types import *
from pyrogram import *
from pyrogram.enums import *  
from functools import wraps
from pyrogram.raw.functions.messages import *
from MukeshRobot import *
from MukeshRobot import EVENT_LOGS, DEV_USERS
from MukeshRobot.utils.errors import capture_err 
from MukeshRobot import pbot as app 
from MukeshRobot.utils.tools import *
from MukeshRobot.utils.mongo import (
    add_userdata,
    cek_userdata,
    get_userdata,
    is_sangmata_on,
    sangmata_off,
    sangmata_on,
)


    

async def authorised(func, subFunc2, client, message, *args, **kwargs):
    chatID = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    except Exception as e:
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(e)
    return subFunc2


async def unauthorised(message: Message, permission, subFunc2):
    text = f"You don't have the required permission to perform this action.\n**Permission:** __{permission}__"
    chatID = message.chat.id
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    return subFunc2

def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if message.sender_chat and message.sender_chat.id == message.chat.id:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(message, permission, subFunc2)
            # For admins and sudo users
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if userID not in DEV_USERS and permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(func, subFunc2, client, message, *args, **kwargs)

        return subFunc2

    return subFunc

async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = (await app.get_chat_member(chat_id, user_id)).privileges
    if not member:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_video_chats:
        perms.append("can_manage_video_chats")
    return perms

admins_in_chat = {}

@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=3,
)
async def cek_mataa(_, ctx: Message):
    if ctx.sender_chat or not await is_sangmata_on(ctx.chat.id):
        return
    if not await cek_userdata(ctx.from_user.id):
        return await add_userdata(ctx.from_user.id, ctx.from_user.username, ctx.from_user.first_name, ctx.from_user.last_name)
    usernamebefore, first_name, lastname_before = await get_userdata(ctx.from_user.id)
    msg = ""
    if usernamebefore != ctx.from_user.username or first_name != ctx.from_user.first_name or lastname_before != ctx.from_user.last_name:
        msg += f"👀 <b>Sangmata</b>\n\n User: {ctx.from_user.mention} [<code>{ctx.from_user.id}</code>]\n"
    if usernamebefore != ctx.from_user.username:
        usernamebefore = f"@{usernamebefore}" if usernamebefore else "<code>Tanpa Username</code>"
        usernameafter = f"@{ctx.from_user.username}" if ctx.from_user.username else "<code>Tanpa Username</code>"
        msg += f"`Mengubah username dari {usernamebefore} ke {usernameafter}.`\n"
        await add_userdata(ctx.from_user.id, ctx.from_user.username, ctx.from_user.first_name, ctx.from_user.last_name)
    if first_name != ctx.from_user.first_name:
        msg += f"`Mengubah nama depan dari {first_name} ke {ctx.from_user.first_name}.`\n"
        await add_userdata(ctx.from_user.id, ctx.from_user.username, ctx.from_user.first_name, ctx.from_user.last_name)
    if lastname_before != ctx.from_user.last_name:
        lastname_before = lastname_before or "`Tanpa Nama Belakang`"
        lastname_after = ctx.from_user.last_name or "`Tanpa Nama Belakang`"
        msg += f"`Mengubah nama belakang dari {lastname_before} ke {lastname_after}.`\n"
        await add_userdata(ctx.from_user.id, ctx.from_user.username, ctx.from_user.first_name, ctx.from_user.last_name)
    if msg != "":
        await ctx.reply_text(msg, quote=True)


@app.on_message(filters.group & filters.command("sangmata"))
@adminsOnly("can_change_info")
async def set_mataa(_, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply_text("Gunakan <code>/on</code>, untuk mengaktifkan sangmata. Jika Anda ingin menonaktifkan, Anda dapat menggunakan parameter off.")
    if ctx.command[1] == "on":
        cekset = await is_sangmata_on(ctx.chat.id)
        if cekset:
            await ctx.reply_text("SangMata telah diaktifkan di grup Anda.")
        else:
            await sangmata_on(ctx.chat.id)
            await ctx.reply_text("Sangmata diaktifkan di grup Anda.")
    elif ctx.command[1] == "off":
        cekset = await is_sangmata_on(ctx.chat.id)
        if not cekset:
            await ctx.reply_text("SangMata telah dinonaktifkan di grup Anda.")
        else:
            await sangmata_off(ctx.chat.id)
            await ctx.reply_text("Sangmata dinonaktifkan di grup Anda.")
    else:
        await ctx.reply_text("Parameter tidak diketahui, gunakan hanya parameter on/off.", del_in=6)


__mod_name__ = "sᴀɴɢᴍᴀᴛᴀ"

__help__ = """
Tʜɪs ғᴇᴀᴛᴜʀᴇ ɪɴsᴘɪʀᴇᴅ ғʀᴏᴍ SᴀɴɢMᴀᴛᴀ Bᴏᴛ. I'ᴍ ᴄʀᴇᴀᴛᴇᴅ sɪᴍᴘʟᴇ ᴅᴇᴛᴇᴄᴛɪᴏɴ ᴛᴏ ᴄʜᴇᴄᴋ ᴜsᴇʀ ᴅᴀᴛᴀ ɪɴᴄʟᴜᴅᴇ ᴜsᴇʀɴᴀᴍᴇ, ғɪʀsᴛ_ɴᴀᴍᴇ, ᴀɴᴅ ʟᴀsᴛ_ɴᴀᴍᴇ.
/sangmata [ᴏɴ/ᴏғғ] - Eɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ sᴀɴɢᴍᴀᴛᴀ ɪɴ ɢʀᴏᴜᴘs.

"""



