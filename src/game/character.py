from game.mechanics import Combat, Quests, Inventory


class Character:

    def __init__(self, *, quest_names=(), location='battleon', haste=0.5, cls='lr', ):
        self.combat = Combat(cls=cls, haste=haste)
        self.quest = Quests.from_names(quest_names)
        self.drops = Inventory()


