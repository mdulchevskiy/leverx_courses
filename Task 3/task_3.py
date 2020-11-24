"""
Найти и исправить ошибку (смотри вложенный файл "task_3.py"), оставив многопоточность.
"""
from threading import (Thread,
                       Lock, )

a = 0
lock = Lock()


def function(arg):
    global a
    lock.acquire()
    try:
        for _ in range(arg):
            a += 1
    finally:
        lock.release()


def main():
    threads = []
    for i in range(5):
        thread = Thread(target=function, args=(1000000,))
        thread.start()
        threads.append(thread)

    [t.join() for t in threads]
    print("----------------------", a)  # ???


if __name__ == "__main__":
    main()
