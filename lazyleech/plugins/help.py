import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .. import ALL_CHATS, help_dict
from ..utils import custom_filters

@Client.on_message(filters.command('helpleech') & filters.chat(ALL_CHATS))
async def help_cmd(client, message):
    module = message.text.split(' ', 1)
    module.pop(0)
    try:
        module = module[0].lower().strip()
    except IndexError:
        module = None
    for internal_name in help_dict:
        external_name, text = help_dict[internal_name]
        external_name = external_name.lower().strip()
        internal_name = internal_name.lower().strip()
        if module in (internal_name, external_name):
            buttons = [
                [InlineKeyboardButton('⬅', 'help_back')]
            ]
            break
    else:
        module = None
        text = 'module you want help with?'
        buttons = []
        to_append = []
        for internal_name in help_dict:
            external_name, _ = help_dict[internal_name]
            to_append.append(InlineKeyboardButton(external_name.strip(), f'help_m{internal_name}'))
            if len(to_append) > 2:
                buttons.append(to_append)
                to_append = []
        if to_append:
            buttons.append(to_append)
    reply = await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    callback_info[(reply.chat.id, reply.message_id)] = message.from_user.id, module

callback_lock = asyncio.Lock()
callback_info = dict()
@Client.on_callback_query(custom_filters.callback_data('help_back') & custom_filters.callback_chat(ALL_CHATS))
async def help_back(client, callback_query):
    message = callback_query.message
    message_identifier = (message.chat.id, message.message_id)
    if message_identifier not in callback_info:
        await callback_query.answer('❌ This help message is too old that I don\'t have info on it.', show_alert=True, cache_time=3600)
        return
    async with callback_lock:
        info = callback_info.get((message.chat.id, message.message_id))
        user_id, location = info
        if user_id != callback_query.from_user.id:
            await callback_query.answer('...no', cache_time=3600)
            return
        if location is not None:
            buttons = []
            to_append = []
            for internal_name in help_dict:
                external_name, _ = help_dict[internal_name]
                to_append.append(InlineKeyboardButton(external_name.strip(), f'help_m{internal_name}'))
                if len(to_append) > 2:
                    buttons.append(to_append)
                    to_append = []
            if to_append:
                buttons.append(to_append)
            await message.edit_text('module you want help with?', reply_markup=InlineKeyboardMarkup(buttons))
            callback_info[message_identifier] = user_id, None
    await callback_query.answer()

@Client.on_callback_query(filters.regex('help_m.+') & custom_filters.callback_chat(ALL_CHATS))
async def help_m(client, callback_query):
    message = callback_query.message
    message_identifier = (message.chat.id, message.message_id)
    if message_identifier not in callback_info:
        await callback_query.answer('❌ This help message is too old that I don\'t have info on it.', show_alert=True, cache_time=3600)
        return
    async with callback_lock:
        info = callback_info.get((message.chat.id, message.message_id))
        user_id, location = info
        if user_id != callback_query.from_user.id:
            await callback_query.answer('...no', cache_time=3600)
            return
        module = callback_query.data[6:]
        if module not in help_dict:
            await callback_query.answer('😅 What module?')
            return
        if module != location:
            await message.edit_text(help_dict[module][1], reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⬅', 'help_back')]
            ]))
            callback_info[message_identifier] = user_id, module
    await callback_query.answer()
