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
from handlers.main import TransferState

import math

router = Router()

storage = MemoryStorage()


@router.message(F.text.startswith('👥Жители'))
async def handler_citizens(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    user = await Db.get_user_with_location(telegram_id=message.from_user.id)

    npc_ids = user.get('location').get('npc')
    npc = await Db.get_npc_info(ids=npc_ids)
    npc_ids = [str(i) for i in npc_ids]
    kb = []

    for j, i in enumerate(npc):
        taked_quests = await Db.get_taked_quest(i["tasks"], "quest_id", {"hero_id" : user["_id"]})
        taked_quests = [q["quest_id"] for q in taked_quests]
        task_count = len(i["tasks"])
        for quest in i["tasks"]:
            if quest in taked_quests:
                task_count -= 1
            else:
                q = await Db.get_quest(quest)
                if len(q) > 0:
                    q = q[0]
                    if q['npc2'] != "" and q['npc1'] != str(i['_id']):
                        task_count -= 1
                    elif q['requiredQuest'] != "":
                        required_quest = await Db.get_taked_quest(q['requiredQuest'], 'quest_id', {"hero_id" : user["_id"]})
                        if len(required_quest) > 0:
                            if required_quest[0]['status'] != "done":
                                task_count -= 1
                        else:
                            task_count -= 1
        

        citizen_name = f'{i.get("name")}'
        
        if task_count > 0:
            citizen_name += " (❗️)"
            
        
        if j % 2 == 0:
            kb.append([KeyboardButton(text=f'{citizen_name}')])
        else:
            kb[j // 2].append(KeyboardButton(text=f'{citizen_name}'))

    kb.append([KeyboardButton(text='⬅️Вернуться')])


    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    await message.answer_photo(FSInputFile('./images/start_location.png'),
                               caption='Жители',
                               reply_markup=keyboard)
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
    await state.set_state(TransferState.transferCitizen)

@router.callback_query(F.data.startswith('resource_buy_'))
async def handler_resource_buy(callback: CallbackQuery, state: FSMContext):
    npc_id = callback.data.split('_')[-1]
    resource_id = callback.data.split('_')[-2]
    step = callback.data.split('_')[-3]
    
    resource = await Db.get_resources(resource_id)
    resource = resource[0]
    
    trade = await Db.get_trades_by_trade_id(resource_id)
    trade = trade[0]
    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    if step == "1":
        
        kb = []
        kb.append([InlineKeyboardButton(text=f'⚖️ Купить', callback_data=f'resource_buy_2_{resource_id}_{npc_id}')])
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'resource_get_{npc_id}')])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        
        await callback.message.edit_caption(
            caption=f'{resource["name"]}\n\n{resource["about"]}\n\n☄️ Стоимость: {trade["price"]}', reply_markup = keyboard)
            
    elif step == "2":
        money = hero['money']
        if money < trade['price']:
            await bot.answer_callback_query(callback.id, f"У вас недостаточно средств для покупки!", show_alert=True)
        else:
            hero['money'] -= trade['price']
            if resource_id in hero['resources'].keys():
                hero['resources'][resource_id] += 1
            else:
                hero['resources'][resource_id] = 1
            
            await Db.update_hero(hero['_id'], hero)
            
            await bot.answer_callback_query(callback.id, f"Вы купили -  {resource['name']}!", show_alert=True)
        


@router.callback_query(F.data.startswith('resource_get_'))
async def handler_resource_get(callback: CallbackQuery, state: FSMContext):
    npc_id = callback.data.split('_')[-1]
    key = None
    
    if len(callback.data.split('_')) > 3:
        key = callback.data.split('_')[-2]
    
    npc = await Db.get_npc_by_id(npc_id=npc_id)
    trade = await Db.get_trades_by_npc(npc_id, {"trade_id.resources" : {"$exists" : 1}})
    resources_ids = {}
    for i in trade:
        for j in i['trade_id']['resources']:
         resources_ids[j] = [i['_id'], i['price']]

    resources = await Db.get_resources(list(resources_ids.keys()))
    kb = []
    
    if key:
        name_buttons = {"1" : "компоненты", "2" : "препараты", "3" : "рецепты", "4" : "обвесы"}
        for i in resources:
            if name_buttons[key] in i["type"].lower():
                kb.append([InlineKeyboardButton(text=f'{i["name"]} - {resources_ids[str(i["_id"])][1]}', callback_data=f'resource_buy_1_{str(i["_id"])}_{npc_id}')])
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'resource_get_{npc_id}')])
        
    else:
        name_buttons = {}
        if "компоненты" in str(resources).lower():
            name_buttons["1"] = "⚙️ Компоненты"
        if "препараты" in str(resources).lower():
            name_buttons["2"] = "💉 Препараты"
        if "рецепты" in str(resources).lower():
            name_buttons["3"] = "📑 Рецепты"
        if "обвесы" in str(resources).lower():
            name_buttons["4"] = "🔭 Обвесы"
            
        for i in range(len(name_buttons.keys())):
            if i % 2 == 0:
                key = list(name_buttons.keys())[i]
                kb.append([InlineKeyboardButton(text=name_buttons[key], callback_data=f'resource_get_{key}_{npc_id}')])
            else:
                key = list(name_buttons.keys())[i]
                kb[math.floor(i / 2)].append(InlineKeyboardButton(text=name_buttons[key], callback_data=f'resource_get_{key}_{npc_id}'))
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'npc_resources_{npc_id}')])   
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    await callback.message.edit_caption(
            caption=f'{npc.get("name")}\n\n☄️ Баланс: {hero["money"]}\n\nВыберете предмет для покупки.', reply_markup = keyboard)
        
        
        
@router.callback_query(F.data.startswith('equips_buy_'))
async def handler_equipments_buy(callback: CallbackQuery, state: FSMContext):
    npc_id = callback.data.split('_')[-1]
    equipment_id = callback.data.split('_')[-2]
    step = callback.data.split('_')[-3]
    
    equipment = await Db.get_equipments(equipment_id)
    equipment = equipment[0]
    
    trade = await Db.get_trades_by_trade_id(equipment_id, sub_field = "equipments")
    trade = trade[0]

    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)

    if step == "1":
        
        kb = []
        kb.append([InlineKeyboardButton(text=f'⚖️ Купить', callback_data=f'equips_buy_2_{equipment_id}_{npc_id}')])
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'equips_get_{npc_id}')])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        
        text = f"<b>Название</b> - {equipment['name']}\n<b>Тип</b> - {equipment['type']}\n<b>Эффективная дистанция</b> - {equipment['distanceModifier']}\n\n"
        
        parameters_text = f"Параметры:\n<b>Здоровье</b> - 0\n<b>Урон</b> - {equipment['weaponDamage']}\n<b>Защита</b> - {equipment['armor']}\n<b>Критический урон</b> - {equipment['criticalDamagePower']}\n<b>Шанс крита</b> - {equipment['criticalDamageProbability']}\n\n"
        
        requirements_text = ""
        if equipment['strenght'] > 0:
            requirements_text += f"<b>Сила</b> - {equipment['strenght']}\n"
        if equipment['endurance'] > 0:
            requirements_text += f"<b>Выносливость</b> - {equipment['endurance']}\n"
        if equipment['dexterity'] > 0:
            requirements_text += f"<b>Ловкость</b> - {equipment['dexterity']}\n"
        if equipment['accuracy'] > 0:
            requirements_text += f"<b>Меткость</b> - {equipment['accuracy']}\n"
        if equipment['luck'] > 0:
            requirements_text += f"<b>Удача</b> - {equipment['luck']}\n"
        
        
        
        if len(requirements_text) > 0:
            requirements_text = "Требования:\n" + requirements_text
            requirements_text += "\n"
        
        text += parameters_text + requirements_text

        text += f"<b>Максимальная прочность</b> - {equipment['solidity']}\n☄️ <b>Стоимость</b> - {trade['price']}"

        
        await callback.message.edit_caption(
            caption=text, reply_markup = keyboard, parse_mode = 'html')
            
    elif step == "2":
        money = hero['money']
        if money < trade['price']:
            await bot.answer_callback_query(callback.id, f"У вас недостаточно средств для покупки!", show_alert=True)
        else:
            
            hero['money'] -= trade['price']
            await Db.add_player_equipments(hero["_id"], equipment_id)
            
            await Db.update_hero(hero['_id'], hero)
            await bot.answer_callback_query(callback.id, f"Вы купили -  {equipment['name']}!", show_alert=True)


@router.callback_query(F.data.startswith('equips_get_'))
async def handler_equipments_get(callback: CallbackQuery, state: FSMContext):
    npc_id = callback.data.split('_')[-1]

    key = None
    if len(callback.data.split('_')) > 3:
        key = callback.data.split('_')[-2]
  
    
    npc = await Db.get_npc_by_id(npc_id=npc_id)
    trade = await Db.get_trades_by_npc(npc_id, {"trade_id.equipments" : {"$exists" : 1}})
    equipments_ids = {}
    for i in trade:
        for j in i['trade_id']['equipments']:
            equipments_ids[j] = [i['_id'], i['price']]

    equipments = await Db.get_equipments(list(equipments_ids.keys()))
    kb = []
    
    if key:
        name_buttons = {"1" : "огнестрельное", "2" : "холодное", "3" : "броня", "4" : "шлем", "5" : "патроны", "6" : "стимуляторы"}
        for i in equipments:
            if name_buttons[key] in i["type"].lower():
                kb.append([InlineKeyboardButton(text=f'{i["name"]} - {equipments_ids[str(i["_id"])][1]}', callback_data=f'equips_buy_1_{str(i["_id"])}_{npc_id}')])
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'npc_resources_{npc_id}')])
        
    else:
        name_buttons = {}
        if "огнестрельное" in str(equipments).lower():
            name_buttons["1"] = "🔫 Огнестрельное"
        if "холодное" in str(equipments).lower():
            name_buttons["2"] = "🪓 Холодное"
        if "броня" in str(equipments).lower():
            name_buttons["3"] = "🎽 Броня"
        if "шлем" in str(equipments).lower():
            name_buttons["4"] = "🪖 Шлем"
        if "патроны" in str(equipments).lower():
            name_buttons["5"] = "☄️ Патроны"
        if "стимуляторы" in str(equipments).lower():
            name_buttons["6"] = "💉 Стимуляторы"
            
        for i in range(len(name_buttons.keys())):
            if i % 2 == 0:
                key = list(name_buttons.keys())[i]
                kb.append([InlineKeyboardButton(text=name_buttons[key], callback_data=f'equips_get_{key}_{npc_id}')])
            else:
                key = list(name_buttons.keys())[i]
                kb[math.floor(i / 2)].append(InlineKeyboardButton(text=name_buttons[key], callback_data=f'equips_get_{key}_{npc_id}'))
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'npc_resources_{npc_id}')])   
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    await callback.message.edit_caption(
            caption=f'{npc.get("name")}\n\n☄️ Баланс: {hero["money"]}\n\nВыберете предмет для покупки.', reply_markup = keyboard)

    
    
    
@router.callback_query(F.data.startswith('npc_resources_'))
async def handler_npc_resources(callback: CallbackQuery, state: FSMContext):
    #loader = await callback.message.answer('Загрузка...')
    npc_id = callback.data.split('_')[-1]
    npc = await Db.get_npc_by_id(npc_id=npc_id)
    trade = await Db.get_trades_by_npc(npc_id = npc_id)


    has_resources = False
    has_equipments = False
    if "resources" in str(trade):
        has_resources = True
    if "equipments" in str(trade):
        has_equipments = True
        
    if has_resources and has_equipments:
        kb = []
        kb.append([InlineKeyboardButton(text="♻️ Ресурсы", callback_data=f'resource_get_{npc_id}'),
        InlineKeyboardButton(text="🔫 Снаряжение", callback_data=f'equips_get_{npc_id}')])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        
        await callback.message.edit_reply_markup(reply_markup = keyboard)
        
    elif has_resources:
        await handler_resource_get(callback, state)
        
    elif has_equipments:
        await handler_equipments_get(callback, state)
        
    else:
        await callback.message.answer(f'Ресурсов у жителя "{npc.get("name")}" пока нет. Приходите позже.')
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)


@router.callback_query(F.data.startswith('npc_tasks_'))
async def handler_npc_tasks(callback: CallbackQuery, state: FSMContext):
    #loader = await callback.message.answer('Загрузка...')
    
    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
        
    npc_id = callback.data.split('_')[-1]
    npc = await Db.get_npc_by_id(npc_id=npc_id)
    
    
    quests_button = "📜Задания"
    resources_button = "🗑Торговля"
    
    
    if len(npc['tasks']) <= 0:
        kb = [
            [InlineKeyboardButton(text=resources_button, callback_data=f'npc_resources_{npc.get("_id")}'),
             InlineKeyboardButton(text=quests_button, callback_data=f'npc_tasks_{npc.get("_id")}')]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await callback.message.edit_caption(
            caption=f'{npc.get("name")}\n\nЗаданий у жителя пока нет. Приходите позже', reply_markup=keyboard)
        return
        
    quests = await Db.get_quest(npc['tasks'])
    kb = [[]]
    
    
    for i in quests:
        name_quest = i["name"] 
        if i['requiredQuest'] != "":
            required_quest = await Db.get_taked_quest(i['requiredQuest'], 'quest_id', {"hero_id" : hero["_id"]})
            if len(required_quest) >= 1:
                if required_quest[0]['status'] != "done":
                    continue
            else:
                continue
                    
        take_quest = await Db.get_taked_quest(i['_id'], 'quest_id', {"hero_id" : hero["_id"]})
        if len(take_quest) >= 1:
            if take_quest[0]['status'] == "done":
                name_quest += " ✅"
        elif i["npc2"] != "" and i["npc1"] != npc_id:
            continue
        else:
            name_quest += "❗️"
        kb.append([InlineKeyboardButton(text=name_quest, callback_data=f'npc_about_task_{npc_id}_{i["_id"]}')])
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    if kb == [[]]:
        kb = [
            [InlineKeyboardButton(text=resources_button, callback_data=f'npc_resources_{npc.get("_id")}'),
             InlineKeyboardButton(text=quests_button, callback_data=f'npc_tasks_{npc.get("_id")}')]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await callback.message.edit_caption(
            caption=f'{npc.get("name")}\n\nЗаданий у жителя пока нет. Приходите позже', reply_markup=keyboard)
    else:
        await callback.message.edit_caption(
            caption=f'{npc.get("name")}\n\nСписок заданий в наличии:',
            reply_markup=keyboard)
    
@router.callback_query(F.data.startswith('npc_about_task_'))
async def handler_npc_about_task(callback: CallbackQuery, state: FSMContext):
    quest_id = callback.data.split('_')[-1]
    npc_id = callback.data.split('_')[-2]
    
    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    quest = await Db.get_quest(quest_id)
    
    if len(quest) <= 0:
        return
        
    quest = quest[0]
    if hero["level"] < quest["level"] and quest["level"] != 0:
        await bot.answer_callback_query(callback.id, f"Требуется {quest['level']} уровень героя!\nУровень вашего героя: {hero['level']}", show_alert=True)
        return
    
        
    caption, keyboard = await about_task(npc_id, quest_id, quest, hero["_id"])
    
    
    await callback.message.edit_caption(caption=caption, reply_markup = keyboard, parse_mode="html")
        

@router.callback_query(F.data.startswith('npc_take_task_'))
async def handler_npc_take_task(callback: CallbackQuery, state):
    hero_id = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    hero_id = hero_id["_id"]
    
    quest_id = callback.data.split('_')[-1]
    npc_id = callback.data.split('_')[-2]
    
    quest = await Db.get_quest(quest_id)
    quest = quest[0]
    quest_name = quest['name']
    
    if quest["npc2"] != "" and quest["npc1"] != npc_id:
        npc_info = await Db.get_npc_info([quest["npc1"]])
        if len(npc_info) > 0:
            npc_info = npc_info[0]
            await bot.answer_callback_query(callback.id, f"Взять квест можно у {npc_info['name']}!", show_alert=True)
            return
    
    await Db.take_quest(hero_id, quest_id) 
    await bot.answer_callback_query(callback.id, f"Ты успешно взял задание: {quest_name}", show_alert=True)
    kb = []
    kb.append([InlineKeyboardButton(text="✳️ Завершить задание", callback_data=f'npc_close_task_{npc_id}_{quest_id}')])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'npc_tasks_{npc_id}')])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_reply_markup(reply_markup = keyboard)
    
@router.callback_query(F.data.startswith('npc_close_task_'))
async def handler_npc_close_task(callback: CallbackQuery, state):
    hero = await Db.get_hero_by_telegram_id(callback.message.chat.id)
    hero_id = hero["_id"]
    
    quest_id = callback.data.split('_')[-1]
    npc_id = callback.data.split('_')[-2]
    
    quest = await Db.get_quest(quest_id)
    if len(quest) <= 0:
        return
        
    quest = quest[0]    
    quest_name = quest['name']
    
    if quest["npc2"] != "" and quest["npc2"] != npc_id:
        npc_info = await Db.get_npc_info([quest["npc2"]])
        if len(npc_info) > 0:
            npc_info = npc_info[0]
            await bot.answer_callback_query(callback.id, f"Сдать квест можно у {npc_info['name']}!", show_alert=True)
            return
    
    
    
    for i in quest['countResources']:
        if i not in hero["resources"].keys():
            await bot.answer_callback_query(callback.id, f"Условия задания не выполнены!", show_alert=True)
            return
        if hero["resources"][i] < quest['countResources'][i]:
            await bot.answer_callback_query(callback.id, f"Условия задания не выполнены!", show_alert=True)
            return
        
    take_quest = await Db.get_taked_quest(quest["_id"], 'quest_id', {'hero_id' : hero_id})
    take_quest = take_quest[0]
    for i in quest['countMobs']:
        if i not in take_quest["resources"].keys():
            await bot.answer_callback_query(callback.id, f"Условия задания не выполнены!", show_alert=True)
            return
        if take_quest["resources"][i] < quest['countMobs'][i]:
            await bot.answer_callback_query(callback.id, f"Условия задания не выполнены!", show_alert=True)
            return


    

    for i in quest['countResources']:
        hero["resources"][i] -= quest['countResources'][i]
        if hero["resources"][i] <= 0:
            hero["resources"].pop(i)

    hero["money"] += quest["money"]
    hero["experience"] += quest["experience"]
    
    reward_quest = "\n<b>Награда</b>\n"
    reward_equipments = None
    reward_resources = None

    if quest['rewardItem'].get("equipments"):
        for equipment in quest['rewardItem']["equipments"].keys():
            for equipment_count in range(quest['rewardItem']["equipments"][equipment]):
                await Db.add_player_equipments(hero_id, equipment)
                
    if quest['rewardItem'].get("resources"):
        for resources in quest['rewardItem']["resources"].keys():
            if hero["resources"].get(resources):
                hero["resources"][resources] += quest['rewardItem']["resources"][resources]
            else:
                hero["resources"][resources] = quest['rewardItem']["resources"][resources]
            
    msg = await Db.update_hero(hero_id, hero)
    
    await Db.close_quest(hero_id, quest_id)
    
    caption, keyboard = await about_task(npc_id, quest_id, quest, hero_id)
    
    await callback.message.edit_caption(caption=caption, reply_markup = keyboard, parse_mode="html")

    await bot.answer_callback_query(callback.id, f"Ты успешно сдал задание: {quest_name}", show_alert=True)
    
    if msg is not None:
        await callback.message.answer(msg, parse_mode = "html")
    
    
@router.message(TransferState.transferCitizen)
async def transfer_to_citizen(message: Message, state: FSMContext):
    #loader = await message.answer('Загрузка...')

    npc = await Db.get_npc_by_name(name=message.text.replace(" (❗️)", ""))
    quests_button = "📜Задания"
    resources_button = "🗑Торговля"
    if len(npc['tasks']) >= 0:
    
        hero = await Db.get_hero_by_telegram_id(message.chat.id)
        taked_quests = await Db.get_taked_quest(npc['tasks'], 'quest_id', {'hero_id' : hero["_id"]})
        
        task_count = len(npc["tasks"])
        taked_quests = [j["quest_id"] for j in taked_quests]
        
        
        
        for i in npc["tasks"]:
            if i in taked_quests:
                task_count -= 1
            else:
                quest = await Db.get_quest(i)
                if len(quest) > 0:
                    quest = quest[0]
                    if quest['npc2'] != "" and quest['npc1'] != str(npc["_id"]):
                        task_count -= 1
                    elif quest['requiredQuest'] != "":
                        required_quest = await Db.get_taked_quest(quest['requiredQuest'], 'quest_id', {"hero_id" : hero["_id"]})

                        if len(required_quest) > 0:
                            if required_quest[0]['status'] != "done":
                                task_count -= 1
                        else:
                            task_count -= 1
                                

        if task_count > 0:
            quests_button += f" (❗️{task_count})"
    
    kb = [
        [InlineKeyboardButton(text=resources_button, callback_data=f'npc_resources_{npc.get("_id")}'),
         InlineKeyboardButton(text=quests_button, callback_data=f'npc_tasks_{npc.get("_id")}')]
    ]


        
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer_photo(FSInputFile(npc['image']),
                               caption=f'{npc.get("name")}\n\n'
                                       f'{npc.get("about")}',
                               reply_markup=keyboard, parse_mode="html")
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)
    
    
async def about_task(npc_id, quest_id, quest = None, hero_id = None):
    if quest is None:
        quest = await Db.get_quest(quest_id)
        if len(quest) <= 0:
            return None, None
        quest = quest[0]
    
    

    npc = await Db.get_npc_by_id(npc_id=npc_id)
    take_quest = await Db.get_taked_quest(quest_id, "quest_id", {"hero_id" : hero_id})
    
    name_quest = "\n\n" + quest['name']   
    text_quest = quest['beginText']
    
    goal_quest = "\n\n<b>Цель</b>\n"
    if len(quest['countMobs']) > 0:
        goal_quest += "\n<b>Убить мобов:</b>"
        if "all" in quest['countMobs'].keys():
            goal_quest += f"\nМобы: {quest['countMobs']['all']}\n" 
        else:
            mobs = await Db.get_mobs(list(quest['countMobs'].keys()))
            for i in mobs:
                goal_quest += f"\n{i['name']}: {quest['countMobs'][str(i['_id'])]}\n" 
    if len(quest['countResources']) > 0:
        goal_quest += "\n<b>Добыть ресурсов:</b>"
        resources = await Db.get_resources(list(quest['countResources'].keys()))
        for i in resources:
            goal_quest += f"\n{i['name']}: {quest['countResources'][str(i['_id'])]}\n" 
            
            
    reward_quest = "\n<b>Награда</b>\n"
    reward_equipments = None
    reward_resources = None

    if "equipments" in quest['rewardItem'].keys():
        if len(quest['rewardItem']['equipments']) > 0:
            reward_equipments = await Db.get_equipments(list(quest['rewardItem']['equipments'].keys()))
            reward_quest += "\n<b>Снаряжение:</b>"
            for i in reward_equipments:
                reward_quest += f"\n{i['name']}: {quest['rewardItem']['equipments'][str(i['_id'])]}\n"
            
            
    if "resources" in quest['rewardItem'].keys():
        if len(quest['rewardItem']['resources']) > 0:
            reward_resources = await Db.get_resources(list(quest['rewardItem']['resources'].keys()))
            reward_quest += "\n<b>Ресурсы:</b>"
            for i in reward_resources:
                reward_quest += f"\n{i['name']}: {quest['rewardItem']['resources'][str(i['_id'])]}\n"
    
    reward_quest += f"\n💰 <b>Золото</b>: {quest['experience']}\n"
    reward_quest += f"💫 <b>Опыт</b>: {quest['experience']}"
    
    
    kb = []
    kb.append([InlineKeyboardButton(text="✳️ Взять задание", callback_data=f'npc_take_task_{npc_id}_{quest_id}')])    
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f'npc_tasks_{npc_id}')])

    
    if len(take_quest) > 0:
        if take_quest[0]['status'] == "done":
            text_quest = quest['endText']
            kb[0].pop(0)
        else:
            kb[0][0] = InlineKeyboardButton(text="✳️ Завершить задание", callback_data=f'npc_close_task_{npc_id}_{quest_id}')
            
    text_quest = "\n\n" + text_quest
    
    caption = npc.get("name") + name_quest + text_quest + goal_quest + reward_quest
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    return caption, keyboard
