#!/usr/bin/env python3
"""
Analyze why the 10x10 puzzle is not completely solved
"""

from puzzle_10x10_v3 import create_10x10_with_constraints
from tango_solver_v3 import TangoSolverV3


def analyze_grid(grid):
    """Detailed analysis of the grid state"""
    print("=" * 70)
    print("DETAILED GRID ANALYSIS")
    print("=" * 70)
    print()

    # Show grid
    print("Current grid state:")
    for r in range(grid.rows):
        row_str = ""
        for c in range(grid.cols):
            val = grid.get_cell(r, c)
            if val is None:
                row_str += " . "
            else:
                row_str += f" {val} "
        print(f"Row {r}: {row_str}")
    print()

    # Analyze each row
    print("ROW ANALYSIS:")
    print("-" * 70)
    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        count_0 = sum(1 for x in row if x == 0)
        count_1 = sum(1 for x in row if x == 1)
        count_empty = sum(1 for x in row if x is None)

        status = "✓ COMPLETE" if count_empty == 0 else f"⚠️  {count_empty} empty"
        balance = f"{count_0} zeros, {count_1} ones"

        print(f"Row {r}: {status:15} | {balance:20} | Need: 5 each")

        if count_empty > 0:
            # Show which columns are empty
            empty_cols = [c for c in range(grid.cols) if grid.get_cell(r, c) is None]
            print(f"        Empty columns: {empty_cols}")

            # Check if we can deduce anything
            if count_0 == 5:
                print(f"        → Row has 5 zeros already, remaining must be ONES")
            elif count_1 == 5:
                print(f"        → Row has 5 ones already, remaining must be ZEROS")
            else:
                needed_0 = 5 - count_0
                needed_1 = 5 - count_1
                print(f"        → Still need: {needed_0} zeros, {needed_1} ones")

    print()
    print("COLUMN ANALYSIS:")
    print("-" * 70)
    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        count_0 = sum(1 for x in col if x == 0)
        count_1 = sum(1 for x in col if x == 1)
        count_empty = sum(1 for x in col if x is None)

        status = "✓ COMPLETE" if count_empty == 0 else f"⚠️  {count_empty} empty"
        balance = f"{count_0} zeros, {count_1} ones"

        print(f"Col {c}: {status:15} | {balance:20} | Need: 5 each")

        if count_empty > 0:
            empty_rows = [r for r in range(grid.rows) if grid.get_cell(r, c) is None]
            print(f"        Empty rows: {empty_rows}")

            if count_0 == 5:
                print(f"        → Column has 5 zeros already, remaining must be ONES")
            elif count_1 == 5:
                print(f"        → Column has 5 ones already, remaining must be ZEROS")
            else:
                needed_0 = 5 - count_0
                needed_1 = 5 - count_1
                print(f"        → Still need: {needed_0} zeros, {needed_1} ones")

    print()
    print("CONSTRAINT VIOLATIONS CHECK:")
    print("-" * 70)

    violations = []

    # Check for three consecutive
    for r in range(grid.rows):
        for c in range(grid.cols - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r, c+1), grid.get_cell(r, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations.append(f"Row {r}, cols {c}-{c+2}: Three consecutive {vals[0]}s")

    for c in range(grid.cols):
        for r in range(grid.rows - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r+1, c), grid.get_cell(r+2, c)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations.append(f"Col {c}, rows {r}-{r+2}: Three consecutive {vals[0]}s")

    # Check explicit constraints
    for constraint in grid.constraints:
        r1, c1 = constraint.cell1
        r2, c2 = constraint.cell2
        val1 = grid.get_cell(r1, c1)
        val2 = grid.get_cell(r2, c2)

        if val1 is not None and val2 is not None:
            if constraint.type == "=" and val1 != val2:
                violations.append(f"Constraint {constraint.cell1} = {constraint.cell2} violated: {val1} ≠ {val2}")
            elif constraint.type == "×" and val1 == val2:
                violations.append(f"Constraint {constraint.cell1} × {constraint.cell2} violated: {val1} == {val2}")

    if violations:
        print("⚠️  VIOLATIONS FOUND:")
        for v in violations:
            print(f"  - {v}")
    else:
        print("✓ No constraint violations detected")

    print()
    print("SUMMARY:")
    print("-" * 70)
    total = grid.rows * grid.cols
    filled = sum(1 for r in range(grid.rows) for c in range(grid.cols) if grid.get_cell(r, c) is not None)
    empty = total - filled

    print(f"Total cells: {total}")
    print(f"Filled: {filled} ({filled/total*100:.1f}%)")
    print(f"Empty: {empty} ({empty/total*100:.1f}%)")
    print()

    # Find the "problematic zone"
    print("PROBLEMATIC ZONES (most empty cells):")
    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        empty_count = sum(1 for x in row if x is None)
        if empty_count > 0:
            empty_cols = [c for c in range(grid.cols) if grid.get_cell(r, c) is None]
            print(f"  Row {r}: {empty_count} empty cells at columns {empty_cols}")


def main():
    grid = create_10x10_with_constraints()

    # Solve it first
    solver = TangoSolverV3(grid)
    solved, iterations, time_ms, backtracks = solver.solve()

    print(f"Solve result: {solved}")
    print(f"Iterations: {iterations}, Backtracks: {backtracks}, Time: {time_ms:.2f}ms")
    print()

    # Analyze
    analyze_grid(grid)


if __name__ == "__main__":
    main()
