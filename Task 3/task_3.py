"""
Найти и исправить ошибку (смотри вложенный файл "task_3.py"), оставив многопоточность.
"""
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock


class GlobalLikeVar:
    def __init__(self, value: int):
        self.value = value
        self.__lock = Lock()

    def increase(self, arg: int):
        for _ in range(arg):
            with self.__lock:
                self.value += 1

    def __repr__(self):
        return f'{self.value}'


def main():
    a = GlobalLikeVar(0)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(5):
            executor.submit(a.increase, 1000000)

    print("----------------------", a)  # ???


if __name__ == "__main__":
    main()
