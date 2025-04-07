from game.combat import CombatKit
from threading import Thread
import time


def attack_and_wait(combat_kit, key):
    combat_kit.attack(key)
    start_time = time.time()
    combat_kit.wait([key])
    end_time = time.time()
    print(end_time - start_time)


def speed_up(combat_kit, delay, haste):
    time.sleep(delay)
    combat_kit.haste = haste


def main():
    combat_kit = CombatKit.load('lr')
    t1 = Thread(target=attack_and_wait, args=(combat_kit, None))
    t2 = Thread(target=speed_up, args=(combat_kit, 6, 0.5))
    t1.start()
    t2.run()


if __name__ == '__main__':
    main()