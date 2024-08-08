import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import OWNER_ID as owner_id
from YukkiMusic import app
import pytz

LOG_GRP = -1001665425160  # ID grup admin

# Dictionary to store the user who reported the bug and their message ID
bug_reports = {}
waiting_for_response = {}

@app.on_message(filters.photo & filters.private)
async def handle_bug_report(client, message):
    if message.caption and "#BUG" in message.caption:
        caption = message.caption
        # Send the bug report to the admin group
        message_sent = await client.send_photo(
            chat_id=LOG_GRP,
            photo=message.photo.file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {message.message_id}")]
            ])
        )

        # Debug: Check what attributes are available on the message_sent object
        print("Message Sent:", message_sent)
        print("Attributes:", dir(message_sent))

        # Save the report to track the message ID and the user ID
        if hasattr(message_sent, 'message_id'):
            bug_reports[message_sent.message_id] = message.from_user.id
        else:
            print("Error: 'message_id' not found on the message_sent object")

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

    # Send the bug report to the admin group
    message_sent = await client.send_message(
        chat_id=LOG_GRP,
        text=bug_report,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {message.id}")]
        ])
    )

    # Debug: Check what attributes are available on the message_sent object
    print("Message Sent:", message_sent)
    print("Attributes:", dir(message_sent))

    # Save the report to track the message ID and the user ID
    if hasattr(message_sent, 'message_id'):
        bug_reports[message_sent.message_id] = user_id
    else:
        print("Error: 'message_id' not found on the message_sent object")

    await message.reply("✅ Laporan bug Anda telah dikirim ke admin, tunggu balasan.")

@app.on_callback_query(filters.regex("jawab_pesan"))
async def handle_bug_reply(client, callback_query: CallbackQuery):
    message_id = int(callback_query.data.split()[1])
    user_id = bug_reports.get(message_id)
    
    if not user_id:
        await callback_query.answer("Pengguna tidak ditemukan.")
        return
    
    await callback_query.answer("Balasan akan dikirimkan ke pengguna.")
    await callback_query.message.edit("Admin, kirimkan balasan di sini:")

    # Store the message ID to track which message is being replied to
    waiting_for_response[callback_query.message.message_id] = user_id

@app.on_message(filters.chat(LOG_GRP))
async def handle_admin_response(client, message):
    if message.reply_to_message and message.reply_to_message.message_id in waiting_for_response:
        user_id = waiting_for_response[message.reply_to_message.message_id]

        # Send the reply to the user who reported the bug
        await client.send_message(
            user_id,
            f"Balasan dari admin:\n{message.text}"
        )

        # Confirm the reply to the admin
        await message.reply("✅ Balasan telah dikirim ke pengguna.")

        # Remove the message ID from waiting_for_response
        del waiting_for_response[message.reply_to_message.message_id]

@app.on_callback_query(filters.regex("batal"))
async def handle_cancel(client, callback_query: CallbackQuery):
    message_id = int(callback_query.data.split()[1])
    if message_id in waiting_for_response:
        user_id = waiting_for_response[message_id]
        del waiting_for_response[message_id]
        await client.send_message(user_id, "❌ Pembatalan permintaan.")
    await callback_query.message.delete()
