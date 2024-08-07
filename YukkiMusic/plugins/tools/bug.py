from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from config import OWNER_ID as owner_id
from YukkiMusic import app


def content(msg: Message) -> [None, str]:
    text_to_return = msg.text

    if msg.text is None:
        return None
    if " " in text_to_return:
        try:
            return msg.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@app.on_message(filters.command("bug"))
async def bugs(_, msg: Message):
    if msg.chat.username:
        chat_username = f"@{msg.chat.username}/`{msg.chat.id}`"
    else:
        chat_username = f"grup pribadi/`{msg.chat.id}`"

    bugs = content(msg)
    user_id = msg.from_user.id
    mention = (
        "[" + msg.from_user.first_name + "](tg://user?id=" + str(msg.from_user.id) + ")"
    )
    datetimes_fmt = "%d-%m-%Y"
    datetimes = datetime.utcnow().strftime(datetimes_fmt)

    bug_report = f"""
**#BUG: ** **tg://user?id={owner_id}**

**Dilaporkan oleh: ** **{mention}**
**ID Pengguna: ** **{user_id}**
**Chat: ** **{chat_username}**

**Bug: ** **{bugs}**

**Waktu: ** **{datetimes}**"""

    if msg.chat.type == "private":
        await msg.reply_text("<b>Perintah ini hanya untuk grup.</b>")
        return

    if user_id == owner_id:
        if bugs:
            await msg.reply_text(
                "<b>Apakah kamu bercanda? Kamu adalah pemilik bot ini.</b>",
            )
            return
        else:
            await msg.reply_text("Tidak ada bug untuk dilaporkan.")
    elif user_id != owner_id:
        if bugs:
            await msg.reply_text(
                f"<b>Laporan Bug: {bugs}</b>\n\n"
                "<b>Bug berhasil dilaporkan ke grup dukungan!</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Tutup", callback_data="close_data")]]
                ),
            )
            await app.send_photo(
                -1002024677280,
                photo="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
                caption=f"{bug_report}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Lihat Bug", url=f"{msg.link}")],
                        [
                            InlineKeyboardButton(
                                "Tutup", callback_data="close_send_photo"
                            )
                        ],
                    ]
                ),
            )
        else:
            await msg.reply_text(
                f"<b>Tidak ada bug untuk dilaporkan!</b>",
            )


@app.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(_, query: CallbackQuery):
    is_admin = await app.get_chat_member(query.message.chat.id, query.from_user.id)
    if not is_admin.privileges.can_delete_messages:
        await query.answer("Anda tidak memiliki hak untuk menutup ini.", show_alert=True)
    else:
        await query.message.delete()
