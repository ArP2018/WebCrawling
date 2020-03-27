import time

from apscheduler.schedulers.blocking import BlockingScheduler


def do_something():
    print('doing something')
    time.sleep(20)


if __name__ == '__main__':
    s = BlockingScheduler()
    s.add_job(do_something, 'interval', seconds=5)

    try:
        do_something()
        s.start()
    except:
        s.shutdown()
