import datetime
import pprint
import bson
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot import bot
from db.db_requests import Db
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import os
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

router = Router()

storage = MemoryStorage()


@router.message(F.text == '🏭Фабрики')
async def handler_fabrics(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    kb = [
        [KeyboardButton(text='💧Колодец'),
         KeyboardButton(text='🧅Огород')],
        [KeyboardButton(text='⬅️Вернуться')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    await message.answer_photo(FSInputFile('./images/start_location.png'),
                               caption='Фабрики',
                               reply_markup=keyboard)
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == '💧Колодец')
async def handler_fabrics_kolodec(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == '🧅Огород')
async def handler_fabrics_ogorod(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
