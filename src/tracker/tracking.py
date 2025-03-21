from packets.sniffing import AqwPacketLogger
from threading import Event, Thread
from time import sleep


class Tracker:

    data_types = ['addItems', 'dropItem', 'addGoldExp', 'mtls']

    def __init__(self, server):
        self.logger = AqwPacketLogger(server)
        self.running = Event()
        self.live_tracking_thread = None
        self.drops = {}
        self.kills = {}

    def __str__(self):
        return 'Drops: ' + str(self.drops) + '\n' + 'Kills: ' + str(self.kills)

    def print_server_list(self):
        servers = self.logger.get_servers()
        for i, server_name in enumerate(list(servers.keys())):
            print(f'{i + 1}: {server_name}')

    def set_server(self, server):
        self.logger.set_server(server)

    def track(self):
        self.running.set()
        while self.running.is_set():
            dataset = self.logger.get_jsons(include=self.data_types)
            for data in dataset:
                self.interpret(data)
            sleep(0.1)
        print('\n' + str(self))

    def interpret(self, data):
        copy = None
        match data.get('cmd'):
            case 'dropItem' | 'addItems':
                item_num = list(data.get('items').keys())[0]
                if self.drops.get(item_num, None):
                    self.drops[item_num]['count'] += data.get('items').get(item_num).get('iQty')
                else:
                    num = data.get('items').get(item_num).get('iQty')
                    name = data.get('items').get(item_num).get('sName', 'unknown')
                    self.drops[item_num] = {'name': name, 'count': num}
                copy = self.drops.copy()
            case 'mtls':
                monster_id = data.get('id')
                if self.kills.get(monster_id, None):
                    self.kills[monster_id] += 1
                else:
                    self.kills[monster_id] = 1
                copy = self.kills.copy()
        return copy

    def run(self):
        self.logger.start()
        self.live_tracking_thread = Thread(target=self.track)
        self.live_tracking_thread.run()

    def start(self):
        self.logger.start()
        self.live_tracking_thread = Thread(target=self.track, daemon=True)
        self.live_tracking_thread.start()

    def stop(self, join=False):
        self.running.clear()
        self.logger.stop(join=join)
        if join:
            self.live_tracking_thread.join()

