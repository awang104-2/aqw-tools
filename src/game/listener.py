from packets.sniffing import Sniffer
from json import loads, dumps
import toml
import os


backend_path = os.path.join(os.path.dirname(__file__), 'config', 'backend.toml')


class GameListener(Sniffer):

    with open(backend_path, 'r') as file:
        backend = toml.load(file)
    aqw_servers = backend['AQW']['SERVERS']
    packet_types = backend['AQW']['PACKETS']

    @staticmethod
    def get_servers():
        return GameListener.aqw_servers.copy()

    @staticmethod
    def get_server_names():
        return list(GameListener.aqw_servers.keys())

    @staticmethod
    def get_server_ips():
        return list(GameListener.aqw_servers.values())

    def __init__(self, server):
        if server not in self.get_server_names() and server not in self.get_server_ips():
            raise ValueError('Not a valid server.')
        server = self.aqw_servers.get(server, server)
        super().__init__(f'tcp and src host {server}')
        self.buffer = ''

    def __update_buffer(self):
        while not self.packets.empty():
            raw = get_raw(self.packets.get())
            blist = parse_bytes(raw)
            slist = decode(blist)
            for s in slist:
                self.buffer += s

    def __reset_buffer(self):
        self.buffer = ''

    def __parse_buffer(self):
        start, end, start_bracket_count, end_bracket_count = (0, 0, 0, 0)
        for i, char in enumerate(self.buffer):
            if char == '{':
                if start_bracket_count == 0:
                    start = i
                start_bracket_count += 1
            elif char == '}':
                end_bracket_count += 1
                if start_bracket_count == end_bracket_count != 0:
                    end = i
                    result, self.buffer = self.buffer[start:end + 1], self.buffer[end + 1:]
                    return result
        raise ValueError('Incomplete or incompatible string for JSON object parsing: ' + self.buffer)

    def reset(self):
        super().reset()
        self.__reset_buffer()

    def log_packet(self, packet):
        if packet.haslayer(Raw):
            super().log_packet(packet=packet)

    def set_server(self, server):
        server = self.aqw_servers.get(server, server)
        bpf_filter = f'tcp and src host {server}'
        super().set_bpf_filter(bpf_filter)

    def get_jsons(self, include=None, exclude=None, save=None):
        if include and exclude:
            raise ValueError('Cannot specify both \'include\' and \'exclude\'.')

        self.__update_buffer()
        jsons = []

        while True:
            try:
                json_string = self.__parse_buffer()
                entry = loads(json_string)['b']['o']
                if not (include or exclude) or (include and entry.get('cmd', '') in include) or (exclude and not entry.get('cmd', '') in exclude):
                    jsons.append(entry)
            except ValueError:
                if save:
                    with open(save, "w") as outfile:
                        for e in jsons:
                            outfile.write(dumps(e) + '\n')
                return jsons
            except KeyError:
                print('error -', json_string)

    def get_sorted_jsons(self, *args, **kwargs):
        sorted_jsons = {}
        jsons = self.get_jsons(*args, **kwargs)
        for json in jsons:
            cmd = json.get('cmd')
            if cmd == 'addGoldExp' and json.get('typ') == 'm':
                cmd = 'addGoldExpM'
            if sorted_jsons.get(cmd):
                sorted_jsons[cmd].append(jsons)
            else:
                sorted_jsons[cmd] = [json]
        return sorted_jsons

    def print_jsons(self, include=None, exclude=None):
        results = self.get_jsons(include=include, exclude=exclude)
        print('\nPrinting results:')
        for i, dictionary in enumerate(results):
            print(f'{i + 1} - {dictionary}')