import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from YukkiMusic.utils.database import get_latest_bug_message_id, save_bug_message_id
from YukkiMusic.utils.decorators.admins import *
from config import OWNER_ID as owner_id  # Impor OWNER_ID
from YukkiMusic import app
import pytz

LOG_GRP = -1001665425160  # ID grup admin

@app.on_message(filters.photo & filters.private)
async def handle_bug_report(client, message):
    if message.caption and "#BUG" in message.caption:
        caption = message.caption
        # Kirim laporan bug ke grup admin
        await client.send_photo(
            chat_id=LOG_GRP,
            photo=message.photo.file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {message.from_user.id}")]
            ])
        )

        await message.reply("✅ Laporan bug Anda telah dikirim ke admin, tunggu balasan.")

@app.on_message(filters.command("bug"))
async def bug_command(client, message):
    if len(message.command) < 2:
        await message.reply("⚠️ Harap sertakan deskripsi bug setelah perintah.")
        return

    bug_description = " ".join(message.command[1:])
    user_id = message.from_user.id
    mention = f"[{message.from_user.first_name}](tg://user?id={user_id})"
    chat_username = f"@{message.chat.username}/`{message.chat.id}`" if message.chat.username else f"grup pribadi/`{message.chat.id}`"

    # Waktu dalam format WIB
    tz = pytz.timezone('Asia/Jakarta')
    current_time = datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S WIB")

    bug_report = f"""
**#BUG: ** **tg://user?id={user_id}**

**Dilaporkan oleh: ** **{mention}**
**ID Pengguna: ** **{user_id}**
**Chat: ** **{chat_username}**

**Bug: ** **{bug_description}**

**Waktu: ** **{current_time}**"""

    # Kirim laporan bug ke grup admin
    await client.send_message(
        chat_id=LOG_GRP,
        text=bug_report,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {user_id}")]
        ])
    )

    await message.reply("✅ Laporan bug Anda telah dikirim ke admin, tunggu balasan.")

@app.on_callback_query(filters.regex("jawab_pesan"))
async def handle_bug_reply(client, callback_query: CallbackQuery):
    admin_id = callback_query.from_user.id
    user_id = int(callback_query.data.split()[1])

    full_name = f"{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}"

    try:
        button = [[InlineKeyboardButton("Batal", callback_data=f"batal {admin_id}")]]
        await client.send_message(
            user_id,
            "Silahkan Kirimkan Balasan Anda.",
            reply_markup=InlineKeyboardMarkup(button)
        )
        response = await client.ask(
            user_id,
            "Kirimkan balasan Anda:",
            timeout=60
        )

        await client.send_message(
            user_id,
            "✅ Pesan Anda telah dikirim ke admin, silahkan tunggu balasannya."
        )
        await callback_query.message.delete()

        await client.send_message(
            admin_id,
            f"Balasan dari pengguna: {response.text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Jawab Lagi", callback_data=f"jawab_pesan {user_id}")]
            ])
        )

    except asyncio.TimeoutError:
        await client.send_message(user_id, "**❌ Pembatalan otomatis**")
        await client.send_message(
            admin_id,
            "❌ Pembatalan permintaan balasan dari pengguna."
        )
        await callback_query.message.delete()

@app.on_callback_query(filters.regex("batal"))
async def handle_cancel(client, callback_query: CallbackQuery):
    admin_id = int(callback_query.data.split()[1])
    await client.send_message(admin_id, "❌ Pembatalan permintaan.")
    await callback_query.message.delete()
