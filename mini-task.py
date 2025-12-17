from queue import Queue
import threading
import numpy as np
import time

def consumer_operation(tup):
    size, value, times = tup
    matrix = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            matrix[i, j] = value ** (i + j)
    matrix = np.linalg.matrix_power(matrix, times)
    return np.sum(matrix)

class Producer(threading.Thread):
    def __init__(self, stack, task_num, lock):
         super().__init__()
         self.task = stack
         self.num_tasks = task_num
         self.lock = lock
    
    def run(self):
        for i in range(1, self.num_tasks + 1):
            task = (i * 2, 2, 2)
            self.task.put(task)
            with self.lock:
                print(f'Producer add task {i} with size: {i}, value: {2}, powered to: {2}')
            
        
        for _ in range(self.num_tasks):
            with self.lock:
                self.task.put(None)
    

class Consumer(threading.Thread):
    def __init__(self, id, stack, results, lock):
        super().__init__()
        self.consumer_id = id
        self.stack = stack
        self.results = results
        self.count = 0
        self.lock = lock
    

    def run(self):
        while True:
            task = self.stack.get()
            if task is None:
                self.stack.put(None)
                with self.lock:
                    print(f'Consumer {self.consumer_id} finished. Completed {self.count} tasks')
                break

            start = time.time()
            result = consumer_operation(task)
            execution_time = time.time() - start
            with self.lock:
                self.results.append((self.consumer_id, task, result, execution_time))
                print(f'Consumer {self.consumer_id}: '
                      f'task: {task}, result: {result}, time: {execution_time}')
            
            self.count += 1


def main_run(num_consumers, num_tasks):
    task_queue = Queue()
    lock = threading.Lock()
    results = []
    producer = Producer(task_queue, num_tasks, lock)
    consumers = []
    for i in range(num_consumers):
        consumer = Consumer(i + 1, task_queue, results, lock)
        consumers.append(consumer)
    
    start = time.time()
    producer.start()
    for consumer in consumers:
        consumer.start()
    producer.join()
    for consumer in consumers:
        consumer.join()
    total = time.time() - start

    print(f'Total tasks completed: {num_tasks} '
          f'Total consumers: {num_consumers} '
          f'Total time: {total:.4f}')
    
    consumer_stats = {}
    for consumer_id, task, result, proc_time in results:
        if consumer_id not in consumer_stats:
            consumer_stats[consumer_id] = {'count': 0, 'total_time': 0}
        consumer_stats[consumer_id]['count'] += 1
        consumer_stats[consumer_id]['total_time'] += proc_time
    
    for consumer_id, stats in consumer_stats.items():
        print(f"Consumer {consumer_id}: "
              f"{stats['count']} tasks, "
              f"total time: {stats['total_time']:.4f}, "
              f"average time: {stats['total_time']/stats['count']:.4f}")
    
    return total, consumer_stats


main_run(20, 500)