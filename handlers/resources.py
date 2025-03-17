import datetime
import pprint
import bson
from math import ceil
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

resource_types = {
    "components" : "⚙️ Компоненты",
    "recipes" : "📑 Рецепты",
    "drugs" : "💉 Препараты",
    "kits" : "🔭 Обвесы",
    "quests" : "📜 Квестовые",
    "other" : "📦 Прочее"
}

@router.message(F.text == '🎒Инвентарь')
async def handler_hero_resources(message: Message, state: FSMContext):
    kb = []
    for i in resource_types:
      kb.append([InlineKeyboardButton(text=resource_types[i], callback_data=f'get_{i}_1')])
      
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    hero = await Db.get_hero_by_telegram_id(telegram_id=message.chat.id)
    image = create_image(hero['equipped'])
    
    await message.answer_photo(BufferedInputFile(image.read(), "image.png"), caption='🎒 Инвентарь', reply_markup=keyboard)
    

@router.callback_query(F.data.startswith('get_'))
async def handler_get_hero_resources(callback: CallbackQuery, state: FSMContext):
    resource_type = callback.data.split("_")[1]
    page = int(callback.data.split("_")[-1])
    max_count_pages = 8
    
    text = f"<b>{resource_types[resource_type]}</b>"
    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    resources = hero['resources']
    resource_datas = await Db.get_resources(list(resources.keys()))
    
    resource_datas_current_type = []
    
    for i in resource_datas:
        type_name = resource_types[resource_type].split(" ")[1].lower()
        if type_name in i["type"]:
            resource_datas_current_type.append(i)
    
    max_idx = len(resource_datas_current_type)
        
    kb = [
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='hero_resources')]
    ]
    
    if max_idx == 0:
        text += "\n\nРесурсов данного типа нет."
    else:
        max_page = ceil(max_idx / 8)
        
        current_idx = (page - 1) * 8

        if current_idx + 8 < max_page * 8:
            max_page_idx = current_idx + 8
        else:
            max_page_idx = max_idx

        resource_datas_current_type = resource_datas_current_type[current_idx : max_page_idx]
            
        for i in resource_datas_current_type:
            text += f"\n\n<b>{i['name']}</b> - {resources[str(i['_id'])]} шт."
            
        text += f"\n\n<b>Страница ({page}/{max_page})</b>"
        
        change_page_button = []
        
        if page > 1:
            change_page_button.append(InlineKeyboardButton(text='◀️', callback_data=f'get_{resource_type}_{page - 1}'))
        if page < max_page:
            change_page_button.append(InlineKeyboardButton(text='▶️', callback_data=f'get_{resource_type}_{page + 1}'))
            
            
        if len(change_page_button) > 0:
            kb.insert(0, change_page_button)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_caption(
                               caption=text,
                               reply_markup=keyboard,
                               parse_mode="html")
                               
@router.callback_query(F.data.startswith('hero_resources'))
async def handler_back_hero_resources(callback: CallbackQuery, state: FSMContext):
    await handler_hero_resources(callback.message, state)

