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


class RegisterState(StatesGroup):
    nickname = State()
    background = State()

class TransferState(StatesGroup):
    transferLocation = State()
    transferCitizen = State()


async def go_to_location(message, state: FSMContext):
    #loader = await message.answer('Загрузка...')
    hero = await Db.get_user_with_location(telegram_id=message.from_user.id)
    
    if hero.get('location').get('is_city'):
        npc_ids = hero.get('location').get('npc')
        npc = await Db.get_npc_info(ids=npc_ids)
        tasks = [j for i in npc for j in i['tasks']]
        npc_ids = [str(i) for i in npc_ids]
        taked_quests = await Db.get_taked_quest(tasks, "quest_id", {"hero_id" : hero["_id"]})
        taked_quests = [quest["quest_id"] for quest in taked_quests]
        
        task_count = len(tasks)
        
        for quest in tasks:
            if quest in taked_quests:
                task_count -= 1
            else:
                q = await Db.get_quest(quest)
                
                if len(q) > 0:
                    q = q[0]
                    if q['npc2'] != "" and q['npc1'] not in npc_ids:
                            task_count -= 1
                    elif q['requiredQuest'] != "":
                        required_quest = await Db.get_taked_quest(q['requiredQuest'], 'quest_id', {"hero_id" : hero["_id"]})
                        if len(required_quest) > 0:
                            if required_quest[0]['status'] != "done":
                                task_count -= 1
                        else:
                            task_count -= 1
        
        citizens = '👥Жители'
        
        if task_count > 0:
                citizens += " (❗️)"
        kb = [
            [KeyboardButton(text='🗺Карта'),
             KeyboardButton(text=citizens)],
            [KeyboardButton(text='👨‍🎤Персонаж'),
             KeyboardButton(text='🏭Фабрики')],
            [KeyboardButton(text='📚Помощь'),
             KeyboardButton(text='⚙️Настройки')]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)
    else:
        kb = [
            [KeyboardButton(text='🗺Карта'),
             KeyboardButton(text='⚔️Найти противника')],
            [KeyboardButton(text='👨‍🎤Персонаж'),
             KeyboardButton(text='📚Помощь')],
            [KeyboardButton(text='⚙️Настройки')]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard = True)

    await message.answer_photo(FSInputFile(hero.get('location').get('image')),
                               caption=f'<b>{hero.get("location").get("name")}</b>\n\n'
                                       f'{hero.get("location").get("about")}\n\n'
                                       f'👮 {hero.get("nickname")} 🔷{hero.get("level")} '
                                       f'({hero.get("hp_free")}/{hero.get("hp")})\n\n'
                                       f'Торговый чат | Новости | Общий чат',
                               reply_markup=keyboard, parse_mode='html')
    await state.clear()
    #await bot.delete_message(chat_id=loader.chat.id, message_id=loader.message_id)

@router.message(F.text == '/start')
async def handler_start_message(message: Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    if await Db.check_telegram_id(telegram_id=telegram_id):
        await go_to_location(message=message, state=state)
    else:
        await message.answer_photo(FSInputFile('./images/location.png'),
                                   caption='Добро пожаловать в Wastelands!')
        await message.answer(f'Для регистрации в игре отправь никнейм.')
        await state.set_state(RegisterState.nickname)

    
@router.message(RegisterState.nickname)
async def handler_nickname_message(message: Message, state: FSMContext):
    nickname = message.text
    if await Db.check_nickname(nickname=nickname):
        await message.answer('Выбранный никнейм занят, используйте другой')
    else:
        await message.answer(f'Регистрируем в системе нового пользователя {nickname} ...')
        type(message.from_user.id)
        
        
        profile = await Db.new_profile(telegram_id=message.from_user.id,
                          telegram_name=message.from_user.first_name,
                          telegram_lang=message.from_user.language_code,
                          nickname=nickname,
                          telegram_last_online=datetime.datetime.now(),
                          telegram_referral_id='',
                          telegram_referrals=[],
                          telegram_is_active=True,
                          premium_coins=0,
                          telegram_source_from='',
                          telegram_created_at=datetime.datetime.now(),
                          is_banned = False,
                          ban_date = None,
                          action_count = 0,
                          current_hero = None,
                          is_premium = False,
                          premium_date = None,
                          max_count_heroes = 2)   
                          
                          
        hero = await Db.new_hero(
                          profile_id = profile.inserted_id,
                          nickname = nickname,
                          gender='',
                          energy=0,
                          speed=1,
                          state='start_location',
                          level=1,
                          location_ref=bson.ObjectId('664a42eb2c15f77ced5860b3'),
                          experience=0,
                          fame=0,
                          money=0,
                          hp=50,
                          hp_free = None,
                          patterns={'strength': 1, 'endurance': 1,
                                    'agility': 1, 'accuracy': 1, 'luck' : 1, 'points': 0},
                          resources={},
                          equipped={'gun_1': {},
                                    'gun_2' : {},
                                    'patrons': {},
                                    'cold_gun_1': {},
                                    'pocket': {},
                                    'armor': {},
                                    'helmet': {}},
                          techniques=[],
                          faction='',
                          craft='',
                          background='',
                          action_count = 0,
                          karma = 0,
                          locations_visited = [])                   
                          
                          
        await Db.change_current_hero(message.from_user.id, hero.inserted_id)
        
        await state.clear()
        await go_to_location(message=message, state=state)


@router.message(F.text == '⬅️Вернуться')
async def handler_back_message(message: Message, state: FSMContext):
    await state.clear()
    await go_to_location(message=message, state=state)
