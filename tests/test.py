from scapy.all import IP, TCP, send, sniff, conf
from threading import Thread
from time import sleep


# Callback function for when a packet is sniffed
def packet_callback(pkt):
    print(f"[Sniffed] {pkt.summary()}")

# Send a dummy TCP packet to localhost (loopback)
def send_dummy_packet():
    packet = IP(dst="127.0.0.1") / TCP(dport=12345, sport=54321, flags="S")
    send(packet, verbose=False)
    print("[Sent] Dummy TCP packet to 127.0.0.1:12345")

# Run the sniffer (filter ensures we catch only our dummy packet)
def sniff_dummy_packet():
    print("[Sniffing] Waiting for packet...")
    sniff(
        iface="\\Device\\NPF_Loopback",  # change to your loopback interface if needed (see below)
        filter="tcp and dst port 12345",
        prn=packet_callback,
        count=1,
        store=False
    )

if __name__ == "__main__":
    # Optional: check available interfaces if "lo" doesn't work
    # print(get_if_list())  # Uncomment to list interfaces
    # print(conf.iface)
    t1 = Thread(target=sniff_dummy_packet)
    t2 = Thread(target=send_dummy_packet)
    t1.start()
    sleep(0.5)
    t2.start()
    sleep(0.5)
    t2.join()
    t1.join()
