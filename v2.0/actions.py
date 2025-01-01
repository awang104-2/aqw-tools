import time
from handlers import ImageHandler
import numpy as np


# Completes quests.
class Quest:
    def __init__(self, autoclicker, num_quests=1, max_quests=99, reward=None):
        self.autoclicker = autoclicker
        self.max_quests = max_quests
        self.num_quests = num_quests
        self.reward = reward

    def locate_on_screen(self, image_path, take_screenshot=True, screen=None):
        if take_screenshot:
            screen = self.get_screen()
        image = ImageHandler.load_image(image_path)
        try:
            top_left, bottom_right = ImageHandler.check_images(screen, image, confidence=0.7)
            location = np.astype((np.array(top_left) + np.array(bottom_right)) / 2, int)
            return location
        except ImageHandler.ImageNotFound as e:
            location = np.array([])
            return location

    def get_screen(self):
        hwnd = self.autoclicker.get_hwnd()
        return ImageHandler.get_screenshot_of_window(hwnd)

    def complete_quest(self):
        def open_quest_log():
            self.autoclicker.press('l')
            time.sleep(1)

        def close_quest_log():
            self.autoclicker.press('l')

        def find_and_click_quest():
            log_complete_path = '/assets/quest/general/log_complete.png'
            coordinates = self.locate_on_screen(log_complete_path)
            if any(coordinates):
                self.autoclicker.click(coordinates)
                time.sleep(1)
                find_and_click_reward()
            else:
                time.sleep(0.25)

        def find_and_click_reward():
            log_complete_path = '/assets/quest/totem.png'
            coordinates = self.locate_on_screen(log_complete_path)
            if any(coordinates):
                self.autoclicker.click(coordinates)
                time.sleep(0.25)
            find_and_click_turn_in()

        def find_and_click_turn_in():
            turn_in_path = '/assets/quest/general/turn_in.png'
            coordinates = self.locate_on_screen(turn_in_path)
            self.autoclicker.click(coordinates)
            time.sleep(1)
            find_and_type_num_quests()

        def find_and_type_num_quests():
            num_path = '/assets/quest/general/quest_number.png'
            coordinates = self.locate_on_screen(num_path)
            if any(coordinates):
                self.autoclicker.click(coordinates)
                time.sleep(0.25)
                self.autoclicker.press('{BACKSPACE}')
                time.sleep(0.25)
                self.autoclicker.type(str(self.max_quests))
                time.sleep(0.25)
                self.autoclicker.press('{ENTER}')
                time.sleep(0.5)
                find_and_click_yes()

        def find_and_click_yes():
            yes_path = '/assets/quest/general/yes.png'
            coordinates = self.locate_on_screen(yes_path)
            self.autoclicker.click(coordinates)
            time.sleep(0.25)

        open_quest_log()
        for i in range(self.num_quests):
            find_and_click_quest()
            if i < self.num_quests - 1:
                time.sleep(1)
        close_quest_log()


class Class:

    dot = {
        'combos': [[2, 3, 4, 3, 5, 3], [2, 3, 5, 4, 3]],
        'gcd': 1
    }
    lr = {
        'combos': [[2, 3, 4, 5], [2, 3, 4, 5]],
        'gcd': 0.25
    }
    am = {
        'combos': [[2, 4, 3], [2, 4, 2, 4, 3]],
        'gcd': 0.8
    }

    def __init__(self, class_):
        self.combos = class_['combos']
        self.gcd = class_['gcd']

    def get_combos(self):
        return self.combos

    def get_combo(self, n):
        return self.combos[n]

    def get_gcd(self):
        return self.gcd


# Automates combat by sending keystroke combos
class Combat:

    dot = Class(Class.dot)
    lr = Class(Class.lr)
    am = Class(Class.am)

    def __init__(self, autoclicker, class_params=dot):
        self.combos = class_params.get_combos()
        self.combo = self.combos[0]
        self.delay = class_params.get_gcd()
        self.autoclicker = autoclicker

    def use_ability(self):
        self.autoclicker.press(str(self.combo[0]))
        self.combo = self.combo[1:] + [self.combo[0]]
        time.sleep(self.delay)

    # 0 for farming, 1 for boss
    def swap_combos(self, mode=0):
        self.combo = self.combos[mode]


class MoveParams:

    unbound_thread = {
        'arrows': [[(1800, 650)], [(1800, 800), (100, 200)], [(1800, 800), (1000, 850)],
                   [(1800, 750), (100, 750)], [(1000, 850), (1000, 850)]],
        'room times': [150, 80, 0, 0, 390],
        'move times': [1, 4, 2.5, 4, 1]
    }

    willpower = {
        'arrows': [[(1800, 500)], [(1800, 800), (90, 580)], [(100, 800)]],
        'room times': [105, 70, 165],
        'move times': [0.5, 3.5, 0.5]
    }

    prismatic_seams = {
        'arrows': [[(1800, 400)], [(1800, 800), (90, 200)]],
        'room times': [500, 0],
        'move times': [0.5, 0.5]
    }

    garish_remnant = {
        'arrows': [[(1800, 650)], [(1800, 400), (100, 650)], [(100, 650)]],
        'room times': [110, 40, 300],
        'move times': [0.5, 3.5, 0.5]
    }

    acquiescence = {
        'arrows': [[(100, 650)], [(900, 150), ], [(1100, 700), (100, 500)], [(1800, 500), (1100, 700)], [(1800, 300), (100, 700)], [(100, 650)]],
        'room times': [300, 150, 0, 0, 0, 500],
        'move times': [0.5, 3, 1.75, 1.75, 4, 0.5]
    }

    nul_totem = {
        'arrows': [[(900, 650)], [(900, 650)]],
        'room times': [300, 150, 0, 0, 0, 500]
    }

    def __init__(self, params):
        self.room_times = params['room times']
        self.move_times = params['move times']
        self.room_arrows = params['arrows']

    def get_room_times(self):
        return self.room_times

    def get_move_times(self):
        return self.move_times

    def get_arrows(self):
        return self.room_arrows


class Move:

    def __init__(self, autoclicker, rooms, room_times, start_room=1):
        self.autoclicker = autoclicker
        self.rooms = rooms
        self.current_room = start_room
        self.room_times = room_times
        self.direction = 'right'
        self.__coordinates = {'left': (100, 450), 'right': (1800, 700)}

    def move(self):
        if self.current_room == self.rooms:
            self.direction = 'left'
        elif self.current_room == 1:
            self.direction = 'right'
        self.autoclicker.press('{SPACE}')
        if self.direction == 'right':
            self.autoclicker.click(self.__coordinates[self.direction])
            self.current_room += 1
        elif self.direction == 'left':
            self.autoclicker.click(self.__coordinates[self.direction])
            self.current_room -= 1
        time.sleep(2)

    def get_room_time(self):
        if self.rooms == 0:
            return None
        return self.room_times[self.current_room - 1]


# Automates movement from room to room. Depends on the quest.
class Movement:

    unbound_thread = MoveParams(MoveParams.unbound_thread)
    willpower = MoveParams(MoveParams.willpower)
    prismatic_seams = MoveParams(MoveParams.prismatic_seams)
    garish_remnant = MoveParams(MoveParams.garish_remnant)
    acquiescence = MoveParams(MoveParams.acquiescence)
    # nul_totem = MoveParams(MoveParams.nul_totem)

    def __init__(self, autoclicker, direction=0, current_room=0, move_params=unbound_thread):
        self.autoclicker = autoclicker
        self.current_room = current_room
        self.direction = direction

        self.room_times = move_params.get_room_times()
        self.move_times = move_params.get_move_times()
        self.room_arrows = move_params.get_arrows()

    def move_rooms(self):
        self.autoclicker.press('{SPACE}')
        if self.current_room == len(self.room_arrows) - 1:
            self.direction = -1
        elif self.current_room == 0:
            self.direction = 0
        coordinates = self.room_arrows[self.current_room][self.direction]
        time.sleep(0.25)
        self.autoclicker.click(coordinates)
        time.sleep(0.15)
        self.autoclicker.press('x')
        t = self.move_times[self.current_room]
        if self.direction == -1:
            self.current_room -= 1
        elif self.direction == 0:
            self.current_room += 1
        time.sleep(t)

    def get_room_time(self):
        return self.room_times[self.current_room]

    def get_last_room(self):
        return len(self.room_arrows) - 1



