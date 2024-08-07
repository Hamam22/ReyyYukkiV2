import datetime
import pytz
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from YukkiMusic import app
from YukkiMusic.utils.decorators.admins import AdminCtual
from config import BANNED_USERS

absen_data = {}

@app.on_message(filters.command("absen") & filters.group & ~(BANNED_USERS))
@AdminCtual
async def absensi_menu(client, message: Message, _):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Absen Masuk", callback_data="absenmasuk"),
                InlineKeyboardButton("Absen Pulang", callback_data="absenpulang"),
            ],
            [
                InlineKeyboardButton("Lihat Absensi Masuk", callback_data="lihatabsenmasuk"),
                InlineKeyboardButton("Lihat Absensi Pulang", callback_data="lihatabsenpulang"),
            ],
            [
                InlineKeyboardButton("Reset Absensi", callback_data="resetabsensi"),
            ]
        ]
    )
    await message.reply_text("Silakan pilih opsi absensi:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^absenmasuk$"))
async def absen_masuk_callback(_, callback_query):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.username
    now = datetime.datetime.now(pytz.timezone('Asia/Jakarta'))
    absen_time = now.strftime("%Y-%m-%d %H:%M:%S")
    day = now.strftime("%A, %d %B %Y")
    grup_id = callback_query.message.chat.id
    if grup_id not in absen_data:
        absen_data[grup_id] = {'absen_masuk': {}, 'absen_pulang': {}}
    if user_id not in absen_data[grup_id]['absen_masuk']:
        absen_data[grup_id]['absen_masuk'][user_id] = {'username': user_name, 'masuk_time': absen_time}
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(f"Absen masuk berhasil pada {absen_time} ({day}).", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(f"Anda sudah melakukan absensi masuk pada {absen_time} ({day}).", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^absenpulang$"))
async def absen_pulang_callback(_, callback_query):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.username
    now = datetime.datetime.now(pytz.timezone('Asia/Jakarta'))
    absen_time = now.strftime("%Y-%m-%d %H:%M:%S")
    day = now.strftime("%A, %d %B %Y")
    grup_id = callback_query.message.chat.id
    if grup_id not in absen_data:
        absen_data[grup_id] = {'absen_masuk': {}, 'absen_pulang': {}}
    if user_id in absen_data[grup_id]['absen_masuk'] and user_id not in absen_data[grup_id]['absen_pulang']:
        absen_data[grup_id]['absen_pulang'][user_id] = {'username': user_name, 'pulang_time': absen_time}
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(f"Absen pulang berhasil pada {absen_time} ({day}).", reply_markup=keyboard)
    elif user_id in absen_data[grup_id]['absen_pulang']:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(f"Anda sudah melakukan absensi pulang pada {absen_time} ({day}).", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(f"Anda belum melakukan absensi masuk pada {absen_time} ({day}).", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^lihatabsenmasuk$"))
async def lihat_absensi_masuk_callback(_, callback_query):
    grup_id = callback_query.message.chat.id
    if grup_id in absen_data:
        absensi_text = "Daftar Absensi Masuk:\n"
        for user_id, data in absen_data[grup_id]['absen_masuk'].items():
            absensi_text += f"{data['username']}: Masuk pada {data['masuk_time']}\n"
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(absensi_text, reply_markup=keyboard)
    else:
        await callback_query.edit_message_text("Belum ada data absensi masuk.", reply_markup=None)

@app.on_callback_query(filters.regex("^lihatabsenpulang$"))
async def lihat_absensi_pulang_callback(_, callback_query):
    grup_id = callback_query.message.chat.id
    if grup_id in absen_data:
        absensi_text = "Daftar Absensi Pulang:\n"
        for user_id, data in absen_data[grup_id]['absen_pulang'].items():
            absensi_text += f"{data['username']}: Pulang pada {data['pulang_time']}\n"
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
                ]
            ]
        )
        await callback_query.edit_message_text(absensi_text, reply_markup=keyboard)
    else:
        await callback_query.edit_message_text("Belum ada data absensi pulang.", reply_markup=None)

@app.on_callback_query(filters.regex("^resetabsensi$"))
async def reset_absensi_callback(_, callback_query):
    user_id = callback_query.from_user.id
    grup_id = callback_query.message.chat.id
    if grup_id in absen_data:
        if user_id in absen_data[grup_id]['absen_masuk']:
            del absen_data[grup_id]['absen_masuk'][user_id]
        if user_id in absen_data[grup_id]['absen_pulang']:
            del absen_data[grup_id]['absen_pulang'][user_id]
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Kembali", callback_data="kembali_absensi"),
            ]
        ]
    )
    await callback_query.edit_message_text("Absensi Anda berhasil direset.", reply_markup=keyboard)
# Fungsi callback lainnya ...

@app.on_callback_query(filters.regex("^kembali_absensi$"))
async def kembali_absensi_callback(_, callback_query):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Absen Masuk", callback_data="absenmasuk"),
                InlineKeyboardButton("Absen Pulang", callback_data="absenpulang"),
            ],
            [
                InlineKeyboardButton("Lihat Absensi Masuk", callback_data="lihatabsenmasuk"),
                InlineKeyboardButton("Lihat Absensi Pulang", callback_data="lihatabsenpulang"),
            ],
            [
                InlineKeyboardButton("Reset Absensi", callback_data="resetabsensi"),
            ]
        ]
    )
    await callback_query.edit_message_text("Silakan pilih opsi absensi:", reply_markup=keyboard)
