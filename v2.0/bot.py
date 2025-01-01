from autoclicker import AutoClicker
from handlers.ImageHandler import *


paths = {
    'complete': '../assets/quest/general/complete.png',
    'relic': '../assets/quest/supplies/relic_of_chaos.png',
    'log complete': '../assets/quest/general/log_complete.png',
    'turn in': '../assets/quest/general/turn_in.png',
    'number': '../assets/quest/general/quest_number.png',
    'yes': '../assets/quest/general/yes.png'
}


class Bot:

    def __init__(self, routine=['1', '2', '3', '4', '5'], dt=100):
        self.combat_params = {'routine': routine, 'step': 0, 'delay': dt, 'size': len(routine)}
        self.quest_params = {'step': 5, 'delay': [1000, 1000, 1000, 1000, 1000, 1000 * 60 * 3], 'size': 6}
        self.autoclicker = AutoClicker()

    def fight(self):
        self.autoclicker.press(self.combat_params['routine'][self.combat_params['step']])
        self.combat_params['step'] = (self.combat_params['step'] + 1) % self.combat_params['size']
        return self.combat_params['delay']

    def check_screen(self):
        img1 = get_screenshot_of_window(self.hwnd, (0, 0, 1600, 500))
        img2 = load_image(paths['complete'])
        return is_image_on_screen(img1, img2, confidence=0.7)

    def do_quest(self):
        step = self.quest_params['step']
        hwnd = self.autoclicker.get_hwnd()
        match step:
            case 0:
                self.autoclicker.click((604, 263))
                """
                img1 = get_screenshot_of_window(hwnd, (0, 0, 900, 900))
                img2 = load_image(paths['log complete'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
                """
            case 1:
                img1 = get_screenshot_of_window(hwnd, (0, 0, 900, 900))
                img2 = load_image(paths['turn in'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 2:
                img1 = get_screenshot_of_window(hwnd)
                img2 = load_image(paths['number'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 3:
                self.autoclicker.type('100')
            case 4:
                img1 = get_screenshot_of_window(hwnd)
                img2 = load_image(paths['yes'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 5:
                pass
        dt = self.quest_params['delay'][step]
        self.quest_params['step'] = (self.quest_params['step'] + 1) % self.quest_params['size']
        return dt

    def collect_items(self, confidence):
        dt = 1000 * 60
        hwnd = self.autoclicker.get_hwnd()
        img1 = get_screenshot_of_window(hwnd)
        img2 = load_image(paths['relic'])
        top_left, bottom_right, max_val = find_best_match(img1, img2)
        if max_val >= confidence:
            coordinates = ((top_left + bottom_right) / 2).astype(int)
            coordinates[0] += 250
            self.autoclicker.click(coordinates)
        return dt

