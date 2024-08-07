from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from YukkiMusic.utils.database import get_latest_bug_message_id, save_bug_message_id
from YukkiMusic.utils.decorators.admins import *
from config import OWNER_ID as owner_id
from YukkiMusic import app

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
            try:
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

                # Tambahkan logging untuk memeriksa objek sent_message
                print(f"Sent message object: {sent_message}")

                # Pastikan ID tersedia
                if hasattr(sent_message, 'id'):
                    # Simpan ID pesan dan verifikasi penyimpanan
                    await save_bug_message_id(sent_message.id)
                    print(f"Bug message ID saved: {sent_message.id}")  # Debugging
                    await msg.reply_text(
                        f"<b>Laporan Bug: {bugs}</b>\n\n"
                        "<b>Bug berhasil dilaporkan ke grup dukungan!</b>",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("Tutup", callback_data="close_data")]]
                        ),
                    )
                else:
                    await msg.reply_text("ID pesan tidak ditemukan dalam objek pesan yang dikembalikan.")
            except Exception as e:
                await msg.reply_text(f"Terjadi kesalahan saat mengirim laporan bug: {e}")
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
async def reply_bug(c, callback_query: CallbackQuery):
    user_id = int(callback_query.from_user.id)
    original_bug_report_id = int(callback_query.data.split()[1])  # Pastikan format data sesuai

    # Kirim pesan balasan
    try:
        await c.send_message(
            user_id,
            "Silahkan kirimkan balasan Anda.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Batal", callback_data=f"batal {user_id}")]])
        )
        await callback_query.answer("Balasan berhasil dikirim. Tunggu balasan Anda.")
    except Exception as e:
        print(f"Error: {e}")
        await callback_query.answer("Gagal mengirim balasan.")
