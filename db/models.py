from db.db_start import Collection


class Model:
    class Profile:
        def __init__(self, telegram_id, telegram_name, telegram_lang, nickname, telegram_last_online, telegram_referral_id, telegram_referrals, telegram_is_active, telegram_source_from, telegram_created_at, premium_coins, is_banned, ban_date, action_count, current_hero, is_premium, premium_date, max_count_heroes):
            self.telegram_id = telegram_id
            self.telegram_name = telegram_name
            self.telegram_lang = telegram_lang
            self.telegram_last_online = telegram_last_online
            self.telegram_referral_id = telegram_referral_id
            self.telegram_referrals = telegram_referrals
            self.telegram_is_active = telegram_is_active
            self.telegram_source_from = telegram_source_from
            self.telegram_created_at = telegram_created_at
            self.premium_coins = premium_coins
            self.nickname = nickname
            self.is_banned = is_banned
            self.ban_date = ban_date
            self.action_count = action_count
            self.current_hero = current_hero
            self.is_premium = is_premium
            self.premium_date = premium_date
            self.max_count_heroes = max_count_heroes
            
        def to_dict(self):
            return {
                "telegram_id": self.telegram_id,
                "telegram_name": self.telegram_name,
                "telegram_lang": self.telegram_lang,
                "telegram_last_online": self.telegram_last_online,
                "telegram_referral_id": self.telegram_referral_id,
                "telegram_referrals": self.telegram_referrals,
                "telegram_is_active": self.telegram_is_active,
                "telegram_source_from": self.telegram_source_from,
                "telegram_created_at": self.telegram_created_at,
                "premium_coins": self.premium_coins,
                "nickname" : self.nickname,
                "is_banned" : self.is_banned,
                "ban_date" : self.ban_date,
                "action_count" : self.action_count,
                "current_hero" : self.current_hero,
                "is_premium" : self.is_premium,
                "premium_date" : self.premium_date,
                "max_count_heroes" : self.max_count_heroes
                
            }
            
    
    class Hero:
        def __init__(self, profile_id, nickname, gender, energy, state, level, speed, location_ref, experience, fame, money, hp, hp_free, patterns, resources, equipped, techniques, faction, craft, background, action_count, karma, locations_visited):
            self.profile_id = profile_id
            self.nickname = nickname
            self.gender = gender
            self.energy = energy
            self.speed = speed
            self.state = state
            self.level = level
            self.location_ref = location_ref
            self.experience = experience
            self.fame = fame
            self.money = money
            self.hp = hp
            self.hp_free = hp_free
            self.patterns = patterns
            self.resources = resources
            self.equipped = equipped
            self.techniques = techniques
            self.faction = faction
            self.craft = craft
            self.background = background
            self.action_count = action_count
            self.karma = karma
            self.locations_visited = locations_visited
            
        def to_dict(self):
            return {
                "profile_id" : self.profile_id,
                "nickname" : self.nickname,
                "gender": self.gender,
                "energy": self.energy,
                "speed" : self.speed,
                "state": self.state,
                "level": self.level,
                "location_ref": self.location_ref,
                "experience": self.experience,
                "fame": self.fame,
                "money": self.money,
                "hp": self.hp,
                "hp_free": self.hp_free,
                "patterns": self.patterns,
                "resources" : self.resources,
                "equipped": self.equipped,
                "techniques": self.techniques,
                "faction": self.faction,
                "craft": self.craft,
                "background": self.background,
                "action_count" : self.action_count,
                "karma" : self.karma,
                "locations_visited" : self.locations_visited
            }
            
            
    class Location:
        def __init__(self, min_level, request_quests, is_event, is_city, npc, nearest_locations, name, about, image):
            self.min_level = min_level
            self.request_quests = request_quests
            self.is_event = is_event
            self.is_city = is_city
            self.npc = npc
            self.nearest_locations = nearest_locations
            self.name = name
            self.about = about
            self.image = image

        def to_dict(self):
            return {
                "min_level": self.min_level,
                "request_quests" : self.request_quests,
                "is_event": self.is_event,
                "is_city": self.is_city,
                "npc": self.npc,
                "nearest_locations": self.nearest_locations,
                "name": self.name,
                "about": self.about,
                "image": self.image
            }

    class Npc:
        def __init__(self, name, about, image, resources, tasks):
            self.name = name
            self.about = about
            self.image = image
            self.resources = resources
            self.tasks = tasks

        def to_dict(self):
            return {
                "name": self.name,
                "about": self.about,
                "image": self.image,
                "npc": self.npc,
                "resources": self.resources,
                "tasks": self.tasks
            }

    class Fight:
        def __init__(self, users_refs, with_npc, battles, winner_ref):
            self.users_refs = users_refs
            self.with_npc = with_npc
            self.battles = battles
            self.winner_ref = winner_ref

        def to_dict(self):
            return {
                "users_refs": self.users_refs,
                "with_npc": self.with_npc,
                "battles": self.battles,
                "winner_ref": self.winner_ref,
            }
            
    class Resources:
        def __init__(self, name, about, typeName, command, probability, image):
            self.name = name
            self.about = about
            self.type = typeName
            self.command = command
            self.probability = probability
            self.image = image

        def to_dict(self):
            return {
                "name": self.name,
                "about": self.about,
                "type": self.type,
                "command": self.command,
                "probability": self.probability,
                "image": self.image
            }
            
    class Equipments:
        def __init__(self, name, about, typeName, craft, level, solidity, armor, patronDamage, weaponDamage, distanceModifier, criticalDamagePower, criticalDamageProbability, strenght, endurance, dexterity, accuracy, luck, probability, count, image):
            self.name = name
            self.about = about
            self.type = typeName
            self.craft = craft
            self.level = level
            self.solidity = solidity
            self.armor = armor
            self.patronDamage = patronDamage
            self.weaponDamage = weaponDamage
            self.distanceModifier = distanceModifier
            self.criticalDamagePower = criticalDamagePower
            self.criticalDamageProbability = criticalDamageProbability
            self.strenght = strenght
            self.endurance = endurance
            self.dexterity = dexterity
            self.accuracy = accuracy
            self.luck = luck
            self.probability = probability
            self.count = count
            self.image = image

        def to_dict(self):
            return {
                "name" : self.name,
                "about" : self.about,
                "type" : self.type,
                "craft" : self.craft,
                "level" : self.level,
                "solidity" : self.solidity,
                "armor" : self.armor,
                "patronDamage" : self.patronDamage,
                "weaponDamage" : self.weaponDamage,
                "distanceModifier" : self.distanceModifier,
                "criticalDamagePower" : self.criticalDamagePower,
                "criticalDamageProbability" : self.criticalDamageProbability,
                "strenght" : self.strenght,
                "endurance" : self.endurance,
                "dexterity" : self.dexterity,
                "accuracy" : self.accuracy,
                "luck" : self.luck,
                "probability" : self.probability,
                "count" : self.count,
                "image" : self.image
            }
            
    class PlayerEquipments:
        def __init__(self, hero_id, equipment_id, solidity_free, max_solidity, count):
            self.hero_id = hero_id
            self.equipment_id = equipment_id
            self.solidity_free = solidity_free
            self.max_solidity = max_solidity
            self.count = count
            
        def to_dict(self):
            return {
                "hero_id" : self.hero_id,
                "equipment_id" : self.equipment_id,
                "solidity_free" : self.solidity_free,
                "max_solidity" : self.max_solidity,
                "count" : self.count
            }
            
    class Quests:
        def __init__(self, name, beginText, endText, typeName, npc1, npc2, requiredQuest, level, countMobs, countResources, money, experience, rewardItem, location, highMeetChance, Race):
            self.name = name
            self.beginText = beginText
            self.endText = endText
            self.type = typeName
            self.npc1 = npc1
            self.npc2 = npc2
            self.requiredQuest = requiredQuest
            self.level = level
            self.countMobs = countMobs
            self.countResources = countResources
            self.money = money
            self.experience = experience
            self.rewardItem = rewardItem
            self.location = location
            self.highMeetChance = highMeetChance
            self.background = background
            
        def to_dict(self):
            return {
                "name" : self.name,
                "beginText" : self.beginText,
                "endText" : self.endText,
                "type" : self.type,
                "npc1" : self.npc1,
                "npc2" : self.npc2,
                "requiredQuest" : self.requiredQuest,
                "level" : self.level,
                "countMobs" : self.countMobs,
                "countResources" : self.countResources,
                "money" : self.money,
                "experience" : self.experience,
                "rewardItem" : self.rewardItem,
                "location" : self.location,
                "highMeetChance" : self.highMeetChance,
                "background" : self.background
            }
            
    class TakeQuests:
        def __init__(self, hero_id, quest_id, time_end, status, resources):
            self.hero_id = hero_id
            self.quest_id = quest_id
            self.time_end = time_end
            self.status = status
            self.resources = resources
            
        def to_dict(self):
            return {
                "hero_id" : self.hero_id,
                "quest_id" : self.quest_id,
                "time_end" : self.time_end,
                "status" : self.status,
                "resources" : self.resources
            }
            
            
    class Mobs:
        def __init__(self, name, about, location_ref, weight, level, hp, patterns, armor, helmet, gun, pouch, experience, money, reception, image, drop):
            self.name = name
            self.about = about
            self.location_ref = location_ref
            self.weight = weight
            self.level = level
            self.hp = hp
            self.patterns = patterns
            self.armor = armor
            self.helmet = helmet
            self.gun = gun
            self.pouch = pouch
            self.experience = experience
            self.money = money
            self.reception = reception
            self.image = image
            self.drop = drop


        def to_dict(self):
            return {
                "name" : self.name,
                "about" : self.about,
                "location_ref" : self.location_ref,
                "weight" : self.weight,
                "level" : self.level,
                "hp" : self.hp,
                "patterns" : self.patterns,
                "armor" : self.armor,
                "helmet" : self.helmet,
                "gun" : self.gun,
                "pouch" : self.pouch,
                "experience" : self.experience,
                "money" : self.money,
                "reception" : self.reception,
                "image" : self.image,
                "drop" : self.drop
            }
            
    class Routes:
        def __init__(self, id_start, id_end, time):
            self.id_start = id_start
            self.id_end = id_end
            self.time = time


        def to_dict(self):
            return {
                "id_start" : self.id_start,
                "id_end" : self.id_end,
                "time" : self.time
            }
            
    class Trades:
        def __init__(self, trade_id, npc_id, currency, price):
            self.trade_id = trade_id
            self.npc_id = npc_id
            self.currency = currency
            self.price = price


        def to_dict(self):
            return {
                "trade_id" : self.trade_id,
                "npc_id" : self.npc_id,
                "currency" : self.currency,
                "price" : self.price
            }

    class Effects:
        def __init__(self, resource_id, command, lifetime, hp, now_hp, strength, endurance, agility, accuracy, luck, armor, helmet, speed_transfer):
            self.resource_id = resource_id
            self.command = command
            self.lifetime = lifetime
            self.hp = hp
            self.now_hp = now_hp
            self.strength = strength
            self.endurance = endurance
            self.agility = agility
            self.accuracy = accuracy
            self.luck = luck
            self.armor = armor
            self.helmet = helmet
            self.speed_transfer = speed_transfer
            
        def to_dict(self):
            return {
                "resource_id" : self.resource_id,
                "command" : self.command,
                "lifetime" : self.lifetime,
                "hp" : self.hp,
                "now_hp" : self.now_hp,
                "strength" : self.strength,
                "endurance" : self.endurance,
                "agility" : self.agility,
                "accuracy" : self.accuracy,
                "luck" : self.luck,
                "armor" : self.armor,
                "helmet" : self.helmet,
                "speed_transfer" : self.speed_transfer
            }
