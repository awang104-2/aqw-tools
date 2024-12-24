from autoclicker import AutoClicker


class Bot:

    def __init__(self, routine=['1', '2', '3', '4', '5']):
        self.routine = routine
        self.autoclicker = AutoClicker()
        self.step = 0

    def action(self):
        N = len(self.routine)
        self.autoclicker.press(self.routine[self.step])
        self.step = (self.step + 1) % N

