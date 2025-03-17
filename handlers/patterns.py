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


@router.message(F.text == '🧬Характеристики')
async def handler_hero_patterns(message: Message, state: FSMContext):

    kb = [
        [InlineKeyboardButton(text="🧬Повысить характеристики", callback_data=f'upgrade_patterns_0')]
    ]
    hero = await Db.get_hero_by_telegram_id(message.chat.id)
    text = get_caption(message, hero)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    image = create_image(hero['equipped'])
                        
    await message.answer_photo(BufferedInputFile(image.read(), "image.png"), caption=text, reply_markup=keyboard, parse_mode="html")
    
                               

@router.callback_query(F.data.startswith('upgrade_patterns'))
async def handler_upgrade_hero_patterns(callback: CallbackQuery, state: FSMContext):
    kb = [
        [InlineKeyboardButton(text='🏋️ Сила ➕ 1', callback_data='upgrade_patterns_1')],
        [InlineKeyboardButton(text='🏃 Выносливость ➕ 1', callback_data='upgrade_patterns_2')],
        [InlineKeyboardButton(text='🤸 Ловкость ➕ 1', callback_data='upgrade_patterns_3')],
        [InlineKeyboardButton(text='🤺 Меткость ➕ 1', callback_data='upgrade_patterns_4')],
        [InlineKeyboardButton(text='🏌️ Удача ➕ 1', callback_data='upgrade_patterns_5')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='hero_patterns')]
    ]
    patterns = int(callback.data.split("_")[-1])
    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    if patterns != 0:
        if patterns == 1:
            hero['patterns']['strength'] += 1
        elif patterns == 2:
            hero['patterns']['endurance'] += 1
        elif patterns == 3:
            hero['patterns']['agility'] += 1
        elif patterns == 4:
            hero['patterns']['accuracy'] += 1
        elif patterns == 5:
            hero['patterns']['luck'] += 1
            
        if hero['patterns']['points'] >= 1:
            hero['patterns']['points'] -= 1
            await Db.update_hero(hero['_id'], hero)
        else:
            await bot.answer_callback_query(callback.id, f"У вас нет свободных очков параметров!", show_alert=True)
            return
            
        
    text = get_caption(callback.message, hero)
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_caption(
                               caption=text,
                               reply_markup=keyboard,
                               parse_mode="html")
                               

@router.callback_query(F.data.startswith('hero_patterns'))
async def handler_back_hero_patterns(callback: CallbackQuery, state: FSMContext):
    await handler_hero_patterns(callback.message, state)
    
    
def get_caption(message, hero):
    patterns = hero["patterns"]
    text = f"<b>🧬 Характеристики</b>\n\n👮 {hero['nickname']} 🔷{hero['level']} ({hero['hp_free']}/{hero['hp']})\n💹 Опыт: ({hero['experience']}/{Db.get_levels()[hero['level']]})\n\n<b>🏋️ Сила: {patterns['strength']}</b>\n<b>🏃 Выносливость: {patterns['endurance']}</b>\n<b>🤸Ловкость: {patterns['agility']}</b>\n<b>🤺 Меткость: {patterns['accuracy']}</b>\n<b>🏌️ Удача: {patterns['luck']}</b>\n\nСвободных очков параметров: {hero['patterns']['points']}"
    
    return text

