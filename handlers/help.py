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


@router.message(F.text == '📚Помощь')
async def handler_help(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    kb = [
        [KeyboardButton(text='Гайды'),
         KeyboardButton(text='Поддержка')],
        [KeyboardButton(text='Правила'),
         KeyboardButton(text='База знаний')],
        [KeyboardButton(text='⬅️Вернуться')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer_photo(FSInputFile('./images/start_location.png'),
                               caption='Помощь',
                               reply_markup=keyboard)
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == 'Гайды')
async def handler_help_everyday(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == 'Поддержка')
async def handler_help_everyday(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == 'Правила')
async def handler_help_everyday(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.message(F.text == 'База знаний')
async def handler_help_everyday(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    await message.answer('Блок находится в разработке...')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)

