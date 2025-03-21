import tomllib
import os


config_path = os.path.join(os.path.dirname(__file__), 'config')
quests_config_path = os.path.join(config_path, 'quests.toml')
drops_config_path = os.path.join(config_path, 'drops.toml')
classes_config_path = os.path.join(config_path, 'classes.toml')
drops_samples_config_path = os.path.join(config_path, 'sampling.toml')

with open(quests_config_path, 'rb') as f:
    quest_config = tomllib.load(f)
with open(drops_config_path, 'rb') as f:
    drop_config = tomllib.load(f)
with open(classes_config_path, 'rb') as f:
    class_config = tomllib.load(f)


def find_config(filepath):
    os.path.dirname(filepath)
    pass


def load():
    pass
