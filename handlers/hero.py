import datetime
import pprint
import bson
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot import bot
from db.db_requests import Db
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import os
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from equipment_image_creator.equipment_image_creator import create_image


router = Router()

storage = MemoryStorage()


@router.message(F.text == '👨‍🎤Персонаж')
async def handler_hero(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    kb = [
        [KeyboardButton(text='🎒Инвентарь'),
         KeyboardButton(text='🧬Характеристики')],
        [KeyboardButton(text='🔫Снаряжение'),
         KeyboardButton(text='📔Навыки')],
        [KeyboardButton(text='⬅️Вернуться')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    
    hero = await Db.get_hero_by_telegram_id(telegram_id=message.chat.id)
    
    image = create_image(hero['equipped'])
    
    text = f"Персонаж:\n\n👮 {hero['nickname']} 🔷{hero['level']} ({hero['hp_free']}/{hero['hp']})\n☄️ Патроны - {hero['money']}\n💹 Опыт - ({hero['experience']}/{Db.get_levels()[hero['level']]})"
                        
    await message.answer_photo(BufferedInputFile(image.read(), "image.png"), caption=text, reply_markup=keyboard)

