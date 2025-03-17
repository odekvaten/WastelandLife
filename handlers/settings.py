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


@router.message(F.text == '⚙️Настройки')
async def handler_settings(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    kb = [
        [KeyboardButton(text='Ежедневные награды'),
         KeyboardButton(text='Магазин')],
        [KeyboardButton(text='Рефералы'),
         KeyboardButton(text='Прочее')],
        [KeyboardButton(text='⬅️Вернуться')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer_photo(FSInputFile('./images/start_location.png'),
                               caption='Настройки',
                               reply_markup=keyboard)
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == 'Ежедневные награды')
async def handler_settings_everyday(message: Message, state: FSMContext):
    loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.callback_query(F.text == 'Магазин')
async def handler_settings_store(message: Message, state: FSMContext):
    loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.callback_query(F.text == 'Рефералы')
async def handler_settings_referrals(message: Message, state: FSMContext):
    loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.callback_query(F.text == 'Прочее')
async def handler_settings_others(message: Message, state: FSMContext):
    loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
