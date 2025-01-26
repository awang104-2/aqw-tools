import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
top_level = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(top_level)
top_level += '\\'
current_dir += '\\'
