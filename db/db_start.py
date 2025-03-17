from motor.motor_asyncio import AsyncIOMotorClient
from secret import DB_PASS

uri = (f"mongodb+srv://"
       f"user:{DB_PASS}"
       f"@cluster0.rggyeky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = AsyncIOMotorClient(uri)
db = client.wastelands


class Collection:
    profile = db.profile
    hero = db.heroes
    equipment = db.equipments
    location = db.locations
    fight = db.fights
    npc = db.npc
    resources = db.resources
    equipments = db.equipments
    quests = db.quests
    takequests = db.takequests
    mobs = db.mobs
    routes = db.routes
    trades = db.trades
    effects = db.effects
    playerequipments = db.playerequipments

async def check_connection():
    try:
        await client.admin.command('ping')  # Использование 'await' внутри асинхронной функции
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

#asyncio.run(check_connection())
