from handlers.DataHandler import add_data_to_csv
from pynput.keyboard import Listener, Key
from network.sniffing import GameSniffer
from bot.autoclicker import AutoClicker
from threading import Thread
from time import sleep

def auto_combat(packet_logger, combo=('1', '2', '3', '4', '5')):
    def combat_loop():
        while packet_logger.running:
            autoclicker = AutoClicker()
            for key in combo:
                autoclicker.press(key)
                sleep(0.1)
    return Thread(target=combat_loop)


def get_player_data(packet):



def on_release(key, packet_logger):
    if key == Key.esc:
        packet_logger.stop()
        return False


def keyboard_listener(packet_logger):
    return Listener(on_release=lambda key: on_release(key, packet_logger))


def sample(server, count=2000, combo=(4, 3, 5)):
    game_sniffer = GameSniffer(server=server)
    autocombat = auto_combat(game_sniffer, combo=combo)
    listener = keyboard_listener(game_sniffer)
    game_sniffer.start()
    autocombat.start()





def get_player_data(packet_logger, count):
    player_total, player_hit, player_crit, player_dodge, player_miss = (0, 0, 0, 0, 0)
    results = packet_logger.get(include=['ct'])
    for result in results:
        infos = result.get('sarsa', None)
        if not infos:
            continue
        else:
            infos = infos[0].get('a')
        for info in infos:
            hit_type = info.get('type')
            if hit_type == 'hit':
                player_hit += 1
                player_total += 1
            elif hit_type == 'crit':
                player_crit += 1
                player_total += 1
            elif hit_type == 'dodge':
                player_dodge += 1
                player_total += 1
            elif hit_type == 'miss':
                player_miss += 1
                player_total += 1
        if player_total == count:
            break
    return {'hit': [player_hit], 'crit': [player_crit], 'dodge': [player_dodge], 'miss': [player_miss], 'total': [player_total], 'p': [player_crit / player_total]}


def get_monster_data(packet_logger, count):
    monster_total, monster_hit, monster_crit, monster_dodge, monster_miss = (0, 0, 0, 0, 0)
    results = packet_logger.get_jsons(include=['ct'])
    for result in results:
        infos = result.get('sara')
        if not infos:
            continue
        for info in infos:
            hit_type = info.get('actionResult').get('type')
            match hit_type:
                case 'hit':
                    monster_hit += 1
                    monster_total += 1
                case 'crit':
                    monster_crit += 1
                    monster_total += 1
                case 'dodge':
                    monster_dodge += 1
                    monster_total += 1
                case 'miss':
                    monster_miss += 1
                    monster_total += 1
        if monster_total == count:
            break
    return {'hit': [monster_hit], 'crit': [monster_crit], 'dodge': [monster_dodge], 'miss': [monster_miss], 'total': [monster_total], 'p': [monster_crit / monster_total]}


def get_data(lvl, cls, pexp, server, time, combo, count):
    packet_logger, time = sample(server, time, combo)
    p_data = get_player_data(packet_logger, count)
    p_data['level'], p_data['class'], p_data['pexp'] = lvl, cls, pexp
    return p_data


def run_test(lvl, cls, pexp, server, time, combo, count, filename, location):
    data = get_data(lvl, cls, pexp, server, time, combo, count)
    add_data_to_csv(filename, location, data)




def main():
    game_sniffer = GameSniffer('twig')
    thread = Thread(target=processing_thread, args=[game_sniffer])
    game_sniffer.start()
    thread.start()
    listener = Listener(on_release=lambda key: on_release(key, game_sniffer))
    listener.run()
