import datetime
import pprint
import bson
from math import ceil
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile, InputMediaPhoto
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


@router.message(F.text == '🔫Снаряжение')
async def handler_hero_equipped(message: Message, state: FSMContext, is_edit = False):
    #loader = await message.answer('Загрузка...')
    hero = await Db.get_hero_by_telegram_id(telegram_id=message.chat.id)
    
    
    dict_equipment_types = {
        '🔫 огнестрельное' : 'gun_1',
        '☄️ патроны' : 'patrons',
        '🪓 холодное' : 'cold_gun_1',
        '💉 стимуляторы' : 'pocket',
        '🦺 броня' : 'armor',
        '🪖 шлем': 'helmet'
    }
    equipment_count = {
        "gun_1" : 0,
        "patrons" : 0,
        "cold_gun_1" : 0,
        "pocket" : 0,
        "armor" : 0,
        "helmet" : 0
    }
    
    
    for gun_type in dict_equipment_types:
        count = await Db.get_player_equipments(hero['_id'], gun_type)
        equipment_count[dict_equipment_types[gun_type]] = len(count)
        
    gun_1_text = f'({equipment_count["gun_1"]})'
    gun_2_text = f'({equipment_count["gun_1"]})'
    patrons_text = f'({equipment_count["patrons"]})'
    cold_gun_1_text = f'({equipment_count["cold_gun_1"]})'
    pocket_text = f'({equipment_count["pocket"]})'
    armor_text = f'({equipment_count["armor"]})'
    helmet_text = f'({equipment_count["helmet"]})'
 
    kb = [
        [InlineKeyboardButton(text=f'🔫Основное оружие {gun_1_text}', callback_data='equipped:gun_1'),
        InlineKeyboardButton(text=f'🔫Запасное оружие {gun_2_text}', callback_data='equipped:gun_2')],
        [InlineKeyboardButton(text=f'🔪Холодное оружие {cold_gun_1_text}', callback_data='equipped:cold_gun_1'),
        InlineKeyboardButton(text=f'☄️Патроны {patrons_text}', callback_data='equipped:patrons')],
        [InlineKeyboardButton(text=f'🦺Тело {armor_text}', callback_data='equipped:armor'),
         InlineKeyboardButton(text=f'🪖Голова {helmet_text}', callback_data='equipped:helmet')],
        [InlineKeyboardButton(text=f'💼Подсумок {pocket_text}', callback_data='equipped:pocket')]
    ]
    image = create_image(hero['equipped'])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    if is_edit:
        await message.edit_media(InputMediaPhoto(media=BufferedInputFile(image.read(), "image.png"), caption='Снаряжение'), reply_markup=keyboard)
    
    else:
        await message.answer_photo(BufferedInputFile(image.read(), "image.png"),
                                   caption='Снаряжение',
                                   reply_markup=keyboard)
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.callback_query(F.data == '🔫Снаряжение')
async def handler_hero_equipped_callback(callback: CallbackQuery, state: FSMContext):

    await handler_hero_equipped(callback.message, state, True)


@router.callback_query(F.data.startswith('equipped:'))
async def handler_hero_equipped_data_callback(callback: CallbackQuery, state: FSMContext, equipped_type_callback=''):
    dict_equipment_types = {
        'gun_1' : '🔫 огнестрельное',
        'gun_2' : '🔫 огнестрельное',
        'patrons' : '☄️ патроны',
        'cold_gun_1' : '🪓 холодное',
        'pocket' : '💉 стимуляторы',
        'armor' : '🦺 броня',
        'helmet' : '🪖 шлем'
    }
    
    if equipped_type_callback:
        equipped_type = equipped_type_callback
    else:
        equipped_type = callback.data.split(':')[1]
        
    page = 1
    
    if len(callback.data.split(':')) > 2:
        page = int(callback.data.split(':')[2])
    
    equipped_type_text = ''
    if equipped_type == 'gun_1':
        equipped_type_text = '🔫Основное оружие'
    elif equipped_type == 'gun_2':
        equipped_type_text = '🔫Запасное оружие'
    elif equipped_type == 'patrons':
        equipped_type_text = '☄️Патроны'
    elif equipped_type == 'cold_gun_1':
        equipped_type_text = '🔪Холодное оружие'
    elif equipped_type == 'pocket':
        equipped_type_text = '💼Подсумок'
    elif equipped_type == 'armor':
        equipped_type_text = '🦺Тело'
    elif equipped_type == 'helmet':
        equipped_type_text = '🪖Голова'
        
    hero = await Db.get_hero_by_telegram_id(telegram_id=callback.from_user.id)
    
    hero_equipments = await Db.get_player_equipments(hero['_id'], dict_equipment_types[equipped_type])

    kb = []
    amount = 0
    
    max_page = ceil(len(hero_equipments) / 10)
    
    current_idx = (page - 1) * 10

    if current_idx + 10 < max_page * 10:
        max_page_idx = current_idx + 10
    else:
        max_page_idx = len(hero_equipments)

    change_page_button = []
    
    if page > 1:
        change_page_button.append(InlineKeyboardButton(text='◀️', callback_data=f'equipped:{equipped_type}:{page - 1}'))
    if page < max_page:
        change_page_button.append(InlineKeyboardButton(text='▶️', callback_data=f'equipped:{equipped_type}:{page + 1}'))

    for equipment in hero_equipments[current_idx:max_page_idx]:
        if hero.get('equipped').get(equipped_type) != None:
            if str(equipment['_id']) == str(hero.get('equipped').get(equipped_type)):
                is_equipped = '✅'
                if equipment["equipments"].get("type") == "☄️ патроны":
                    kb.append([InlineKeyboardButton(text=f'{is_equipped} {equipment["equipments"].get("name")} ({equipment.get("count")})', callback_data=f'get_equipped:{str(equipment.get("_id"))}:{equipped_type}:0')])
                else:
                    kb.append([InlineKeyboardButton(text=f'{is_equipped} {equipment["equipments"].get("name")} ({equipment.get("solidity_free")}/{equipment.get("max_solidity")})', callback_data=f'get_equipped:{str(equipment.get("_id"))}:{equipped_type}:0')])
                amount += 1
                continue
                
        if str(equipment['_id']) == str(hero.get('equipped').get("gun_1")) or str(equipment['_id']) == str(hero.get('equipped').get("gun_2")):
            continue

        is_equipped = '❌'
        if equipment["equipments"].get("type") == "☄️ патроны":
            kb.append([InlineKeyboardButton(text=f'{is_equipped} {equipment["equipments"].get("name")} ({equipment.get("count")})', callback_data=f'get_equipped:{str(equipment.get("_id"))}:{equipped_type}:1')])
        else:
            kb.append([InlineKeyboardButton(text=f'{is_equipped} {equipment["equipments"].get("name")} ({equipment.get("solidity_free")}/{equipment.get("max_solidity")})', callback_data=f'get_equipped:{str(equipment.get("_id"))}:{equipped_type}:1')])
                
        amount += 1
    
    if len(change_page_button) > 0:
        kb.append(change_page_button)
        
    kb.append([InlineKeyboardButton(text=f'⬅️ Назад', callback_data='🔫Снаряжение')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    if amount > 0:
        await callback.message.edit_caption(caption=f'{equipped_type_text} - текущее снаряжение в инвентаре', reply_markup=keyboard)
    else:
        await callback.message.edit_caption(caption=f'{equipped_type_text} - отсутствует снаряжение в инвентаре', reply_markup=keyboard)
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
    # else:
    #     print(2)
    #     kb = [[InlineKeyboardButton(text=f'⬅️Назад', callback_data='🔫Снаряжение')]]
    #     keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    #     await callback.message.answer_photo(FSInputFile('./images/start_location.png'),
    #                                         caption=f'{equipped_type_text} - отсутствует снаряжение в инвентаре',
    #                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('set_equipped:'))
async def handler_set_equipped(callback: CallbackQuery, state: FSMContext):
    #loader = await callback.message.answer('Загрузка...')
    equipped_id = callback.data.split(':')[-1]
    equipped_type = callback.data.split(':')[-2]
    hero = await Db.get_hero_by_telegram_id(telegram_id=callback.from_user.id)
    hero['equipped'][equipped_type] = bson.ObjectId(equipped_id)
    await Db.update_hero(hero['_id'], hero)
    
    callback_data = f"get_equipped:{equipped_id}:{equipped_type}:0"
    await handler_get_equipped(callback, state, callback_data)



@router.callback_query(F.data.startswith('unset_equipped:'))
async def handler_unset_equipped(callback: CallbackQuery, state: FSMContext):
    equipped_id = callback.data.split(':')[-1]
    equipped_type = callback.data.split(':')[-2]
    hero = await Db.get_hero_by_telegram_id(telegram_id=callback.from_user.id)
    hero['equipped'][equipped_type] = {}
    await Db.update_hero(hero['_id'], hero)
    callback_data = f"get_equipped:{equipped_id}:{equipped_type}:1"
    await handler_get_equipped(callback, state, callback_data)
    
    
@router.callback_query(F.data.startswith('delete_equipment:'))
async def handler_unset_equipped(callback: CallbackQuery, state: FSMContext):
    equipped_id = callback.data.split(':')[-1]
    equipped_type = callback.data.split(':')[-2]
    hero = await Db.get_hero_by_telegram_id(telegram_id=callback.from_user.id)
    if str(hero['equipped'][equipped_type]) == str(equipped_id):
        hero['equipped'][equipped_type] = {}
        await Db.update_hero(hero['_id'], hero)
    
    await Db.delete_player_equipments(equipped_id)
    await handler_hero_equipped(callback.message, state, True)

    
@router.callback_query(F.data.startswith('get_equipped:'))
async def handler_get_equipped(callback: CallbackQuery, state: FSMContext, callback_data = None):
    #loader = await callback.message.answer('Загрузка...')
    if not callback_data:
        callback_data = callback.data
        
    equipped_id = callback_data.split(':')[-3]
    equipped_type = callback_data.split(':')[-2]
    equipped_status = int(callback_data.split(':')[-1])
    
    hero = await Db.get_hero_by_telegram_id(telegram_id=callback.message.chat.id)
    
    equipment = await Db.get_player_equipments(hero['_id'], equipment_id  = equipped_id)
    
    equipment = equipment[0]
    
    
    
    text = f"<b>{equipment['equipments']['name']}\n\nТребования:\nУровень - 🔷 {equipment['equipments']['level']}"
    
    if equipment['equipments']['strenght'] != None:
        text += "\n🏋️Сила - " + str(equipment['equipments']['strenght'])
    if equipment['equipments']['endurance'] != None:
        text += "\n🏃Выносливость - " + str(equipment['equipments']['endurance'])
    if equipment['equipments']['dexterity'] != None:
        text += "\n🤸Ловкость - " + str(equipment['equipments']['dexterity'])
    if equipment['equipments']['accuracy'] != None:
        text += "\n🤺Меткость - " + str(equipment['equipments']['accuracy'])
    if equipment['equipments']['luck'] != None:
        text += "\n🏌️Удача - " + str(equipment['equipments']['luck'])
        
    text += "\n\nХарактеристики:"
    
    if equipment['equipments']['type'] == "🔫 огнестрельное" or equipment['equipments']['type'] == "🪓 холодное":
        text += "\n☄️Урон - " + str(equipment['equipments']['weaponDamage'])
        if equipment['equipments']['type'] == "🔫 огнестрельное":
            text += "\n↔️Дистанция - " + str(equipment['equipments']['distanceModifier'])
        text += "\n💥Крит - " + str(equipment['equipments']['criticalDamagePower'])
        
    elif equipment['equipments']['type'] == "🦺 броня" or equipment['equipments']['type'] == "🪖 шлем" or equipment['equipments']['type'] == "💉 стимуляторы":
        text += "\n🛡Броня - " + str(equipment['equipments']['armor'])
    
    criticalDamageProbability = None
    
    if equipment['equipments']['type'] == "🔫 огнестрельное" or equipment['equipments']['type'] == "🪓 холодное":
        criticalDamageProbability = "низкий"
        if equipment['equipments']['criticalDamageProbability'] > 50 and equipment['equipments']['criticalDamageProbability'] <= 100:
            criticalDamageProbability = "средний"
        elif equipment['equipments']['criticalDamageProbability'] > 100:
            criticalDamageProbability = "высокий"
            
    elif equipment['equipments']['type'] == "💉 стимулятор":
        criticalDamageProbability = "пониженный"
        if equipment['equipments']['criticalDamageProbability'] >= 0:
            criticalDamageProbability = "повышенный"
            
    if criticalDamageProbability:
        text += "\n🎲Шанс крита - " + criticalDamageProbability


    if equipment['equipments']['type'] != "💉 стимулятор" and equipment['equipments']['type'] != "☄️ патроны":
        text += f"\n\n⚙️ {equipment['solidity_free']}/{equipment['max_solidity']}"
        
    if equipment['equipments']['type'] == "☄️ патроны":
        text += f"\n\nКоличество: {equipment['count']}"
        
    text += "</b>"
    
    
    kb = []
    
    if equipped_status == 1:
        kb.append([InlineKeyboardButton(text=f'Экипировать', callback_data=f'set_equipped:{equipped_type}:{str(equipment.get("_id"))}')])
    else:
        kb.append([InlineKeyboardButton(text=f'Снять', callback_data=f'unset_equipped:{equipped_type}:{str(equipment.get("_id"))}')])
    kb.append([InlineKeyboardButton(text=f'Улучшить', callback_data='upgrade_equipment')])
    kb.append([InlineKeyboardButton(text=f'Выкинуть', callback_data=f'delete_equipment:{equipped_type}:{str(equipment.get("_id"))}')])
    kb.append([InlineKeyboardButton(text=f'⬅️ Назад', callback_data='🔫Снаряжение')])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    


    image = create_image(hero['equipped'])
    await callback.message.edit_media(InputMediaPhoto(media=BufferedInputFile(image.read(), "image.png"), caption=text, parse_mode = "html"), reply_markup=keyboard)
    
    
    #await handler_hero_equipped_data_callback(callback=callback, state=state, equipped_type_callback=equipped_type)
