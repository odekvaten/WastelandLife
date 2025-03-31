from PIL import Image
from io import BytesIO 

def create_image(equipped):
    image = Image.open("images/equipment/inventory.png")
    if equipped.get("gun_1"):
        gun_1 = Image.open("images/equipment/images/gun1.png")
        image = merge_image(image, gun_1, (100, 296))
    if equipped.get("gun_2"):
        gun_2 = Image.open("images/equipment/images/gun2.png")
        image = merge_image(image, gun_2, (70, 30))
    if equipped.get("patrons"):    
        ammo = Image.open("images/equipment/images/ammo.png")
        image = merge_image(image, ammo, (100, 444))
    if equipped.get("armor"):
        armor = Image.open("images/equipment/images/armor.png")
        image = merge_image(image, armor, (805, 236))
    if equipped.get("helmet"):
        helmet = Image.open("images/equipment/images/helmet.png")
        image = merge_image(image, helmet, (805, 56))
    if equipped.get("cold_gun_1"):
        knife = Image.open("images/equipment/images/knife.png")
        image = merge_image(image, knife, (790, 626))
    if equipped.get("pocket"):
        stimulator = Image.open("images/equipment/images/stimulator.png")
        image = merge_image(image, stimulator, (160, 617))
        image = merge_image(image, stimulator, (160, 766))
    
    buff = BytesIO()
    image.save(buff, "PNG")
    buff.seek(0)
    return buff

def merge_image(img1, img2, position):
    img2 = img2.resize((144, 144))

    img1.paste(img2, position)

    return img1
