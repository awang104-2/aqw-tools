from src.handlers.ImageHandler import load_image, get_screenshot_of_window, find_best_match
from src.bot import parse_res_to_tuple
from time import sleep
import os


def get_dir_from_res(resolution):
    package_path = os.path.dirname(__file__)
    dir_path = os.path.join(package_path, 'assets', resolution)
    return dir_path


class Quest:

    def __init__(self, autoclicker, resolution, name=None, quest_id=None):
        if not (quest_id or name):
            raise ValueError('Must specify the quest ID or the name of the quest.')

        self.autoclicker = autoclicker
        self.drops = {}
        self.requirements = {}
        self.quest_log_open = False
        self.quest_id = {'QuestID': 384, 'sName': 'Ninja Challenge'}
        self.resolution = parse_res_to_tuple(resolution)
        self.search_dir = get_dir_from_res(resolution)

    def __call__(self, packet):
        cmd = packet.get('cmd')
        match cmd:
            case 'addItems':
                self.update(packet)
            case 'ccqr':
                self.reset(packet)
        return cmd

    def update(self, packet):
        if packet.get('cmd') != 'addItems':
            raise ValueError('Must be an \'addItems\' packet.')

        key = list(self.packet.get('items').keys())[0]
        if key in list(self.drops.keys()):
            data = self.packet.get('items').get(key)
            self.drops[key] += data.get('iQty')

    def quest_status(self):
        return self.drops == self.condition

    def open_log(self):
        if not self.quest_log_open:
            self.quest_log_open = True
            self.autoclicker.press('l')
            sleep(0.75)

    def close_log(self):
        if self.quest_log_open:
            self.quest_log_open = False
            self.autoclicker.press('l')
            sleep(0.75)

    def open_quest(self):
        x, y = 0, int(self.resolution[1] / 2)
        width, height = int(self.resolution[0] / 2), int(self.resolution[1] / 2)
        main_image = get_screenshot_of_window(self.autoclicker.get_hwnd())
        template = load_image(self.search_dir + '\\' + 'complete')
        top_left, bot_right, _ = find_best_match(main_image=main_image, template=template, region=(x, y, width, height))
        loc = (top_left + bot_right) / 2
        self.autoclicker.click(loc)
        sleep(0.75)



class Combat:

    classes = ['archmage', 'am', 'arcana invoker', 'ai']

    def __init__(self, cls):
        if cls.lower() not in Combat.classes:
            raise ValueError('Find')
        self.cls = cls.lower()



