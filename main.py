from os import listdir

from Classes.Logger import Logger

from Classes.Footlocker import Footlocker


def main():
    log = Logger().log

    log('Starting tasks', color='magenta')
    threads = []
    i = 0
    for task in listdir('tasks'):
        threads.append(Footlocker(i, 'tasks/{}'.format(task)))
        threads[i].start()
        i += 1






if __name__ == '__main__':
    main()
