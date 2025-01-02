from pyautogui import *


path = 'tester_img.png'
top, left, width, height = locateOnScreen(path, confidence=0.9)
parameters = (int(top), int(left), width, height)
im = screenshot(region=parameters)
im.show()
