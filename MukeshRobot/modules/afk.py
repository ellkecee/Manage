#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiAFKBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiAFKBot/blob/master/LICENSE >
#
# All rights reserved.
#

import time
import re 

from pyrogram import Client, filters, enums
from pyrogram.types import Message 
from pyrogram import raw 
from typing import Optional 
from pyrogram import utils
from pyrogram.errors import PeerIdInvalid

from MukeshRobot import pbot as app 
from MukeshRobot.utils.errors import capture_err 
from MukeshRobot.utils.mongo import add_afk, is_afk, remove_afk, add_served_chat
from MukeshRobot.utils.functions import get_readable_time2

# Handle set AFK Command
@app.on_message(filters.command(["afk"]))
async def active_afk(_, ctx: Message):
    if ctx.sender_chat:
        return 
    user_id = ctx.from_user.id
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await remove_afk(user_id)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time2((int(time.time() - timeafk)))
            if afktype == "animation":
                if str(reasonafk) == "None":
                    return await ctx.reply_animation(
                    data, 
                    caption=f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Telah Afk Sejak `{seenago}`\n\nAlasan: `{reasonafk}`",
                    )
                else:
                     return await ctx.reply_animation(
                     data,
                     caption=f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Telah Afk Sejak `{seenago}`",
                     )
            if afktype == "photo":
                if str(reasonafk) == "None":  # Perhatikan koreksi ini
                    return await ctx.reply_photo(
                    photo=f"downloads/{user_id}.jpg",
                    caption=f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Telah Afk Sejak `{seenago}`\n\nAlasan: `{reasonafk}`",
                    )
                else:  
                     return await ctx.reply_photo(
                     photo=f"downloads/{user_id}.jpg",
                     caption=f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Telah Afk Sejak `{seenago}`",
                     )
            if afktype == "text":
                return await ctx.reply_text( 
                    f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Telah Afk Sejak `{seenago}`",
                       disable_web_page_preview=True,
                     )
            if afktype == "text_reason":
                return await ctx.reply_text( 
                    f"downloads/{user_id}.jpg",
                     caption=f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Telah Afk Sejak `{seenago}`",
                    
                    disable_web_page_preview=True,
                )
        except Exception as e:
            return await ctx.reply_text(f"{ctx.from_user.first_name} [`{ctx.from_user.id}`] Kembali Online",
                
                disable_web_page_preview=True,
            )
    if len(ctx.command) == 1 and not ctx.reply_to_message:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(ctx.command) > 1 and not ctx.reply_to_message:
        _reason = (ctx.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "text_reason",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif len(ctx.command) == 1 and ctx.reply_to_message.animation:
        _data = ctx.reply_to_message.animation.file_id
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": None,
        }
    elif len(ctx.command) > 1 and ctx.reply_to_message.animation:
        _data = ctx.reply_to_message.animation.file_id
        _reason = (ctx.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": _reason,
        }
    elif len(ctx.command) == 1 and ctx.reply_to_message.photo:
        await app.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(ctx.command) > 1 and ctx.reply_to_message.photo:
        await app.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
        _reason = ctx.text.split(None, 1)[1].strip()
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif len(ctx.command) == 1 and ctx.reply_to_message.sticker:
        if ctx.reply_to_message.sticker.is_animated:
            details = {
                "type": "text",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
        else:
            await app.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
    elif len(ctx.command) > 1 and ctx.reply_to_message.sticker:
        _reason = (ctx.text.split(None, 1)[1].strip())[:100]
        if ctx.reply_to_message.sticker.is_animated:
            details = {
                "type": "text_reason",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
        else:
            await app.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
    else:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }

    await add_afk(user_id, details)
    await ctx.reply_text(f"{ctx.from_user.mention} [`{ctx.from_user.id}`] Sekarang Afk")
    


# Detect user that AFK based on Yukki Repo
@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=8,
)
async def afk_watcher_func(self: Client, ctx: Message):
    if ctx.sender_chat:
        return
    userid = ctx.from_user.id
    user_name = ctx.from_user.mention
    if ctx.entities:
        possible = ["/afk", f"/afk@{self.me.username}", "!afk"]
        message_text = ctx.text or ctx.caption
        for entity in ctx.entities:
            try:
                if (
                    entity.type == enums.MessageEntityType.BOT_COMMAND
                    and (message_text[0 : 0 + entity.length]).lower() in possible
                ):
                    return
            except UnicodeDecodeError:  # Some weird character make error
                return

    msg = ""
    replied_user_id = 0

    # Self AFK
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time2((int(time.time() - timeafk)))
            if afktype == "text":
                msg += f"{user_name} [`{userid}`] kembali online dan telah afk selama `{seenago}`"
            if afktype == "text_reason":
                msg += f"{user_name} [`{userid}`] kembali online dan telah afk selama `{seenago}`\n\nAlasan: `{reasonafk}`"
            if afktype == "animation":
                if str(reasonafk) == "None":
                    await ctx.reply_animation(
                        data,
                        caption=f"{user_name} [`{userid}`] kembali online dan telah afk selama `{seenago}`",
                        
                    )
                else:
                    await ctx.reply_animation(
                        data,
                        caption=f"{user_name} [`{userid}`] kembali online dan telah afk selama `{seenago}`\n\nAlasan: `{reasonafk}`",
                        )
                    
            if afktype == "photo":
                if str(reasonafk) == "None":
                    await ctx.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=f"{user_name} [`{userid}`] kembali online dan telah afk selama `{seenago}`",
                        
                    )
                else:
                    await ctx.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=f"{user_name} [`{userid}`] kembali online dan telah afk selama `{seenago}`\n\nAlasan: `{reasonafk}`",
                        
                    )
        except:
            msg += f"{user_name} [`{userid}`] kembali online"

    # Replied to a User which is AFK
    if ctx.reply_to_message:
        try:
            replied_first_name = ctx.reply_to_message.from_user.mention
            replied_user_id = ctx.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                try:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    data = reasondb["data"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time2((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += f"{replied_first_name} [`{replied_user_id}`] Telah Afk Sejak `{seenago}`"
                    if afktype == "text_reason":
                        msg += f"{replied_first_name} [`{replied_user_id}`] Telah Afk Sejak `{seenago}`\n\nAlasan: `{reasonafk}`"
                        
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            send = await ctx.reply_animation(
                                data,
                                caption=f"{replied_first_name} [`{replied_user_id}`] Telah Afk Sejak `{seenago}`",
                            )
                        else:
                            send = await ctx.reply_animation(
                                data,
                                caption=f"{replied_first_name} [`{replied_user_id}`] Telah Afk Sejak `{seenago}`\n\nAlasan: `{reasonafk}`",
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            send = await ctx.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"{replied_first_name} [`{replied_user_id}`] Telah Afk Sejak `{seenago}`",
                            )
                        else:
                            send = await ctx.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"{replied_first_name} [`{replied_user_id}`] Telah Afk Sejak `{seenago}`\n\nAlasan: `{reasonafk}`",
                            )
                except Exception:
                    msg += f"{replied_first_name} [`{replied_user_id}`] Sedang Afk",
                    
        except:
            pass

    # If username or mentioned user is AFK
    if ctx.entities:
        entity = ctx.entities
        j = 0
        for _ in range(len(entity)):
            if (entity[j].type) == enums.MessageEntityType.MENTION:
                found = re.findall("@([_0-9a-zA-Z]+)", ctx.text)
                try:
                    get_user = found[j]
                    user = await app.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time2((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += f"{user.first_name[:25]} [`{userid}`] Telah Afk sejak `{seenago}` yang lalu"
                            
                        if afktype == "text_reason":
                            msg +=f"{user.first_name[:25]} [`{userid}`] Telah Afk Sejak `{seenago}` Yang Lalu\n\n Alasan: `{reasonafk}`"
                            
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_animation(
                                    data,
                                    caption=f"{user.first_name[:25]} [`{userid}`] Telah Afk sejak `{seenago}` Yang lalu",
                                )
                            else:
                                send = await ctx.reply_animation(
                                    data,
                                    caption=f"{user.first_name[:25]} [`{userid}`] Telah Afk Sejak `{seenago}` Yang lalu\n\n Alasan: `{reasonafk}`",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"{user.first_name[:25]} [`{userid}`] Telah Afk Sejak  `{seenago}` Yang lalu",
                                )
                            else:
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"{user.first_name[:25]} [`{userid}`] Telah Afk sejak `{seenago}` yang lalu\n\n Alasan: `{reasonafk}`",
                                )
                    except:
                        msg += f"{user.first_name[:25]} [`{userid}`] Sedang Afk"
                        
            elif (entity[j].type) == enums.MessageEntityType.TEXT_MENTION:
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time2((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += f"{first_name[:25]} [`{user_id}`] Telah Afk sejak `{seenago}` Yang lalu"
                        if afktype == "text_reason":
                            msg += f"{first_name[:25]} [`{user_id}`] Telah Afk Sejak `{seenago}` Yang lalu\n\n Alasan: `{reasonafk}`"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_animation(
                                    data,
                                    caption=f"{first_name[:25]} [`{user_id}`] Telah Afk sejak `{seenago}` Yang lalu",
                                )
                            else:
                                send = await ctx.reply_animation(
                                    data,
                                    caption=f"{first_name[:25]} [`{user_id}`] Telah Afk Sejak `{seenago}` Yang lalu\n\n Alasan: `{reasonafk}`",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"{first_name[:25]} [`{user_id}`] Telah Afk sejak `{seenago}` Yang lalu",
                                )
                            else:
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"{first_name[:25]} [`{user_id}`] Telah Afk Sejak `{seenago}` Yang lalu\n\n Alasan: `{reasonafk}`",
                                )
                    except:
                        msg += f"{first_name[:25]} [`{user_id}`] Sedang Afk"
            j += 1
    if msg != "":
        try:
            await ctx.reply_text(msg, disable_web_page_preview=True)
        except:
            return
    
   
__help__ = """
 ❍ /afk <reason>*:* ᴍᴀʀᴋ ʏᴏᴜʀsᴇʟғ ᴀs ᴀғᴋ(ᴀᴡᴀʏ ғʀᴏᴍ ᴋᴇʏʙᴏᴀʀᴅ).
 ❍ ʙʏᴇ <ʀᴇᴀsᴏɴ>*:* sᴀᴍᴇ ᴀs ᴛʜᴇ ᴀғᴋ ᴄᴏᴍᴍᴀɴᴅ - ʙᴜᴛ ɴᴏᴛ ᴀ ᴄᴏᴍᴍᴀɴᴅ.
ᴡʜᴇɴ ᴍᴀʀᴋᴇᴅ ᴀs ᴀғᴋ, ᴀɴʏ ᴍᴇɴᴛɪᴏɴs ᴡɪʟʟ ʙᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴡɪᴛʜ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴀʏ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ!
"""
__mod_name__ = "ᴀғᴋ"