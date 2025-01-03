from pyautogui import *


im = screenshot(region=(600, 600, 600, 400))
im.show()
exit(1)


path = 'tester_img.png'
top, left, width, height = locateOnScreen(path, confidence=0.9)
parameters = (int(top), int(left), width, height)
im = screenshot(region=parameters)
im.show()
