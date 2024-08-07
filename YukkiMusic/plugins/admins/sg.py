import asyncio
import random

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory

from YukkiMusic import userbot as us, app
from YukkiMusic.core.userbot import assistants

@app.on_message(filters.command("sg"))
async def sg(client: Client, message: Message):
    if len(message.text.split()) < 2 and not message.reply_to_message:
        return await message.reply("Harap berikan username/id atau balas pesan.")
    if message.reply_to_message:
        args = message.reply_to_message.from_user.id
    else:
        args = message.text.split()[1]
    lol = await message.reply("👀")
    if args:
        try:
            user = await client.get_users(f"{args}")
        except Exception:
            return await lol.edit("<code>Harap berikan pengguna yang valid!</code>")
    bo = ["sangmata_bot", "sangmata_beta_bot"]
    sg = random.choice(bo)
    if 1 in assistants:
        ubot = us.one
    
    try:
        a = await ubot.send_message(sg, f"{user.id}")
        await a.delete()
    except Exception as e:
        return await lol.edit(str(e))
    await asyncio.sleep(1)
    
    async for stalk in ubot.search_messages(a.chat.id):
        if not stalk.text:
            continue
        if not stalk:
            await message.reply("Botnya ngambek.")
        else:
            await message.reply(stalk.text)
            break  # Keluar dari loop setelah menampilkan satu pesan
    
    try:
        user_info = await ubot.resolve_peer(sg)
        await ubot.send(DeleteHistory(peer=user_info, max_id=0, revoke=True))
    except Exception:
        pass
    
    await lol.delete()
