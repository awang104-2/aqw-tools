from handlers.ImageHandler import *
from autoclicker import AutoClicker

relic = '../assets/quest/supplies/relic_of_chaos.png'
complete = '../assets/quest/general/log_complete.png'

autoclicker = AutoClicker()
hwnd = autoclicker.get_hwnd()
img1 = get_screenshot_of_window(hwnd)
img2 = load_image(complete)
top_left, bottom_right, max_val = find_best_match(img1, img2)
coordinates = ((top_left + bottom_right) / 2).astype(int)
print(coordinates)
autoclicker.click(coordinates)
