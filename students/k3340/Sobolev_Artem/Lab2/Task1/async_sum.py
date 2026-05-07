import asyncio
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


async def calculate_sum_async(start: int, end: int) -> int:
    await asyncio.sleep(0)
    return calculate_sum(start, end)


async def main_async() -> None:
    ranges = split_range(N, WORKERS)

    start_time = time.perf_counter()

    tasks = [
        asyncio.create_task(calculate_sum_async(start, end))
        for start, end in ranges
    ]

    results = await asyncio.gather(*tasks)

    total = sum(results)

    end_time = time.perf_counter()

    print("Асинхронность")
    print(f"Количество задач: {WORKERS}")
    print(f"Результат: {total}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()