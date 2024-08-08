import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import OWNER_ID as owner_id
from YukkiMusic import app
import pytz

LOG_GRP = -1001665425160  # ID grup admin

# Dictionary to store user waiting for response
waiting_for_response = {}
bug_reports = {}

@app.on_message(filters.photo & filters.private)
async def handle_bug_report(client, message):
    if message.caption and "#BUG" in message.caption:
        caption = message.caption
        # Kirim laporan bug ke grup admin
        sent_message = await client.send_photo(
            chat_id=LOG_GRP,
            photo=message.photo.file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {message.from_user.id}")]
            ])
        )

        # Verifikasi bahwa `sent_message` adalah objek `Message` dengan atribut `message_id`
        if hasattr(sent_message, 'message_id'):
            # Simpan informasi laporan bug
            bug_reports[sent_message.message_id] = message.from_user.id

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
    sent_message = await client.send_message(
        chat_id=LOG_GRP,
        text=bug_report,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {user_id}")]
        ])
    )

    # Verifikasi bahwa `sent_message` adalah objek `Message` dengan atribut `message_id`
    if hasattr(sent_message, 'message_id'):
        # Simpan informasi laporan bug
        bug_reports[sent_message.message_id] = user_id

    await message.reply("✅ Laporan bug Anda telah dikirim ke admin, tunggu balasan.")

@app.on_callback_query(filters.regex("jawab_pesan"))
async def handle_bug_reply(client, callback_query: CallbackQuery):
    admin_id = callback_query.from_user.id
    user_id = int(callback_query.data.split()[1])

    # Simpan ID pengguna yang menunggu balasan
    waiting_for_response[admin_id] = user_id

    # Kirimkan pesan ke grup admin meminta balasan
    await client.send_message(
        LOG_GRP,
        f"Admin {admin_id} siap menjawab laporan bug dari pengguna {user_id}. Kirimkan balasan di sini:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Batal", callback_data=f"batal {admin_id}")]
        ])
    )

    # Hapus pesan tombol "Jawab"
    await callback_query.message.delete()

@app.on_message(filters.chat(LOG_GRP) & filters.reply)
async def handle_admin_response(client, message):
    if message.reply_to_message and message.reply_to_message.message_id in bug_reports:
        user_id = bug_reports[message.reply_to_message.message_id]

        # Kirim balasan ke pengguna
        await client.send_message(
            user_id,
            f"Balasan dari admin: {message.text}"
        )

        # Hapus entri dari dictionary
        del bug_reports[message.reply_to_message.message_id]

        # Acknowledge admin
        await message.reply("✅ Pesan Anda telah dikirim ke pengguna. Terima kasih!")

@app.on_callback_query(filters.regex("batal"))
async def handle_cancel(client, callback_query: CallbackQuery):
    admin_id = int(callback_query.data.split()[1])
    if admin_id in waiting_for_response:
        user_id = waiting_for_response[admin_id]
        del waiting_for_response[admin_id]
        await client.send_message(user_id, "❌ Pembatalan permintaan.")
    await callback_query.message.delete()
