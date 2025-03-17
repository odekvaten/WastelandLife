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


@router.message(F.text == '📔Навыки')
async def handler_hero_techniques(message: Message, state: FSMContext):
    pass
