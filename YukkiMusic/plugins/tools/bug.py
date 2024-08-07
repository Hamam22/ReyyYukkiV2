from datetime import datetime
from pymongo import MongoClient
from pyrogram import filters
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
            # Simpan ID pesan bug
            save_bug_message_id(sent_message.message_id)

            await msg.reply_text(
                f"<b>Laporan Bug: {bugs}</b>\n\n"
                "<b>Bug berhasil dilaporkan ke grup dukungan!</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Tutup", callback_data="close_data")]]
                ),
            )
        else:
            await msg.reply_text("<b>Tidak ada bug untuk dilaporkan!</b>")

@app.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(_, query: CallbackQuery):
    is_admin = await app.get_chat_member(query.message.chat.id, query.from_user.id)
    if not is_admin.privileges.can_delete_messages:
        await query.answer("Anda tidak memiliki hak untuk menutup ini.", show_alert=True)
    else:
        await query.message.delete()

@app.on_callback_query(filters.regex("reply_bug"))
async def reply_bug(_, query: CallbackQuery):
    is_admin = await app.get_chat_member(query.message.chat.id, query.from_user.id)
    if not is_admin.privileges.can_post_messages:
        await query.answer("Anda tidak memiliki hak untuk membalas pesan ini.", show_alert=True)
    else:
        # Ambil ID pesan bug yang benar dari MongoDB
        bug_message_id = get_latest_bug_message_id()
        if bug_message_id:
            try:
                await app.send_message(
                    query.message.chat.id,
                    text="Balasan untuk laporan bug.",
                    reply_to_message_id=bug_message_id
                )
                await query.answer("Balasan berhasil dikirim.")
            except Exception as e:
                await query.answer(f"Terjadi kesalahan: {e}", show_alert=True)
        else:
            await query.answer("ID pesan bug tidak ditemukan.", show_alert=True)
