from datetime import datetime
from pymongo import MongoClient
from pyrogram import filters
from YukkiMusic.utils.database import get_latest_bug_message_id, save_bug_message_id
from YukkiMusic.utils.decorators.admins import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from config import OWNER_ID as owner_id
from YukkiMusic import app

# Fungsi untuk mendapatkan konten pesan setelah perintah
def content(msg: Message) -> [None, str]:
    text_to_return = msg.text
    if text_to_return and " " in text_to_return:
        try:
            return text_to_return.split(None, 1)[1]
        except IndexError:
            return None
    return None

@app.on_message(filters.command("bug"))
async def bugs(_, msg: Message):
    if msg.chat.username:
        chat_username = f"@{msg.chat.username}/`{msg.chat.id}`"
    else:
        chat_username = f"grup pribadi/`{msg.chat.id}`"

    bugs = content(msg)
    user_id = msg.from_user.id
    mention = f"[{msg.from_user.first_name}](tg://user?id={user_id})"
    datetimes_fmt = "%d-%m-%Y"
    datetimes = datetime.utcnow().strftime(datetimes_fmt)

    bug_report = f"""
**#BUG: ** **tg://user?id={owner_id}**

**Dilaporkan oleh: ** **{mention}**
**ID Pengguna: ** **{user_id}**
**Chat: ** **{chat_username}**

**Bug: ** **{bugs if bugs else 'Tidak ada deskripsi bug.'}**

**Waktu: ** **{datetimes}**"""

    if msg.chat.type == "private":
        await msg.reply_text("<b>Perintah ini hanya untuk grup.</b>")
        return

    if user_id == owner_id:
        if bugs:
            await msg.reply_text(
                "<b>Apakah kamu bercanda? Kamu adalah pemilik bot ini.</b>"
            )
        else:
            await msg.reply_text("Tidak ada bug untuk dilaporkan.")
    else:
        if bugs:
            sent_message = await app.send_photo(
                -1001665425160,  # ID chat grup dukungan
                photo="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
                caption=f"{bug_report}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Lihat Bug", url=f"{msg.link}")],
                        [
                            InlineKeyboardButton("Tutup", callback_data="close_send_photo"),
                            InlineKeyboardButton("Balas", callback_data="reply_bug")
                        ],
                    ]
                )
            )

            # Debugging: periksa objek sent_message
            print(f"Sent message object: {sent_message}")

            # Pastikan ID tersedia
            if hasattr(sent_message, 'id'):
                await save_bug_message_id(sent_message.id)  # Tunggu hingga selesai
                await msg.reply_text(
                    f"<b>Laporan Bug: {bugs}</b>\n\n"
                    "<b>Bug berhasil dilaporkan ke grup dukungan!</b>",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Tutup", callback_data="close_data")]]
                    ),
                )
            else:
                await msg.reply_text("ID pesan tidak ditemukan dalam objek pesan yang dikembalikan.")
        else:
            await msg.reply_text("<b>Tidak ada bug untuk dilaporkan!</b>")
