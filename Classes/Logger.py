from time import strftime

from termcolor import colored

from colorama import init


class Logger:
    def __init__(self, tid=None):
        self.tid = tid
        init()

    def set_tid(self, tid):
        self.tid = tid

    def log(self, text, color=None, timestamp=True):
        if color is not None:
            text = colored(text, color)
        if self.tid is not None:
            text = '[{}] :: {}'.format(self.tid, text)
        if timestamp:
            print('[{}] {}'.format(strftime('%H:%M:%S'), text))
        else:
            print(text)
