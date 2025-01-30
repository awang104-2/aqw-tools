from src.handlers.ImageHandler import load_image, get_screenshot_of_window, find_best_match
from src.bot import parse_res_to_tuple
import os


def get_dir_from_res(resolution):
    match resolution:
        case '1920x1080':
            return


class Quest:

    def __init__(self, autoclicker, name, resolution):
        self.autoclicker = autoclicker
        self.log_open = False
        self.stackable = False
        self.drops = {'2024': 0}
        self.condition = {'2024': 3}
        self.quest_log_open = True
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

    def close_log(self):
        if self.quest_log_open:
            self.quest_log_open = False
            self.autoclicker.press('l')

    def open_quest(self):
        x, y = 0, int(self.resolution[1] / 2)
        width, height = int(self.resolution[0] / 2), int(self.resolution[1] / 2)

        main_image = get_screenshot_of_window(self.autoclicker.get_hwnd())
        template = load_image()
        find_best_match(img1, img, region=(x, y, width, height))

    def reset(self, packet):
        if packet.get('cmd') != 'ccqr':
            raise ValueError('Must be a \'ccqr\' packet.')

        if self.quest_id.get('QuestID') == packet.get('QuestID') or self.quest_id.get('sName') == packet.get('sName'):
            for key in self.drops.keys():
                self.drops[key] = 0

    def open_img(self):

        dir = os.path.abspath()
        load_image()

    def do_quest(self):
        step = self.quest_params['step']
        match step:
            case 0:
                self.autoclicker.press('l')
            case 1:
                self.autoclicker.click((604, 263))
            case 2:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['turn in'])
                top_left, bottom_right, _ = find_best_match(img1, img2, region=(0, 0, 900, 900))
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 3:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['number'])
                top_left, bottom_right, max_val = find_best_match(img1, img2, region=(400, 300, 800, 800))
                if max_val > 0.8:
                    coordinates = ((top_left + bottom_right) / 2).astype(int)
                    self.autoclicker.click(coordinates)
                else:
                    self.quest_params['step'] += 1
            case 4:
                self.autoclicker.type('9999')
            case 5:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['yes'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 6:
                self.autoclicker.press('l')
        self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
        return self.quest_params['delays'][step]
