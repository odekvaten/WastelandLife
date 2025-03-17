import asyncio
import random
from math import ceil

from db.db_start import client
from datetime import datetime, timedelta
from db.db_start import Collection
from db.models import Model
import aiohttp
import bson

class Db:
    @staticmethod
    async def check_nickname(nickname):
        is_nickname = await Collection.hero.find({'nickname': nickname}).to_list(None)
        if is_nickname:
            return True
        else:
            return False

    @staticmethod
    async def check_telegram_id(telegram_id):
        is_telegram_id = await Collection.profile.find({'telegram_id': telegram_id}).to_list(None)
        if is_telegram_id:
            return True
        else:
            return False
            
    @staticmethod
    async def new_profile(telegram_id, telegram_name, telegram_lang, nickname, telegram_last_online, telegram_referral_id, telegram_referrals, telegram_is_active, premium_coins, telegram_source_from, telegram_created_at, is_banned, ban_date, action_count, current_hero, is_premium, premium_date, max_count_heroes):
        user = await Collection.profile.insert_one({
                "telegram_id": telegram_id,
                "telegram_name": telegram_name,
                "telegram_lang": telegram_lang,
                "telegram_last_online": telegram_last_online,
                "telegram_referral_id": telegram_referral_id,
                "telegram_referrals": telegram_referrals,
                "telegram_is_active": telegram_is_active,
                "telegram_source_from": telegram_source_from,
                "telegram_created_at": telegram_created_at,
                "premium_coins": premium_coins,
                "nickname" : nickname,
                "is_banned" : is_banned,
                "ban_date" : ban_date,
                "action_count" : action_count,
                "current_hero" : current_hero,
                "is_premium" : is_premium,
                "premium_date" : premium_date,
                "max_count_heroes" : max_count_heroes})
                
        return user
    
    @staticmethod
    async def new_trade(trade_id, npc_id, currency, price):
        await Collection.trades.insert_one({
                "trade_id" : [],
                "npc_id" : [],
                "currency": "☄️патрон",
                "price": 40
                })
                
    @staticmethod
    async def get_trades_by_npc(npc_id, filters = {}):
        if type(npc_id) is list:
            npc_id = [bson.ObjectId(id) for id in npc_id]
        elif type(npc_id) is str:
            npc_id = [npc_id]
        
        filters["npc_id"] = {"$in" : npc_id}
        
        trades = await Collection.trades.find(filters).to_list(None)
        return trades
        
    @staticmethod
    async def get_trades_by_trade_id(trade_id, filters = {}, sub_field = "resources"):
        if type(trade_id) is str:
            trade_id = [trade_id]
        
        filters["trade_id." + sub_field] = {"$in" : trade_id}
        
        trades = await Collection.trades.find(filters).to_list(None)
        return trades
     
                
    @staticmethod
    async def new_hero(profile_id, nickname, gender, energy, state, level, speed, location_ref, experience, fame, money, hp, hp_free, patterns, resources, equipped, techniques, faction, craft, background, action_count, karma, locations_visited):
    
        if hp_free is None:
            hp_free = hp
            
        hero = await Collection.hero.insert_one({
                "profile_id" : profile_id,
                "nickname" : nickname,
                "gender": gender,
                "energy": energy,
                "state": state,
                "level": level,
                "speed" : speed,
                "location_ref": location_ref,
                "experience": experience,
                "fame": fame,
                "money": money,
                "hp": hp,
                "hp_free": hp_free,
                "patterns": patterns,
                "resources" : resources,
                "equipped": equipped,
                "techniques": techniques,
                "faction": faction,
                "craft": craft,
                "background": background,
                "action_count" : action_count,
                "karma" : karma,
                "locations_visited" : locations_visited})
        return hero
    
    @staticmethod
    async def change_current_hero(telegram_id, hero_id):
        await Collection.profile.update_one({'telegram_id': telegram_id},
        {'$set': {'current_hero': bson.ObjectId(hero_id)}})

        return True
        
    @staticmethod
    async def get_hero_equipped(_id):
        equipped = await Collection.equipments.find({"_id": bson.ObjectId(_id)}).to_list(None)
        return equipped[0]
    
    @staticmethod
    async def get_profile(telegram_id):
        profile = await Collection.profile.find({"telegram_id": telegram_id}).to_list(None)
        return profile[0]
        
    @staticmethod
    async def get_user_with_location(telegram_id):
        hero_id = await Db.get_profile(telegram_id)
        hero_id = bson.ObjectId(hero_id["current_hero"])
        pipeline = [
            {
                '$match': {
                    '_id': hero_id
                }
            },
            {
                '$lookup': {
                    'from': 'locations',
                    'localField': 'location_ref',
                    'foreignField': '_id',
                    'as': 'location'
                }
            },
            {
                '$unwind': {
                    'path': '$location',
                    'preserveNullAndEmptyArrays': True
                }
            }
        ]
        
        hero = await Collection.hero.aggregate(pipeline).to_list(None)

        
        if 'location' not in hero[0].keys():
            await Db.update_location(telegram_id, '🏙 Контейнер')
            hero = await Collection.hero.aggregate(pipeline).to_list(None)                  
                                                            
        return hero[0]

    @staticmethod
    async def get_npc_info(ids):
        npc_object_ids = [bson.ObjectId(id) for id in ids]
        npc = await Collection.npc.find({"_id": {"$in": npc_object_ids}}).to_list(None)
        return npc

    @staticmethod
    async def get_npc_by_name(name):
        npc = await Collection.npc.find({"name": name}).to_list(None)
        return npc[0]

    @staticmethod
    async def get_npc_by_id(npc_id):
        npc = await Collection.npc.find({"_id": bson.ObjectId(npc_id)}).to_list(None)
        return npc[0]

    @staticmethod
    async def get_locations_info(ids):
        locations_object_ids = [bson.ObjectId(id) for id in ids]
      
        locations = await Collection.location.find({"_id": {"$in": locations_object_ids}}).to_list(None)
        return locations

    @staticmethod
    async def get_location_by_name(location_name):
        location = await Collection.location.find({"name": location_name}).to_list(None)
        return location[0]

    @staticmethod
    async def get_hero_by_telegram_id(telegram_id):
        hero_id = await Db.get_profile(telegram_id)
        hero_id = hero_id["current_hero"]
        hero = await Collection.hero.find({"_id": bson.ObjectId(hero_id)}).to_list(None)
       
        return hero[0]
        
    @staticmethod
    async def get_hero(hero_id):
        hero = await Collection.hero.find({"_id": bson.ObjectId(hero_id)}).to_list(None)
       
        return hero[0]
        
    @staticmethod
    async def update_location(hero_telegram_id, location_name):
        hero = await Db.get_hero_by_telegram_id(telegram_id=hero_telegram_id)
        hero_id = str(hero.get('_id'))
        location = await Db.get_location_by_name(location_name=location_name)
        location_id = str(location.get('_id'))
        current_location = await Collection.hero.update_one({'_id': bson.ObjectId(hero_id)},
                                                            {'$set': {'location_ref': bson.ObjectId(location_id)}})
        return True

    @staticmethod
    async def resource_set_equipped(hero_telegram_id, resource_name):
        hero = await Db.get_hero_by_telegram_id(telegram_id=hero_telegram_id)
        if '_id' in hero:
            del hero['_id']
        resources = hero.get('resources')
        resource_data = {}
        new_resources = []
        equipped_now_data = {}
        if resources:
            print('resources')
            for resource in resources:
                if resource.get('name') == resource_name:
                    print('if resource.get == resource_name')
                    resource_data = resource
                else:
                    new_resources.append(resource)
            if resource_data:
                print('if resource_data')
                if hero.get('equipped').get(resource_data.get('type')):
                    equipped_now_data = hero.get('equipped').get(resource_data.get('type'))
                    new_resources.append(equipped_now_data)
                hero['resources'] = new_resources
                hero['equipped'][resource_data.get('type')] = resource_data
                print(hero)
                isss = await Collection.hero.update_one({'telegram_id': hero_telegram_id}, {'$set': hero})
                print(isss)
        else:
            pass

    @staticmethod
    async def is_fight_available(telegram_id):
        hero = await Db.get_hero_by_telegram_id(telegram_id)
        hero_lvl = hero.get('level')
        hero_hp = hero.get('hp')
        hero_hp_free = hero.get('hp_free')

        if hero_hp_free / hero_hp < 0.5:
            return False
        else:
            return True

    @staticmethod
    async def find_fight(telegram_id):
        hero = await Db.get_hero_by_telegram_id(telegram_id)
        hero_lvl = hero.get('level')
        hero_hp = hero.get('hp')

        is_human_fight = False
        finding_fights_try = 5
        waiting_fights = await Collection.fight.find({'status': 'waiting', 'lvl': '1'}).to_list(None)

        if not waiting_fights:
            while finding_fights_try > 0 and not is_human_fight:
                print('finding fight')
                await asyncio.sleep(1)
                waiting_fights = await Collection.fight.find({'status': 'waiting', 'lvl': '1'}).to_list(None)
                finding_fights_try -= 1
            if not is_human_fight:
                all_mobs = await Db.get_mobs()
                hero_location = hero.get('location_ref')
                
                mobs = []
                for i in all_mobs:
                    if str(i['location_ref']) == str(hero_location):
                        mobs.append(i)
                
                if len(mobs) > 0:        
                    mob = random.choice(mobs)
                else:
                    mob = random.choice(all_mobs)
                
                bot_fight = {
                    'status': 'fight',
                    'type': 'bot',
                    'hero_1': {
                        'is_bot': False,
                        'user_ref': hero.get('_id'),
                        'user_telegram_id': hero.get('telegram_id'),
                        'name': hero.get('nickname'),
                        'lvl': hero.get('level'),
                        'hp' : hero.get('hp'),
                        'hp_free': hero.get('hp_free'),
                        'patterns': hero.get('patterns'),
                        'equipped': hero.get('equipped'),
                        'hits' : 0,
                        'misses' : 0,
                        'dodge_count' : 0,
                        'crytical_damage_count' : 0
                    },
                    'hero_2': {
                        'is_bot': True,
                        'user_ref': mob["_id"],
                        'name': mob["name"],
                        'about' : mob["about"],
                        'lvl': mob["level"],
                        'hp': mob['hp'],
                        'hp_free': mob["hp"],
                        'patterns': mob["patterns"],
                        'experience' : mob["experience"],
                        'money' : mob["money"],
                        'equipped': {
                            'gun_1': mob["gun"]["gun_1"],
                            'gun_2': mob["gun"]["gun_2"],
                            'cold_gun_1': mob["gun"]["cold_gun_1"],
                            'armor': mob["armor"],
                            'helmet': mob["helmet"]
                        },
                        'hits' : 0,
                        'misses' : 0,
                        'image' : mob["image"],
                        'drop' : mob['drop']
                    },
                    'round_num': 1,
                    'meters': 7,
                    'rounds': []
                }
                await Collection.fight.insert_one(bot_fight)
                return bot_fight

        return waiting_fights[0]

        # pipeline = [
        #     {
        #         '$match': {
        #             '_id': bson.ObjectId(str(waiting_fights[0].get('_id')))
        #         }
        #     },
        #     {
        #         '$lookup': {
        #             'from': 'heroes',
        #             'localField': 'hero_ref',
        #             'foreignField': '_id',
        #             'as': 'hero'
        #         }
        #     },
        #     {
        #         '$unwind': {
        #             'path': '$hero',
        #             'preserveNullAndEmptyArrays': True
        #         }
        #     }
        # ]
        # fight = await Collection.fight.aggregate(pipeline).to_list(None)
        # return fight[0]

    @staticmethod
    async def find_action(fight_id, user_telegram_id, attack_type, evasion_type, only_fight = False):
        fight = await Collection.fight.find({'_id': bson.ObjectId(fight_id)}).to_list(None)
        fight = fight[0]
        if only_fight:
            return fight

        accuracy = fight.get('hero_1').get('patterns').get('accuracy')
        endurance = fight.get('hero_1').get('patterns').get('endurance')
        luck = fight.get('hero_1').get('patterns').get('luck')
        is_equipped_hero_1 = fight.get('hero_1').get('equipped')
        weaponType = None
        criticalDamagePower = 0
        criticalDamageProbability = 0
        
        can_shoot = True
        
        
        if is_equipped_hero_1:
            if is_equipped_hero_1.get('gun_1'):
                if is_equipped_hero_1.get('gun_1').get('_id'):
                    gun_1_id = await Db.get_player_equipments(fight.get('hero_1').get("user_ref"), equipment_id =  is_equipped_hero_1.get('gun_1').get('_id'))
                    if gun_1_id:
                        gun_1_id = gun_1_id[0]['equipment_id']
                    
                    gun_1 = await Db.get_hero_equipped(gun_1_id)
                    gun_1.update(is_equipped_hero_1.get('gun_1'))
                    weaponType = gun_1.get("type")
                    weaponDamage = ceil(gun_1.get("weaponDamage"))
                    patronDamage = ceil(gun_1.get("patronDamage"))
                    criticalDamagePower = ceil(gun_1.get("criticalDamagePower"))
                    criticalDamageProbability = ceil(gun_1.get("criticalDamageProbability"))
                    distanceModifier = gun_1.get("distanceModifier")
                    if type(distanceModifier) == list and weaponType == "🔫 огнестрельное":
                        if fight['round_num'] < len(distanceModifier):
                            distanceModifier = distanceModifier[fight['round_num']]
                        else:
                            distanceModifier = distanceModifier[len(distanceModifier) - 1]
                    else:
                            distanceModifier = 0
                    hero = await Db.get_hero(fight.get('hero_1').get('user_ref'))
                    if hero["equipped"]["patrons"].get('_id'):
                        patrons = await Db.get_player_equipments(fight.get('hero_1').get("user_ref"), equipment_id = is_equipped_hero_1.get('patrons').get('_id'))
                        patrons = patrons[0]
                        patrons["count"] -= 1
                        if patrons["count"] <= 0:
                            
                            hero["equipped"]["patrons"] = {}
                            await Db.update_hero(hero["_id"], hero)
                            await Db.delete_player_equipments(is_equipped_hero_1.get('patrons').get('_id'))
                        else:
                            patrons.pop("equipments")
                            await Db.update_player_equipments(patrons.get('_id'), patrons)
                    else:
                        if hero['money'] > 0:
                            hero["money"] -= 1
                            await Db.update_hero(hero["_id"], hero)
                        else:
                            can_shoot = False    
                    
                else:
                    weaponDamage = 0
                    patronDamage = 0
                    distanceModifier = 0    
                    
            else:
                weaponDamage = 0
                patronDamage = 0
                distanceModifier = 0
        else:
            gun_1 = 0
            
        if weaponType != "🔫 огнестрельное":
            accuracy = 1
            distanceModifier = 0
            patronDamage = 0
            
            
            
        meters = fight.get('meters')
        is_equipped_hero_2 = fight.get('hero_2').get('equipped')
        hero_2_accuracy = fight.get('hero_2').get('patterns').get('accuracy')
        hero_2_luck = fight.get('hero_2').get('patterns').get('luck')
        hero_2_endurance = fight.get('hero_2').get('patterns').get('endurance')
        hero_2_agility = fight.get('hero_2').get('patterns').get('agility')

        hero_2_weaponType = None
        hero_2_criticalDamagePower = 0
        hero_2_criticalDamageProbability = 0
        if is_equipped_hero_2:
            if is_equipped_hero_2.get('gun_1'):
                if is_equipped_hero_2.get('gun_1').get('_id'):
                    
                    hero_2_gun_1 = await Db.get_hero_equipped(is_equipped_hero_2.get('gun_1').get('_id'))
                    hero_2_gun_1.update(is_equipped_hero_2.get('gun_1'))
                    hero_2_weaponType = hero_2_gun_1.get("type")
                    hero_2_weaponDamage = ceil(hero_2_gun_1.get("weaponDamage"))
                    hero_2_patronDamage = ceil(hero_2_gun_1.get("patronDamage"))
                    hero_2_criticalDamagePower = ceil(hero_2_gun_1.get("criticalDamagePower"))
                    hero_2_criticalDamageProbability = ceil(hero_2_gun_1.get("criticalDamageProbability"))
                    hero_2_distanceModifier = hero_2_gun_1.get("distanceModifier")
                    if type(hero_2_distanceModifier) == list and hero_2_weaponType == "🔫 огнестрельное":
                        if fight['round_num'] < len(hero_2_distanceModifier):
                            hero_2_distanceModifier = hero_2_distanceModifier[fight['round_num']]
                        else:
                            hero_2_distanceModifier = hero_2_distanceModifier[len(hero_2_distanceModifier) - 1]
                    else:
                            hero_2_distanceModifier = 0
                else:
                    hero_2_weaponDamage = 0
                    hero_2_patronDamage = 0
                    hero_2_distanceModifier = 0    
                    
            else:
                hero_2_weaponDamage = 0
                hero_2_patronDamage = 0
                hero_2_distanceModifier = 0
        else:
            hero_2_gun_1 = 0
            
        if hero_2_weaponType != "🔫 огнестрельное":
            hero_2_accuracy = 1
            hero_2_distanceModifier = 0
            hero_2_patronDamage = 0
        
        
        if is_equipped_hero_1:
            if is_equipped_hero_1["armor"].get("_id"):
                hero_1_armor = await Db.get_hero_equipped(is_equipped_hero_1["armor"].get("_id"))
                hero_1_protection_armor = hero_1_armor.get('armor')
                
            else:
                hero_1_protection_armor = 0
            if is_equipped_hero_1["helmet"].get("_id") and hero_2_weaponType == "🔫 огнестрельное":
                hero_1_helmet = await Db.get_hero_equipped(is_equipped_hero_1["armor"])
                hero_1_protection_helmet = hero_1_helmet.get('armor')
            else:
                hero_1_protection_helmet = 0
        else:
            hero_1_protection_armor = 0
            hero_1_protection_helmet = 0
        
        hero_1_protection = hero_1_protection_armor + hero_1_protection_helmet
        
        if is_equipped_hero_2:
            if is_equipped_hero_2["armor"] != "":

                hero_2_armor = await Db.get_hero_equipped(is_equipped_hero_2["armor"])
                hero_2_protection_armor = hero_2_armor.get('armor')
                
            else:
                hero_2_protection_armor = 0
            if is_equipped_hero_2["helmet"] != "" and weaponType == "🔫 огнестрельное":
                hero_2_helmet = await Db.get_hero_equipped(is_equipped_hero_2["helmet"])
                hero_2_protection_helmet = hero_2_helmet.get('armor')
            else:
                hero_2_protection_helmet = 0
        else:
            hero_2_protection_armor = 0
            hero_2_protection_helmet = 0
            
        hero_2_protection = hero_2_protection_armor + hero_2_protection_helmet
        
        criticalProbability = luck * 0.1 + criticalDamageProbability * 0.1
        hero_1_crytical_damage_status = False
        if random.randrange(0, 100) <= criticalProbability:
            attack = ((weaponDamage * accuracy * 0.05 * distanceModifier) + patronDamage + criticalDamageProbability) - (hero_2_endurance * 0.1 + hero_2_protection * 0.1)
            fight['hero_1']['crytical_damage_count'] += 1
            hero_1_crytical_damage_status = True
        else:
            attack = ((weaponDamage * accuracy * 0.05  * distanceModifier) + patronDamage) - (hero_2_endurance * 0.1 + hero_2_protection * 0.1)
            
        
        
        bot_attack_types = ['left', 'right', 'center']
        bot_attack_type = bot_attack_types[random.randint(0, 2)]

        bot_evasion_types = ['left', 'right', 'center']
        bot_evasion_type = bot_evasion_types[random.randint(0, 2)]

        
        
        hero_2_criticalProbability = hero_2_luck * 0.1 + hero_2_criticalDamageProbability * 0.1
        
        if random.randrange(0, 100) <= hero_2_criticalProbability:
            bot_attack = ((hero_2_weaponDamage * hero_2_accuracy * 0.05 * hero_2_distanceModifier) + hero_2_patronDamage + hero_2_criticalDamageProbability) - (endurance * 0.1 + hero_1_protection * 0.1)
        else:
            bot_attack = ((hero_2_weaponDamage * hero_2_accuracy * 0.05 * hero_2_distanceModifier) + hero_2_patronDamage) - (endurance * 0.1 + hero_1_protection * 0.1)
        

        dodge = None
        

        if attack_type != bot_evasion_type:
            hero_1_attack_status = False
            fight['hero_1']['misses'] +=  1
        else:
            hero_1_attack_status = True
            fight['hero_1']['hits'] += 1
            if fight['hero_2']['hp_free'] > attack and can_shoot:
                fight['hero_2']['hp_free'] -= attack
            else:
                fight['hero_2']['hp_free'] = 0
            fight['hero_2']['hp_free'] = round(fight['hero_2']['hp_free'])
                
        dodge_status = False
        if bot_attack_type != evasion_type:
            hero_2_attack_status = False
            fight['hero_2']['misses'] += 1
        else:
            hero_2_attack_status = True
            fight['hero_2']['hits'] += 1
            
            
            dodge = fight['hero_1']["patterns"]["agility"] * random.randint(1, 4) * 0.1
            if random.randrange(0, 100) <= dodge:
                hero_2_attack_status = False
                dodge_status = True
                fight['hero_1']['dodge_count'] +=  1
                
            if hero_2_attack_status:
                if fight['hero_1']['hp_free'] > bot_attack:
                    fight['hero_1']['hp_free'] -= bot_attack
                else:
                    fight['hero_1']['hp_free'] = 0
            
            fight['hero_1']['hp_free'] = round(fight['hero_1']['hp_free'])
        

        fight['rounds'].append({
            'round': fight['round_num'],
            'hero_1_attack_type': attack_type,
            'hero_1_attack': round(max(0, attack)),
            'hero_1_attack_status': hero_1_attack_status,
            'hero_1_evasion_type': evasion_type,
            'hero_1_critical_probability': criticalProbability,
            "hero_1_crytical_damage_status": hero_1_crytical_damage_status,
            'hero_1_dodge': dodge,
            'hero_1_dodge_status': dodge_status,
            "hero_1_can_shoot" : can_shoot,
            'hero_2_attack_type': bot_attack_type,
            'hero_2_attack': round(max(0, bot_attack)),
            'hero_2_attack_status': hero_2_attack_status,
            'hero_2_evasion_type': bot_evasion_type,
        })

        fight['round_num'] = fight['round_num'] + 1
        if fight['meters'] > 0:
            fight['meters'] = fight['meters'] - 1

        await Collection.fight.update_one({'_id': bson.ObjectId(fight['_id'])}, {'$set': fight})
        return fight



    @staticmethod
    async def take_quest(hero_id, quest_id):
        await Collection.takequests.insert_one({
            "hero_id" : bson.ObjectId(hero_id),
            "quest_id" : bson.ObjectId(quest_id),
            "time_end" : "",
            "status" : "open",
            "resources" : {}
        })
        
    @staticmethod
    async def close_quest(hero_id, quest_id):
        date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')
        quest = await Collection.takequests.update_one({
            "hero_id" : bson.ObjectId(hero_id),
            "quest_id" : bson.ObjectId(quest_id)
            }, {'$set': {
                "time_end" : date,
                "status" : "done"
                }
            })

    @staticmethod
    async def update_quest(hero_id, quest_id, resources):
        quest = await Collection.takequests.update_one({
            "hero_id" : bson.ObjectId(hero_id),
            "quest_id" : bson.ObjectId(quest_id)
            }, {'$set': {
                "resources" : resources
                }
            })       
            
    @staticmethod
    async def get_taked_quest(quest_id, field="_id", filter = {}):
    
        if type(quest_id) != list:
            quest_id = [bson.ObjectId(quest_id)]
            
        filter[field] = {"$in": quest_id}  
        
        quests = await Collection.takequests.find(filter).to_list(None)
        
        return quests


    @staticmethod
    async def get_quest(quest_id):
        if type(quest_id) != list:
            quest_id = [bson.ObjectId(quest_id)]
        quests = await Collection.quests.find({"_id": {"$in": quest_id}}).to_list(None)
        return quests


    @staticmethod
    async def get_mobs(mob_id = None):
    
        if mob_id is None:
            mobs = await Collection.mobs.find({}).to_list(None)
            return mobs
        
        if type(mob_id) != list:
            mob_id = [bson.ObjectId(mob_id)]
        else:
            mob_id = [bson.ObjectId(i) for i in mob_id]
            
        mobs = await Collection.mobs.find({"_id": {"$in": mob_id}}).to_list(None)

        return mobs
        
    @staticmethod
    async def get_resources(resource_id):
        if type(resource_id) != list:
            resource_id = [bson.ObjectId(resource_id)]
        else:
            resource_id = [bson.ObjectId(i) for i in resource_id]
        resources = await Collection.resources.find({"_id": {"$in": resource_id}}).to_list(None)
        return resources
    
    @staticmethod
    async def get_equipments(equipped_id):
        if type(equipped_id) != list:
            equipped_id = [bson.ObjectId(equipped_id)]
        else:
            equipped_id = [bson.ObjectId(i) for i in equipped_id]
        equipments = await Collection.equipments.find({"_id": {"$in": equipped_id}}).to_list(None)
        return equipments
        
    @staticmethod
    async def get_player_equipments(hero_id, equipment_type = None, equipment_id = None):
            
        pipeline = [
            {
                '$lookup': {
                    'from': 'equipments',
                    'localField': 'equipment_id',
                    'foreignField': '_id',
                    'as': 'equipments'
                }
            },
            {
                '$unwind': {
                    'path': '$equipments',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$match': {
                    'hero_id': bson.ObjectId(hero_id)
                }
            }
        ]
        
        if equipment_id:
            pipeline[2]['$match']['_id'] = bson.ObjectId(equipment_id)
        
        if equipment_type:
            pipeline[2]['$match']['equipments.type'] = equipment_type
            

        equipments = await Collection.playerequipments.aggregate(pipeline).to_list(None)
        return equipments
        
    @staticmethod
    async def update_player_equipments(equipment_id, equipment):
        if equipment.get("_id"):
            equipment.pop("_id")
            
        await Collection.playerequipments.update_one({"_id" : equipment_id}, {"$set" : equipment})
        
    @staticmethod
    async def add_player_equipments(hero_id, equipment_id):
        equipment = await Db.get_equipments(bson.ObjectId(equipment_id))

        if len(equipment) <= 0:
            return None
            
        equipment = equipment[0]
        await Collection.playerequipments.insert_one({
                "hero_id" : bson.ObjectId(hero_id),
                "equipment_id" : bson.ObjectId(equipment_id),
                "solidity_free" : equipment["solidity"],
                "max_solidity" : equipment["solidity"],
                "count" : equipment["count"]
        })
        
    @staticmethod
    async def delete_player_equipments(equipment_id):
         await Collection.playerequipments.delete_one({"_id" : bson.ObjectId(equipment_id)})
            
    @staticmethod
    async def add_quest_resource(resource, user_id):    
        take_quests = await Db.get_taked_quest(user_id, "hero_id", filter = {"status" : "open"})
        
        resource = str(resource)

        for i in range(len(take_quests)):
            quest = await Db.get_quest(take_quests[i]["quest_id"])
             
            if len(quest) <= 0:
                continue
                
            quest = quest[0]
            
            if type(quest["countMobs"]) is dict:
                if resource not in quest["countMobs"].keys():
                    if "all" in quest["countMobs"].keys():
                        if "all" in take_quests[i]["resources"].keys():
                            if take_quests[i]["resources"]["all"] >= quest["countMobs"]["all"]:
                                continue
                            take_quests[i]["resources"]["all"] += 1
                        else:
                            take_quests[i]["resources"]["all"] = 1
                            
                        await Db.update_quest(user_id, take_quests[i]["quest_id"], take_quests[i]["resources"])
                    continue
                
                
        
                if resource in take_quests[i]["resources"].keys():
                    if take_quests[i]["resources"][resource] >= quest["countMobs"][resource]:
                        continue
                        
                    take_quests[i]["resources"][resource] += 1
                else:
                    take_quests[i]["resources"][resource] = 1
                
                    
                await Db.update_quest(user_id, take_quests[i]["quest_id"], take_quests[i]["resources"])
            
    @staticmethod
    async def update_hero(hero_id, hero):   
        msg = None
        update_location = False
        if "_id" in hero.keys():
            hero.pop("_id")
        if 'experience' in hero.keys():
            levels = Db.get_levels()
            if hero['experience'] > levels[hero['level']]:
                if hero['level'] != list(levels.keys())[-1]:
                    profile = await Collection.profile.find_one({"_id": hero['profile_id']})
                    telegram_id = profile['telegram_id']
                    location = await Db.get_locations_info([hero['location_ref']])
                    location = location[0]

                    update_location = True
                    
                    hero['patterns']['points'] += 5
                    hero['level'] += 1
                    msg = f"У вас новый уровень {hero['level']}"

        
        await Collection.hero.update_one({'_id': hero_id},
        {'$set': hero})
        
        if update_location:
            await Db.update_location(telegram_id, location['name'])
        
        return msg
        
    @staticmethod
    async def update_hero_hp():
        heroes = await Collection.hero.find({}).to_list(None)
        for hero in heroes:
            if hero["hp_free"] < hero["hp"]:
                hero["hp_free"] += 1
                await Db.update_hero(hero['_id'], hero)

    
    @staticmethod
    def get_levels():
        return {
            1 : 50,
            2 : 150,
            3 : 350,
            4 : 650,
            5 : 1250,
            6 : 2150,
            7 : 3450,
            8 : 5150,
            9 : 7350,
            10 : 10350,
            11 : 14350,
            12 : 19550,
            13 : 26150,
            14 : 34350,
            15 : 44350,
            16 : 56550,
            17 : 71350,
            18 : 89150,
            19 : 110350,
            20 : 135350
      } 
