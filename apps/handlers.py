from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.enums.content_type import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.methods.get_file import GetFile
from aiogram.methods.send_chat_action import SendChatAction
import os
import json
import time
import PIL.Image
import google.generativeai as genai
from apps.keyboards import russian_english_keyboard as ru_en_kb
from apps.keyboards import change_lang as change_lang_keyboard

from dotenv import load_dotenv
load_dotenv()


try:
    
    genai.configure(api_key=os.getenv('gemini_token'))
except Exception as e:
    print(e)

# Конфигурация генерации
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 1000000,
}

# Настройки безопасности
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

try:
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
except Exception as e:
    json.dump({'error': str(e)}, open('server_log/log.json', 'w+'))

convo = model.start_chat(history=[])

router = Router()

@router.message(CommandStart)
async def start(message: Message):
    if not os.path.exists(f'accounts/' + message.from_user.full_name + '.json'):
        await message.answer(f'Hi, {message.from_user.full_name}', reply_markup=ru_en_kb)
    else:
        await message.answer(f'Hi, {message.from_user.full_name}')

@router.message(Command('change_current_language'))
async def change_language(message: Message):
    select_lang = json.load(open(f'accounts/' + message.from_user.full_name + '.json'))
    if select_lang[0]['lang'] == 'english':
        await message.answer('your language is english. Do you want to change your language to russian?', reply_markup=change_lang_keyboard)
    elif select_lang[0]['lang'] == 'russian':
        await message.answer(f'Ваш язык русский. Вы серьёзно хотите изменить его на английский?', reply_markup=change_lang_keyboard)

@router.callback_query(F.data)
async def answer(callback: CallbackQuery):
    try:
        select_lang = json.load(open(f'accounts/{callback.message.from_user.full_name}.json', 'r'))
    except:
        pass
    if callback.data == 'cancle':
        if select_lang[0]['lang'] == 'english':
            await callback.message.answer("Cancle")
        elif select_lang[0]['lang'] == 'russian':
            await callback.message.answer("Отмена")

    if callback.data == 'English_version':
        convo.send_message('you must speak english even if i speak russian. You cant speak russian')
        time.sleep(3)
        select_lang = [{'lang': 'english'}, {'name': callback.message.from_user.full_name}]
        await callback.message.answer("You have selected English version.")
        try:
            os.mkdir('accounts')
        except:
            pass
        json.dump(select_lang, open(f'accounts/{callback.message.from_user.full_name}.json', 'w+'))

    elif callback.data == 'Russian_version':
        convo.send_message('you must speak russian even if i speak english. You cant speak english')
        time.sleep(3)
        select_lang = [{'lang': 'russian'}, {'name': callback.message.from_user.full_name}]
        await callback.message.answer("Вы выбрали русскую версию.")
        try:
            os.mkdir('accounts')
        except:
            pass

    if callback.data == 'english_to_russian':
        if os.path.exists:
            os.remove(f'accounts/{callback.message.from_user.full_name}.json')
            json.dump([{"lang": "russian"}, {"name": callback.message.from_user.full_name}], open(f'accounts/{callback.message.from_user.full_name}.json', 'w+'))
            await callback.message.answer('Удачно')

    elif callback.data == 'russian_to_english':
        if os.path.exists:
            os.remove(f'accounts/{callback.message.from_user.full_name}.json')
            json.dump([{"lang": "english"}, {"name": callback.message.from_user.full_name}], open(f'accounts/{callback.message.from_user.full_name}.json', 'w+'))
            await callback.message.answer('Success')

@router.message(F.content_type == ContentType.DOCUMENT or F.content_type == ContentType.PHOTO)
async def user_media(message: Message):
    full_name = message.from_user.first_name + message.from_user.last_name
    select_lang = json.load(open(f'accounts/{full_name}.json', 'r'))
    if select_lang[0]['lang'] == 'english':
        convo.send_message('you must speak english even if i speak russian. You cant speak russian')
        time.sleep(3)

    elif select_lang[0]['lang'] == 'russian':
        convo.send_message('you must speak russian even if i speak english. You cant speak english')
        time.sleep(3)

    try:
        os.mkdir('photo_tg')
    except FileExistsError:
        pass

    try:
        photo_path = 'photo_tg/file.jpg'
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_info = await message.GetFile(file_id)
            downloaded_file = await message.download_file(file_info.file_path)

            with open(photo_path, 'wb') as new_file:
                new_file.write(downloaded_file)

        elif message.content_type == 'document':
            file_id = message.document.file_id
            file_info = await message.GetFile(file_id)
            downloaded_file = await message.download_file(file_info.file_path)

            with open(photo_path, 'wb') as new_file:
                new_file.write(downloaded_file)

        img = PIL.Image.open(photo_path)
        await message.SendChatAction(message.chat.id, action='typing')
        if message.caption:
            convo.send_message(message.caption)
            time.sleep(3)

        else:
            convo.send_message('Just watch this image')
            time.sleep(3)

        convo.send_message(img)

        await message.answer(convo.last.text)

        os.remove(photo_path)

    except Exception as e:
        pass

@router.message()
async def user_text(message: Message):
    select_lang = json.load(open(f'accounts/{message.from_user.full_name}.json', 'r'))

    try:
        if select_lang[0]['lang'] == 'english':
            convo.send_message('you must speak english even if i speak russian. You cant speak russian')
            time.sleep(3)
            await message.send_chat_action(message.chat.id, action='typing')
            convo.send_message(message.text)
            await message.answer(convo.last.text)

        elif select_lang[0]['lang'] == 'russian':
            convo.send_message('you must to speak russian even if i speak english. You cant speak english')
            time.sleep(3)
            await message.send_chat_action(message.chat.id, action='typing')
            convo.send_message(message.text)
            await message.answer(convo.last.text)

    except Exception as e:
        await message.answer(f'Try again! {e}')
        json.dump({'error': str(e)}, open('server_log/log.json', 'w+'))
