from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from secret import BOT_TOKEN

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import multiprocessing
import os


def start_adminka():
    os.system("cd /home/adminka/\npython3 index.py")



bot = Bot(token=BOT_TOKEN, default= DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()
scheduler = AsyncIOScheduler()
adminka_process = multiprocessing.Process(target = start_adminka)
adminka_process.start()







