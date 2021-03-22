from utils.profiling.timer import Timer
from time import sleep


def work():
    timer = Timer('A')
    for _ in range(1000):
        timer.start()
        sleep(1)
        timer.stop()


if __name__ == "__main__":
    work()
