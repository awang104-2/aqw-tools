from game.game_sniffer import GameSniffer
from pynput.keyboard import Listener, Key
from game.interpreter import Interpreter
from game.character import Character
import threading
import time


def on_release(key, interpreter, sniffer):
    if key == Key.esc:
        interpreter.stop()
        sniffer.stop()
        time.sleep(1.5)
        print(threading.enumerate())
        return False


def interpreter_test():
    game_sniffer = GameSniffer(server='twig')
    character = Character(class_name='lr', haste=0.5, quest_names=[], location='battleon-1')
    interpreter = Interpreter(character=character, sniffer=game_sniffer)
    function = lambda key: on_release(key, interpreter, game_sniffer)
    listener = Listener(on_release=function)
    listener.start()
    interpreter.start()
    game_sniffer.run()


if __name__ == '__main__':
    interpreter_test()