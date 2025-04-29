from scapy.all import sniff
from network.sending import *
from time import sleep
from threading import Thread


def stop(packet):
    if packet.haslayer(Raw) and packet[Raw].load == b'STOP SNIFFING':
        return True
    return False


def callback(packet):
    print(packet)


def sniffer():
    host_name, ip_address = get_host()
    bpf_filter = f'udp and dst host {ip_address} and dst port {DEFAULT_PORT}'
    print(bpf_filter)
    sniff(filter=bpf_filter, prn=callback, store=0, stop_filter=stop)
    # sniff(iface='\\Device\\NPF_Loopback', filter=bpf_filter, prn=callback, store=0, stop_filter=stop)


def send():
    sleep(0.25)
    print('sending')
    send_dummy_packet(local=False, payload=b'First message.', verbose=False)
    sleep(0.25)
    print('sending')
    send_dummy_packet(local=False, payload=b'Second message.', verbose=False)
    sleep(0.25)
    print('sending')
    send_dummy_packet(local=False, payload=b'STOP SNIFFING', verbose=False)


def main():
    t1 = Thread(target=sniffer)
    t2 = Thread(target=send)
    t1.start()
    t2.start()
    t2.join()
    t1.join()


if __name__ == '__main__':
    main()