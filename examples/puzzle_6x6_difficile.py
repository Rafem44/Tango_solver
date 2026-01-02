#!/usr/bin/env python3
"""
6×6 Tango puzzle from the mobile app (Niveau DIFFICILE)

Grid mapping (Orange 🟠 = 1, Blue 🌙 = 0):
Row 0: . . . . . .
Row 1: . × . . 🟠 🟠
Row 2: 🟠 🌙 . . . ×
Row 3: . = . . 🌙 🌙
Row 4: 🌙 🌙 . . . ×
Row 5: . = . . 🟠 🌙
"""

from tango_solver_simple import TangoGridSimple, TangoSolverSimple, Constraint


def create_6x6_difficile():
    """Create the 6×6 DIFFICILE puzzle from the app screenshot

    Reading from the image carefully:
    Row 0: . . . . . .
    Row 1: . [×] . . 🟠 🟠  (× between cols 0-1)
    Row 2: 🟠 🌙 . . . [×]  (× vertical between rows 2-3 at col 5)
    Row 3: . [=] . . 🌙 🌙  (= between cols 0-1)
    Row 4: 🌙 🌙 . . . [×]  (× vertical between rows 4-5 at col 5)
    Row 5: . [=] . . 🟠 🌙  (= between cols 0-1)
    """
    grid = TangoGridSimple(6, 6)

    # Initial values (Orange 🟠 = 1, Blue 🌙 = 0)
    # Row 1
    grid.set_cell(1, 4, 1)  # 🟠
    grid.set_cell(1, 5, 1)  # 🟠

    # Row 2
    grid.set_cell(2, 0, 1)  # 🟠
    grid.set_cell(2, 1, 0)  # 🌙

    # Row 3
    grid.set_cell(3, 4, 0)  # 🌙
    grid.set_cell(3, 5, 0)  # 🌙

    # Row 4
    grid.set_cell(4, 0, 0)  # 🌙
    grid.set_cell(4, 1, 0)  # 🌙

    # Row 5
    grid.set_cell(5, 4, 1)  # 🟠
    grid.set_cell(5, 5, 0)  # 🌙

    # Horizontal constraints
    # Row 1: × between (1,0) and (1,1)
    grid.add_constraint(1, 0, 1, 1, "×")

    # Row 3: = between (3,0) and (3,1)
    grid.add_constraint(3, 0, 3, 1, "=")

    # Row 5: = between (5,0) and (5,1)
    grid.add_constraint(5, 0, 5, 1, "=")

    # Vertical constraints (× on the right side)
    # Between rows 2-3 at column 5: (2,5) × (3,5)
    grid.add_constraint(2, 5, 3, 5, "×")

    # Between rows 4-5 at column 5: (4,5) × (5,5)
    grid.add_constraint(4, 5, 5, 5, "×")

    return grid


def display_grid(grid):
    """Display the grid in a readable format"""
    for r in range(grid.rows):
        row_str = ' '.join(['.' if grid.get_cell(r, c) is None
                           else str(grid.get_cell(r, c))
                           for c in range(grid.cols)])
        print(row_str)


def main():
    print("=" * 70)
    print("6×6 TANGO PUZZLE - NIVEAU DIFFICILE")
    print("=" * 70)
    print()

    grid = create_6x6_difficile()

    # Count initial cells
    initial_count = sum(1 for r in range(6) for c in range(6)
                       if grid.get_cell(r, c) is not None)

    print(f"Initial: {initial_count}/36 cells")
    print(f"Constraints: {len(grid.constraints)} (= and ×)")
    print()

    print("Initial grid:")
    display_grid(grid)
    print()

    # Solve
    print("=" * 70)
    print("SOLVING...")
    print("=" * 70)
    print()

    solver = TangoSolverSimple(grid)
    solved, iterations, time_ms = solver.solve(max_iterations=50)

    print("Solution grid:")
    display_grid(grid)
    print()

    filled_count = sum(1 for r in range(6) for c in range(6)
                      if grid.get_cell(r, c) is not None)

    print(f"✓ Solved: {solved}")
    print(f"📊 Filled: {filled_count}/36 ({filled_count*100//36}%)")
    print(f"🔄 Iterations: {iterations}")
    print(f"⏱️  Time: {time_ms:.4f} ms")
    print()
    print(f"Progress: +{filled_count - initial_count} cells solved")
    print()


if __name__ == "__main__":
    main()
