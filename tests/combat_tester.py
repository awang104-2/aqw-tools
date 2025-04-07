from game.combat import CombatKit
from threading import Thread
import time


def main():
    combat_kit = CombatKit.load('lr', 0.5)
    attack('5', combat_kit)

def attack(key, combat_kit):
    start_time = time.time()
    combat_kit.attack(key)
    current_time = time.time()
    print(f'{current_time - start_time:.4}s')
    combat_kit.wait(key)
    combat_kit.attack(key)
    current_time = time.time()
    print(f'{current_time - start_time:.4}s')


if __name__ == '__main__':
    main()