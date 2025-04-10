from network.processing import Processor
from pynput.keyboard import Listener, Key
from network.sniffing import Sniffer
from game.game_sniffer import GameSniffer
from network.layers import Raw
from time import sleep
from game.aqw_backend import AQW_SERVERS


def on_release(key, sniffer, processor):
    if key == Key.esc:
        processor.stop()
        sniffer.stop()
        return False
    elif key == Key.ctrl_l:
        pass


def processor_with_game_sniffer(server):
    sniffer = GameSniffer(server=server)
    listener = Listener(on_release=lambda key: on_release(key, sniffer, processor))
    processor = Processor(sniffer=sniffer)
    sniffer.start()
    processor.start()
    # processor.print.set()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    sleep(1)
    print('Finished.')


def get_and_print_packet_kills(processor):
    packet = processor.get_packet()['b']['o']
    if packet.get('cmd') == 'addGoldExp' and packet.get('typ') == 'm':
        print(packet)


def get_and_print_packet_combat(processor):
    packet = processor.get_packet()['b']['o']
    if packet.get('cmd') == 'ct' and packet.get('sarsa'):
        try:
            print(packet['sarsa'][0]['a'])
        except Exception as e:
            raise e.add_note(f'Packet - {packet['sarsa']}')


def raw_processor(server):
    twig_ip = AQW_SERVERS.get(server.lower())
    bpf_filter = f'tcp and (src host {twig_ip} or dst host {twig_ip})'
    sniffer = Sniffer(bpf_filter, [Raw], False)
    listener = Listener(on_release=lambda key: on_release(key, sniffer, processor))
    processor = Processor(sniffer=sniffer)
    processor.print.set()
    # processor.get_and_print_packet = lambda: get_and_print_packet_combat(processor)
    sniffer.start()
    processor.start()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    processor.join()
    print('Finished.')


def sAct_test():
    dictionary = {'t': 'xt', 'b': {'r': -1, 'o': {'cmd': 'sAct', 'actions': {'passive': [
        {'tgtMin': 1, 'id': 2122, 'icon': 'i,i,i,i,i,Gunop1', 'ref': 'p1', 'nam': 'Reinforced Chamber', 'mp': 0,
         'tgtMax': 1, 'desc': 'Your high-tech parts allow you to shoot faster and more powerful shots for +10% damage.',
         'auras': [{}], 'isOK': True, 'range': 301, 'fx': 'w', 'tgt': 'h', 'typ': 'passive', 'cd': 2000},
        {'tgtMin': 1, 'id': 2123, 'icon': 'i,i,i,i,i,Gunop1', 'ref': 'p2', 'nam': 'Sharpshooter', 'mp': 0, 'tgtMax': 1,
         'desc': 'You pinpoint critical weaknesses with ease, granting you +10% Crit Chance.', 'auras': [{}],
         'isOK': True, 'range': 301, 'fx': 'w', 'tgt': 'h', 'typ': 'passive', 'cd': 2000},
        {'tgtMin': 1, 'id': 2124, 'icon': 'i,i,i,i,i,Gunop1', 'ref': 'p3', 'nam': 'Blessed Ammunition', 'mp': 0,
         'tgtMax': 1, 'desc': '+20% Luck.', 'auras': [{}], 'isOK': True, 'range': 301, 'fx': 'w', 'tgt': 'h',
         'typ': 'passive', 'cd': 2000}], 'active': [{'anim': 'GunAttack3', 'auraCheck': 'Bang', 'nam': 'Fire!',
                                                     'desc': "Fire as fast as you can pull the trigger! Your shots are so fast that they're unavoidable. Your cylinder holds 6 shots, needing to be reloaded when empty.",
                                                     'forceResult': 'noMiss', 'range': 401, 'isOK': True, 'fx': 'w',
                                                     'dsrc': 'Hours1', 'id': 2117, 'checkQty': 5, 'DmgFct': 2,
                                                     'strl': 'sp_qchronoa1v2', 'storedID': 2636, 'tgtMin': 1,
                                                     'icon': 'i,i,i,i,i,Gunoaa', 'mp': 15, 'tgtMax': 1,
                                                     'auras': [{}, {}, {}, {}, {}], 'damage': 1.15, 'applyAura': 0,
                                                     'ref': 'aa', 'removeAura': 'Bang', 'auto': True, 'tgt': 'h',
                                                     'typ': 'p', 'cd': 200},
                                                    {'tgtMin': 1, 'icon': 'i,i,i,i,i,Gunoa1', 'nam': 'Reload',
                                                     'auraCheck': 'Temporal Rift', 'mp': -1000, 'anim': 'Cast3',
                                                     'tgtMax': 1, 'forceResult': 'crit',
                                                     'desc': 'Load 6 shots into your revolver and refill your mana. Removes Tracer rounds and FMJ rounds.\r\n\r\nIf you have 4 or more stacks of Temporal Rift, consume them and enter Gunslinger Stance for 2 seconds, granting you free shots and generating Chaos Rifts, which block Temporal Rift and increase your Crit Damage by 20% per stack for 10 seconds.',
                                                     'isOK': True, 'range': 301, 'auras': [{}, {}], 'fx': 'w',
                                                     'damage': 0, 'applyAura': 1, 'dsrc': 'Hours1', 'id': 2118,
                                                     'ref': 'a1', 'checkQty': 4, 'removeAura': 'Temporal Rift',
                                                     'tgt': 's', 'typ': 'ma', 'DmgFct': 2, 'strl': 'sp_cssa1',
                                                     'cd': 6000},
                                                    {'tgtMin': 1, 'id': 2119, 'icon': 'i,i,i,i,i,Gunoa2', 'ref': 'a2',
                                                     'nam': 'Tracer Rounds', 'mp': 5, 'tgtMax': 1,
                                                     'desc': 'Load Tracers and fire one, increasing your Defense by 20% and Dodge by 40% until you reload. Gain a Temporal Rift, stacking to 4 and lasting 10 seconds, and a HoT for 4 seconds based on max health. Replaces FMJ rounds.\r\n\r\nFiring with Tracer rounds Paints your opponent, reducing their damage, Dodge, and Crit Chance by 6% per stack, up to 4 stacks, for 16 seconds.',
                                                     'auras': [{}, {}, {}], 'isOK': True, 'range': 401, 'fx': 'w',
                                                     'tgt': 'h', 'typ': 'p', 'cd': 3000},
                                                    {'tgtMin': 1, 'icon': 'i,i,i,i,i,Gunoa3', 'nam': 'FMJ Rounds',
                                                     'mp': 5, 'tgtMax': 1,
                                                     'desc': "Load Full Metal Jackets and fire an empowered shot, dealing additional damage and increasing your Physical Damage by 25% until you reload. Gain a Temporal Rift, stacking to 4 and lasting 10 seconds. Replaces Tracer rounds.\r\n\r\nFiring with FMJ rounds shreds your opponent's defense by 6% per stack, up to 6 stacks, for 12 seconds.",
                                                     'auras': [{}, {}], 'isOK': True, 'range': 401, 'fx': 'w',
                                                     'damage': 1.7, 'dsrc': 'APSP2', 'id': 2120, 'ref': 'a3',
                                                     'tgt': 'h', 'typ': 'p', 'cd': 1500},
                                                    {'tgtMin': 1, 'icon': 'i,i,i,i,i,Gunoa4', 'mp': 0,
                                                     'anim': 'GunAttack3', 'nam': 'Silver Bullet', 'tgtMax': 1,
                                                     'desc': 'Fire a silver bullet, dealing powerful damage based on how much damage was dealt in the last 10 seconds while a Rift was present. Empties your rounds and Blinds your target, reducing their Hit Chance by 50% for 1 second.',
                                                     'isOK': True, 'range': 808, 'auras': [{}, {}], 'fx': 'w',
                                                     'damage': 0.3, 'dsrc': 'Chrono2', 'id': 2121, 'ref': 'a4',
                                                     'tgt': 'h', 'typ': 'p', 'strl': 'sp_cssa4', 'cd': 6000},
                                                    {'ref': 'i1', 'icon': 'icu1', 'mp': 0, 'anim': 'Cheer',
                                                     'nam': 'Potions',
                                                     'desc': 'Equip a potion or scroll from your inventory to use it here.',
                                                     'range': 808, 'isOK': True, 'fx': '', 'tgt': 'f', 'typ': 'i',
                                                     'strl': '', 'cd': 60000}]}}}}
    print('---------Abilities--------')
    sact = dictionary['b']['o'].get('actions').get('active')
    for action in sact:
        print(f'{action.get('nam')}: {float(action.get('cd')) / 1000}s')
    print('\n---------Passives---------')
    sact = dictionary['b']['o'].get('actions').get('passive')
    for action in sact:
        print(f'{action.get('nam')}')


if __name__ == '__main__':
    server = input('server > ').lower()
    # raw_processor(server)
    processor_with_game_sniffer(server)
