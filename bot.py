from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from secret import BOT_TOKEN

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os




bot = Bot(token=BOT_TOKEN, default= DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()
scheduler = AsyncIOScheduler()







