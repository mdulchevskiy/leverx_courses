"""
Найти и исправить ошибку (смотри вложенный файл "task_3.py"), оставив многопоточность.
"""
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock

a = 0
lock = Lock()


def function(arg):
    global a
    for _ in range(arg):
        with lock:
            a += 1


def main():
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(5):
            executor.submit(function, 1000000)

    print("----------------------", a)  # ???


if __name__ == "__main__":
    main()
