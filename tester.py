from autoclicker import AutoClicker
from actions import Move

autoclicker = AutoClicker()
move = Move(autoclicker, rooms=3, start_room=1)
move.move()
move.move()
move.move()
