import asyncio
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
from handlers.main import go_to_location, TransferState


router = Router()

storage = MemoryStorage()


@router.message(F.text == '🗺Карта')
async def handler_map(message: Message, state: FSMContext):
    await state.clear()
    user = await Db.get_user_with_location(telegram_id=message.from_user.id)
    kb = []
    locations_ids = user.get('location').get('nearest_locations')
    locations = await Db.get_locations_info(ids=locations_ids)

    for j, i in enumerate(locations):
        if j % 2 == 0:
            kb.append([KeyboardButton(text=f'{i.get("name")}')])
        else:
            kb[j // 2].append(KeyboardButton(text=f'{i.get("name")}'))

    kb.append([KeyboardButton(text='⬅️Вернуться')])
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    await message.answer_photo(FSInputFile('./images/start_location.png'),
                               caption='Карта',
                               reply_markup=keyboard)
                               
    await state.set_state(TransferState.transferLocation)
    

@router.message(TransferState.transferLocation)
async def transfer_to_location(message: Message, state: FSMContext):
    location = await Db.get_location_by_name(message.text)
    hero = await Db.get_hero_by_telegram_id(message.from_user.id)
    if hero['level'] < location['min_level']:
        await message.answer(f'Переход в локацию возможен после достижения <b>{location["min_level"]}</b> уровня.', parse_mode = "html")
        return
    elif str(location['request_quests']) != "":
        if type(location['request_quests']) is str:
            location['request_quests'] = [location['request_quests']]
        
        if len(location['request_quests']) > 0:
            taked_quests = await Db.get_taked_quest(location['request_quests'], "quest_id", {"hero_id" : hero["_id"]})
            if len(taked_quests) <= len(location['request_quests']):
                await message.answer(f'Переход в локацию возможен после выполнения обязательных квестов.', parse_mode = "html")
                return
    
    loader = await message.answer('Переход к локации...')
    await state.clear()
    await asyncio.sleep(5)
    await Db.update_location(hero_telegram_id=message.from_user.id, location_name=message.text)
    await go_to_location(message=message, state=state)
    await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
