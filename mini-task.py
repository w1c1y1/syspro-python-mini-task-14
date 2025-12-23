from queue import Queue
import threading
import time

num_consumers = 10
num_tasks = 30


def matrix_mult(a, b):
    n = len(a)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += a[i][k] * b[k][j]
    return result


def matrix_pow(mat, n):
    if n == 0:
        size = len(mat)
        return [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    result = mat
    for _ in range(n - 1):
        result = matrix_mult(result, mat)
    return result


def consumer_operation(task):
    size, value, times = task
    matrix = [[value ** (i + j) for j in range(1, size + 1)] for i in range(1, size + 1)]
    return matrix_pow(matrix, times)

class Producer(threading.Thread):
    def __init__(self, queue, num_tasks):
        super().__init__()
        self.queue = queue
        self.num_tasks = num_tasks

    def run(self):
        for i in range(1, self.num_tasks + 1):
            task = (i * 2, 2, 8)
            self.queue.put(task)


class Consumer(threading.Thread):
    def __init__(self, queue, consumer_id):
        super().__init__()
        self.queue = queue
        self.consumer_id = consumer_id

    def run(self):
        while True:
            task = self.queue.get()
            if task is None:
                break
            result = consumer_operation(task)
            print(f"Consumer {self.consumer_id}: обработана матрица {len(result)}x{len(result)}")


def main():
    global num_tasks
    global num_consumers

    queue = Queue()

    producer = Producer(queue, num_tasks)
    consumers = [Consumer(queue, i) for i in range(num_consumers)]

    start = time.time()
    producer.start()
    for consumer in consumers:
        consumer.start()

    producer.join()
    for _ in range(num_consumers):
        queue.put(None)

    for consumer in consumers:
        consumer.join()

    print(f"Время выполнения: {time.time() - start:.2f} сек")


main()