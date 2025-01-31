class Player:

    def __init__(self, bot):
        self.bot = bot
        self.combat_params = {'routine': ['1', '2', '3', '4', '5'], 'step': 0, 'delay': 0.25}
        self.quest_params = {'delays': [0.8, 0.8, 0.5, 0.2, 0.5, 0.5, 0.2],  'step': 0}
        self.collector_params = {'confidence': 0.8, 'delay': 0.5}
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()

    def fight(self):
        self.autoclicker.press(self.combat_params['routine'][self.combat_params['step']])
        self.combat_params['step'] = (self.combat_params['step'] + 1) % len(self.combat_params['routine'])
        return self.combat_params['delay']

    def collect_items(self):
        img1 = get_screenshot_of_window(self.hwnd)
        img2 = load_image(paths['relic'])
        top_left, bottom_right, max_val = find_best_match(img1, img2)
        if max_val >= self.collector_params['confidence']:
            coordinates = ((top_left + bottom_right) / 2).astype(int)
            coordinates[0] += 250
            self.autoclicker.click(coordinates)
        return self.collector_params['delay']