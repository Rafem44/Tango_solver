#!/usr/bin/env python3
"""
Test puzzle from OCR V2 detection
"""

from tango_solver_v5 import TangoGridV5, TangoSolverV5


def create_puzzle_from_ocr():
    """Create puzzle from OCR V2 detected values"""
    grid = TangoGridV5(6, 6)

    # Values detected by OCR V2
    ocr_values = [
        (0, 2, 1),  # 🟠
        (1, 4, 0),  # 🌙
        (1, 5, 0),  # 🌙
        (2, 2, 1),  # 🟠
        (2, 3, 0),  # 🌙
        (3, 3, 0),  # 🌙
        (4, 5, 1),  # 🟠
        (5, 4, 1),  # 🟠
        (5, 5, 1),  # 🟠
    ]

    for row, col, value in ocr_values:
        grid.set_cell(row, col, value)

    # TODO: Add constraints manually if needed
    # For now, try to solve with just the values

    return grid


def display_grid(grid):
    """Display grid"""
    for r in range(grid.rows):
        row_str = ' '.join(['.' if grid.get_cell(r, c) is None
                           else str(grid.get_cell(r, c))
                           for c in range(grid.cols)])
        print(f"  {row_str}")


def main():
    print("=" * 70)
    print("TEST: Puzzle from OCR V2 Detection")
    print("=" * 70)
    print()

    grid = create_puzzle_from_ocr()

    print("Initial grid (from OCR):")
    display_grid(grid)
    print()

    print("Solving with V5...")
    solver = TangoSolverV5(grid)
    solved, iterations, time_ms = solver.solve(max_iterations=50)

    print("\nSolution:")
    display_grid(grid)
    print()

    filled = sum(1 for r in range(6) for c in range(6) if grid.get_cell(r, c) is not None)

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✓ Solved: {solved}")
    print(f"📊 Filled: {filled}/36 ({filled*100//36}%)")
    print(f"🔄 Iterations: {iterations}")
    print(f"⏱️  Time: {time_ms:.4f} ms")
    print()

    if not solved:
        print("⚠️  Puzzle not completely solved.")
        print("   Contraintes = et × probablement nécessaires!")
        print("   Ajoutez-les manuellement ou améliorez la détection.")


if __name__ == "__main__":
    main()
