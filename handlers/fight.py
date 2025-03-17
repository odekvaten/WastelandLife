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


class FightState(StatesGroup):
    fight = State()
    attack = State()
    evasion = State()


@router.message(F.text == '⚔️Найти противника')
async def handler_fight(message: Message, state: FSMContext):
    hero_telegram_id = message.from_user.id
    is_available_fight = await Db.is_fight_available(telegram_id=hero_telegram_id)
    if not is_available_fight:
        await message.answer('Недостаточно hp. Попробуйте позже...')
        return

    loader = await message.answer('Поиск противника...')
    fight = await Db.find_fight(telegram_id=hero_telegram_id)
    await state.update_data(fight=fight)
    await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
    kb = [


        [KeyboardButton(text='↖️Атаковать левее'),
         KeyboardButton(text='↗️Атаковать правее')],
        [KeyboardButton(text='⬆️Атаковать по центру')],
        [KeyboardButton(text='🏃Сбежать')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    if fight.get('type') == 'bot':
        try:
            await message.answer_photo(FSInputFile(fight.get("hero_2").get("image")),
                                   caption=f'Вы встретили "{fight.get("hero_2").get("name")}"\n\n{fight.get("hero_2").get("about")}',
                                   reply_markup=keyboard)
        except:                       
            await message.answer(f'Вы встретили "{fight.get("hero_2").get("name")}"\n\n{fight.get("hero_2").get("about")}')

    await message.answer(f'Между вами {fight.get("meters")} метров', reply_markup=keyboard)
    await message.answer(f'Выберите куда атаковать', reply_markup=keyboard)

@router.message(F.text == '↖️Атаковать левее')
@router.message(F.text == '↗️Атаковать правее')
@router.message(F.text == '⬆️Атаковать по центру')
async def handler_fight_attack(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if not state_data.get('fight'):
        return
    meters_message = state_data.get('meters_message')
    kb = [
        [KeyboardButton(text='↖️Увернуться левее'),
         KeyboardButton(text='↗️Увернуться правее')],
        [KeyboardButton(text='⬆️Остаться по центру')],
        [KeyboardButton(text='🏃Сбежать')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    await message.answer(f'Выберите куда увернуться', reply_markup=keyboard)
    attack = ''
    if message.text == '↖️Атаковать левее':
        attack = 'left'
    elif message.text == '↗️Атаковать правее':
        attack = 'right'
    elif message.text == '↗️Атаковать по центру':
        attack = 'center'
    await state.update_data(attack=attack)


@router.message(F.text == '🏃Сбежать')
async def handler_escape(message: Message, state: FSMContext):
    state_data = await state.get_data()
    fight = state_data.get('fight')
    attack = state_data.get('attack')
    if not fight:
        kb = [[KeyboardButton(text='⬅️Вернуться')]]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
        await message.answer(text = 'Бой завершен!', reply_markup = keyboard)
        return
        
    hero = await Db.get_hero_by_telegram_id(message.chat.id)
    kb = [
            [KeyboardButton(text='⬅️Вернуться')]
        ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    await state.clear()
    await message.answer(f'💔 <b>Победил противник</b>', reply_markup=keyboard, parse_mode = 'html')
         

    for equipment in hero['equipped'].keys():
        equipment_id = hero['equipped'][equipment].get("_id")
        if equipment_id:
            current_equipment = await Db.get_player_equipments(hero["_id"], equipment_id = equipment_id)
            if len(current_equipment) > 0:
                current_equipment = current_equipment[0]
                if current_equipment["equipments"].get("type") != "☄️ патроны":
                    current_equipment.pop("equipments")
                    current_equipment['solidity_free'] -= 1
                    if current_equipment['solidity_free'] <= 0:
                        hero['equipped'][equipment] = {}
                        await Db.delete_player_equipments(equipment_id)
                    else:
                        await Db.update_player_equipments(current_equipment['_id'], current_equipment)
            
            fight = await Db.find_action(fight.get('_id'), message.chat.id, "", "", only_fight = True)
            hero_1_hp_free = fight['hero_1']['hp_free']
            hero['hp_free'] = hero_1_hp_free    
        
        
        
        

@router.message(F.text == '↖️Увернуться левее')
@router.message(F.text == '↗️Увернуться правее')
@router.message(F.text == '⬆️Остаться по центру')
async def handler_fight_attack(message: Message, state: FSMContext):

    if message.text == '↖️Увернуться левее':
        evasion = 'left'
    elif message.text == '↗️Увернуться правее':
        evasion = 'right'
    elif message.text == '⬆️Остаться по центру':
        evasion = 'center'

    state_data = await state.get_data()
    fight = state_data.get('fight')
    attack = state_data.get('attack')
    if not fight:
        kb = [[KeyboardButton(text='⬅️Вернуться')]]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
        await message.answer(text = 'Бой завершен!', reply_markup = keyboard)
        return

    result = await Db.find_action(fight_id=fight.get('_id'), user_telegram_id=message.from_user.id, attack_type=attack, evasion_type=evasion)

    print(result)

    await state.update_data(fight=result)

    round_result = result.get('rounds')[fight.get('round_num') - 1]

    name_type_attacks = {'left' : 'влево', 'right' : 'вправо', 'center' : 'прямо'}
    
    hero_1_name = result['hero_1']['name']
    hero_1_result = round_result.get('hero_1_attack_status')
    hero_1_attack = round_result.get('hero_1_attack')
    hero_1_hp = result['hero_1']['hp']
    hero_1_hp_free = result['hero_1']['hp_free']
    hero_1_hits = result['hero_1']['hits']
    hero_1_misses = result['hero_1']['misses']
    hero_1_dodge_count = result['hero_1']['dodge_count']
    hero_1_crytical_damage_count = result['hero_1']['crytical_damage_count']
    hero_1_crytical_damage_status = round_result['hero_1_crytical_damage_status']
    hero_1_dodge_status = round_result['hero_1_dodge_status']
    hero_1_can_shoot = round_result['hero_1_can_shoot']
    
    if round_result.get('hero_1_attack_type'):
        hero_1_type_attacks = name_type_attacks[round_result['hero_1_attack_type']]
    else:
        hero_1_type_attacks = 'прямо'
    
    if hero_1_can_shoot:
        if hero_1_result:
            hero_1_text = f'👨‍🏭 {hero_1_name}🔸1 ❤️{hero_1_hp_free}/{hero_1_hp} атакует <b>{hero_1_type_attacks}</b> и <b>попадает</b>'
            if hero_1_crytical_damage_status:
                hero_1_text += " <b>нанося критический урон</b>"
        else:
            hero_1_text = f'👨‍🏭 {hero_1_name}🔸1 ❤️{hero_1_hp_free}/{hero_1_hp} атакует <b>{hero_1_type_attacks}</b> и <b>промахивается</b>'
            hero_1_attack = 0
    else:
        hero_1_text = f'👨‍🏭 {hero_1_name}🔸1 ❤️{hero_1_hp_free}/{hero_1_hp} <b>закончились патроны</b>'
        hero_1_attack = 0

    hero_2_name = result['hero_2']['name']
    hero_2_result = round_result.get('hero_2_attack_status')
    hero_2_attack = round_result.get('hero_2_attack')
    hero_2_hp = result['hero_2']['hp']
    hero_2_hp_free = result['hero_2']['hp_free']
    hero_2_hits = result['hero_2']['hits']
    hero_2_misses = result['hero_2']['misses']
    if round_result.get('hero_2_attack_type'):
        hero_2_type_attacks = name_type_attacks[round_result['hero_2_attack_type']]
    else:
        hero_2_type_attacks = 'прямо'


    if hero_2_result:
        hero_2_text = f'{hero_2_name}🔸2 ❤️{hero_2_hp_free}/{hero_2_hp} атакует <b>{hero_2_type_attacks}</b> и <b>попадает</b>'
    else:
        if hero_1_dodge_status:
            hero_2_text = f'{hero_2_name}🔸2 ❤️{hero_2_hp_free}/{hero_2_hp} атакует <b>{hero_2_type_attacks}</b> и <b>попадает, но противник уворачивается</b>'
        else:
            hero_2_text = f'{hero_2_name}🔸2 ❤️{hero_2_hp_free}/{hero_2_hp} атакует <b>{hero_2_type_attacks}</b> и <b>промахивается</b>'
        hero_2_attack = 0



    await message.answer(f'🔁{result.get("round_num") - 1} ➡️{result.get("meters")}⬅️\n\n'
                         f'{hero_1_text}\n\n'
                         f'{hero_2_text}\n\n'
                         f'⬆️{hero_1_attack} ⬇️{hero_2_attack}\n\n'
                         f'🎯{hero_1_hits} 🚫{hero_1_misses} ❤️‍🩹{hero_2_hits} ⚡️{hero_1_crytical_damage_count} 🤸‍♂️{hero_1_dodge_count}', parse_mode = "html")

    if hero_2_hp_free > 0 and hero_1_hp_free > 0:
        kb = [
            [KeyboardButton(text='↖️Атаковать левее'),
             KeyboardButton(text='↗️Атаковать правее')],
            [KeyboardButton(text='⬆️Атаковать по центру')]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
        await message.answer(f'Выберите куда атаковать', reply_markup=keyboard)
    else:
        kb = [
            [KeyboardButton(text='⬅️Вернуться')]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
        await state.clear()
        
        hero = await Db.get_hero(result['hero_1']['user_ref'])
        if hero_1_hp_free <= 0:
            await message.answer(f'💔 <b>Поражение</b> от {hero_2_name} 🔸2\n\nВаше израненное тело доставили в ближайшее поселение.', reply_markup=keyboard, parse_mode = 'html')
             
            locations = await Db.get_locations_info([hero['location_ref']])
            locations = locations[0]
            nearest_locations = await Db.get_locations_info(locations['nearest_locations'])
            
            await Db.update_location(message.chat.id, nearest_locations[0]['name'])
            for equipment in hero['equipped'].keys():
                equipment_id = hero['equipped'][equipment].get("_id")
                if equipment_id:
                    current_equipment = await Db.get_player_equipments(result['hero_1']['user_ref'], equipment_id = equipment_id)
                    if len(current_equipment) > 0:
                        current_equipment = current_equipment[0]
                        if current_equipment["equipments"].get("type") != "☄️ патроны":
                            current_equipment.pop("equipments")
                            current_equipment['solidity_free'] -= 1
                            if current_equipment['solidity_free'] <= 0:
                                hero['equipped'][equipment] = {}
                                await Db.delete_player_equipments(equipment_id)
                            else:
                                await Db.update_player_equipments(current_equipment['_id'], current_equipment)
                                
                hero['hp_free'] = hero_1_hp_free    
                hero['location_ref'] = nearest_locations[0]['_id']
                await Db.update_hero(result['hero_1']['user_ref'], hero)
                        

        else:
            experience = 0
            money = 0
            msg = None
            text_drops = ""

            if result['hero_1']["lvl"] - result['hero_2']["lvl"] <= 3:
                
                if result['hero_2'].get('experience'):
                    experience = result['hero_2'].get('experience')
                    money = result['hero_2'].get('money')
                    hero['experience'] += experience
                    hero['money'] += money
            
                if result['hero_2'].get('drop'):
                    drops = result['hero_2'].get('drop')
                    if len(drops.keys()) > 0:
                        for drop in drops.keys():
                            if hero["resources"].get(drop):
                                hero["resources"][drop] += drops[drop]
                            else:
                                hero["resources"][drop] = drops[drop]
                        resources = await Db.get_resources(list(drops.keys())) 
                        for resource in resources:
                            text_drops += "\n" + resource["name"]
                    
                    hero['experience'] += experience
                    
            hero['hp_free'] = hero_1_hp_free    
            msg = await Db.update_hero(result['hero_1']['user_ref'], hero)
            text =  f'🥇<b>Победа</b> над противником {hero_2_name} 🔸2\n\nПолучено:'   
            if experience > 0:
                text += "\n💹 Опыт - {experience}"
                
            if money > 0:
                text += f"\n☄️ Патроны - {money}"
                
            text += text_drops
            
            
            await message.answer(text, reply_markup=keyboard, parse_mode = 'html')
            
            
            if result["type"] == "bot":
                await Db.add_quest_resource(result["hero_2"]["user_ref"], result["hero_1"]["user_ref"])
            
            if msg is not None:
                await message.answer(msg, parse_mode = 'html')
                
               
