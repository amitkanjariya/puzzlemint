"""Measure CPU-only puzzle generation and validation. Run from repository root."""

from statistics import median
from time import perf_counter

from app.engine import generate, validate_game


def main():
    for count in (4, 6, 8):
        times = []
        for seed in range(30):
            config = {"theme": "museum", "difficulty": "medium", "puzzle_count": count, "random_seed": seed}
            start = perf_counter()
            specs = generate(config)
            puzzles = [{**spec, "id": str(index), "dependencies": [] if index == 0 else [str(index - 1)]}
                for index, spec in enumerate(specs)]
            errors = validate_game(puzzles)
            if errors:
                raise RuntimeError(f"Generated game failed validation: {errors}")
            times.append((perf_counter() - start) * 1000)
        times.sort()
        print(f"{count} puzzles: median {median(times):.1f} ms; p95 {times[28]:.1f} ms; max {times[-1]:.1f} ms (n=30)")


if __name__ == "__main__":
    main()
