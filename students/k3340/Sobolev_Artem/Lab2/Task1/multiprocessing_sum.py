import multiprocessing
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


def calculate_sum_for_range(args: tuple[int, int]) -> int:
    start, end = args
    return calculate_sum(start, end)


def main() -> None:
    ranges = split_range(N, WORKERS)

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=WORKERS) as pool:
        results = pool.map(calculate_sum_for_range, ranges)

    total = sum(results)

    end_time = time.perf_counter()

    print("Многопроцессность")
    print(f"Количество процессов: {WORKERS}")
    print(f"Результат: {total}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    main()