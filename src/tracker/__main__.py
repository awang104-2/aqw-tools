from tracker.tracking import Tracker
from pynput.keyboard import Key, Listener


def on_release(key):
    if key == Key.esc:
        tracker.stop()
        return False


tracker = Tracker(server=None)
server = input('Server > ').lower()
if server != 'exit':
    tracker.set_server(server)
    listener = Listener(on_release=on_release)
    listener.start()
    tracker.run()



