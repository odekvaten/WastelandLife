import asyncio
from bot import bot, dp, scheduler
from handlers import (main, map, fight, citizens, hero, fabrics, help, settings,
                      equipped, skills, resources, patterns, techniques)
from db.db_start import check_connection
from db.db_requests import Db





async def run():
    dp.include_routers(main.router, map.router, fight.router, citizens.router,
                       hero.router, fabrics.router, help.router, settings.router,
                       equipped.router, skills.router, resources.router, patterns.router, techniques.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await check_connection()
    scheduler.add_job(Db.update_hero_hp, "interval", seconds=1)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print('Exit')
