import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import OWNER_ID as owner_id
from YukkiMusic import app
import pytz
import logging

LOG_GRP = -1001665425160  # ID grup admin
OWNER_ID = 843830036

# Dictionary to store user waiting for response
waiting_for_response = {}
bug_reports = {}

logging.basicConfig(level=logging.INFO)

@app.on_message(filters.photo & filters.private)
async def handle_bug_report(client, message):
    if message.caption and "#BUG" in message.caption:
        caption = message.caption
        try:
            # Kirim laporan bug ke grup admin
            sent_message = await client.send_photo(
                chat_id=LOG_GRP,
                photo=message.photo.file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {message.from_user.id}")]
                ])
            )

            # Simpan informasi laporan bug
            if hasattr(sent_message, 'message_id'):
                bug_reports[sent_message.message_id] = message.from_user.id
                logging.info(f"Bug report sent: {sent_message.message_id} -> {message.from_user.id}")

            await message.reply("✅ Laporan bug Anda telah dikirim ke admin, tunggu balasan.")
        except Exception as e:
            logging.error(f"Error sending bug report photo: {e}")
            await message.reply("❌ Terjadi kesalahan saat mengirim laporan bug.")

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

    try:
        # Kirim laporan bug ke grup admin
        sent_message = await client.send_message(
            chat_id=LOG_GRP,
            text=bug_report,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {user_id}")]
            ])
        )

        # Simpan informasi laporan bug
        if hasattr(sent_message, 'message_id'):
            bug_reports[sent_message.message_id] = user_id
            logging.info(f"Bug report sent: {sent_message.message_id} -> {user_id}")

        await message.reply("✅ Laporan bug Anda telah dikirim ke admin, tunggu balasan.")
    except Exception as e:
        logging.error(f"Error sending bug report message: {e}")
        await message.reply("❌ Terjadi kesalahan saat mengirim laporan bug.")

@app.on_callback_query(filters.regex("jawab_pesan"))
async def handle_bug_reply(client, callback_query: CallbackQuery):
    admin_id = callback_query.from_user.id
    user_id = int(callback_query.data.split()[1])

    # Simpan ID pengguna yang menunggu balasan jika yang menjawab adalah owner
    if admin_id == OWNER_ID:
        waiting_for_response[admin_id] = user_id
        logging.info(f"Owner {admin_id} ready to respond to user {user_id}")

        try:
            # Kirimkan pesan ke grup admin meminta balasan
            await client.send_message(
                LOG_GRP,
                f"Pemilik {admin_id} siap menjawab laporan bug dari pengguna {user_id}. Kirimkan balasan di sini:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Batal", callback_data=f"batal {admin_id}")]
                ])
            )

            # Hapus pesan tombol "Jawab"
            await callback_query.message.delete()
        except Exception as e:
            logging.error(f"Error handling bug reply: {e}")
            await callback_query.message.reply("❌ Terjadi kesalahan saat memproses balasan.")
    else:
        await callback_query.message.reply("❌ Hanya pemilik yang dapat menjawab laporan bug.")

@app.on_message(filters.chat(LOG_GRP) & filters.reply)
async def handle_admin_response(client, message):
    if message.reply_to_message and message.reply_to_message.message_id in bug_reports:
        user_id = bug_reports[message.reply_to_message.message_id]

        # Pastikan hanya owner yang dapat mengirim balasan
        if message.from_user.id == OWNER_ID:
            try:
                # Kirim balasan ke pengguna
                await client.send_message(
                    user_id,
                    f"Balasan dari pemilik: {message.text}"
                )
                logging.info(f"Response sent to user {user_id}: {message.text}")

                # Hapus entri dari dictionary
                del bug_reports[message.reply_to_message.message_id]

                # Acknowledge pemilik
                await message.reply("✅ Pesan Anda telah dikirim ke pengguna. Terima kasih!")
            except Exception as e:
                logging.error(f"Error sending admin response: {e}")
                await message.reply("❌ Terjadi kesalahan saat mengirim balasan.")
        else:
            await message.reply("❌ Hanya pemilik yang dapat mengirim balasan.")
    else:
        await message.reply("❌ Tidak dapat menemukan laporan bug yang relevan.")

@app.on_callback_query(filters.regex("batal"))
async def handle_cancel(client, callback_query: CallbackQuery):
    admin_id = int(callback_query.data.split()[1])
    if admin_id in waiting_for_response:
        user_id = waiting_for_response[admin_id]
        del waiting_for_response[admin_id]
        try:
            await client.send_message(user_id, "❌ Pembatalan permintaan.")
            logging.info(f"Cancellation message sent to user {user_id}")
        except Exception as e:
            logging.error(f"Error sending cancel message: {e}")
    await callback_query.message.delete()
