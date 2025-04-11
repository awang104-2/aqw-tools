from game.mechanics.items import *


inventory = Inventory()
inventory.add(item_id=-99999, name='Test Item 2', quantity=1)
inventory.save()
inventory.merge_config()

