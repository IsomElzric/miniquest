"""
menu.py
Holds menu class for building the menus in the game.

by Alexander Turner
"""


from miniquest.option import Option


TEXT_PATH = "assets/text/"


class Menu:
    def __init__(self, title):
        self.title = title
        self.text = []
        self.options = []

    def load_text(self, menu, file):
        with open('{}{}/{}.txt'.format(TEXT_PATH, menu, file)) as f:
            self.text.append(f.readlines())

    def add_options(self, option_text):
        self.options.append(option_text)

    def output(self):
        print(self.text)
        print("")
        for option in self.options:
            print(option)

    def get_input(self, input):
        pass