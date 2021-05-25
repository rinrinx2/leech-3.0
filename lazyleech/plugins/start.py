from pyrogram import Client, filters
from .. import ALL_CHATS

@Client.on_message(filters.command('start') & filters.chat(ALL_CHATS))
async def start(client, message):
    await message.reply_text('✅ working')
    