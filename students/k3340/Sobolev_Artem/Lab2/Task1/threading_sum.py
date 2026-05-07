import threading
import time
import os


N = 10_000_000_000_000
WORKERS = os.cpu_count() or 4


def calculate_sum(start: int, end: int) -> int:
    return (start + end) * (end - start + 1) // 2


def split_range(n: int, parts: int) -> list[tuple[int, int]]:
    chunk_size = n // parts
    ranges = []

    start = 1

    for i in range(parts):
        end = start + chunk_size - 1

        if i == parts - 1:
            end = n

        ranges.append((start, end))
        start = end + 1

    return ranges


def worker(index: int, start: int, end: int, results: list[int]) -> None:
    results[index] = calculate_sum(start, end)


def main() -> None:
    ranges = split_range(N, WORKERS)
    results = [0] * WORKERS
    threads = []

    start_time = time.perf_counter()

    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(
            target=worker,
            args=(index, start, end, results)
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)

    end_time = time.perf_counter()

    print("Многопоточность")
    print(f"Количество потоков: {WORKERS}")
    print(f"Результат: {total}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    main()