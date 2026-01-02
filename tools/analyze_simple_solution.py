#!/usr/bin/env python3
"""
Analyze the simple solver's solution for violations
"""

from tango_solver_simple import create_10x10_simple, TangoSolverSimple


def analyze_solution(grid):
    """Check for any constraint violations"""
    print("=" * 70)
    print("VALIDATION CHECK")
    print("=" * 70)
    print()

    violations = []

    # Check three consecutive in rows
    for r in range(grid.rows):
        for c in range(grid.cols - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r, c+1), grid.get_cell(r, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations.append(f"Row {r}, cols {c}-{c+2}: Three consecutive {vals[0]}s")

    # Check three consecutive in columns
    for c in range(grid.cols):
        for r in range(grid.rows - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r+1, c), grid.get_cell(r+2, c)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations.append(f"Col {c}, rows {r}-{r+2}: Three consecutive {vals[0]}s")

    # Check balance constraints
    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        count_0 = sum(1 for x in row if x == 0)
        count_1 = sum(1 for x in row if x == 1)
        count_empty = sum(1 for x in row if x is None)

        # Only check if row is complete
        if count_empty == 0 and (count_0 != 5 or count_1 != 5):
            violations.append(f"Row {r}: Balance violated ({count_0} zeros, {count_1} ones)")
        # Check if too many of one value
        elif count_0 > 5:
            violations.append(f"Row {r}: Too many zeros ({count_0} > 5)")
        elif count_1 > 5:
            violations.append(f"Row {r}: Too many ones ({count_1} > 5)")

    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        count_0 = sum(1 for x in col if x == 0)
        count_1 = sum(1 for x in col if x == 1)
        count_empty = sum(1 for x in col if x is None)

        # Only check if column is complete
        if count_empty == 0 and (count_0 != 5 or count_1 != 5):
            violations.append(f"Col {c}: Balance violated ({count_0} zeros, {count_1} ones)")
        # Check if too many of one value
        elif count_0 > 5:
            violations.append(f"Col {c}: Too many zeros ({count_0} > 5)")
        elif count_1 > 5:
            violations.append(f"Col {c}: Too many ones ({count_1} > 5)")

    # Check explicit constraints
    for constraint in grid.constraints:
        r1, c1 = constraint.cell1
        r2, c2 = constraint.cell2
        val1 = grid.get_cell(r1, c1)
        val2 = grid.get_cell(r2, c2)

        if val1 is not None and val2 is not None:
            if constraint.type == "=" and val1 != val2:
                violations.append(f"{constraint.cell1} = {constraint.cell2}: {val1} ≠ {val2}")
            if constraint.type == "×" and val1 == val2:
                violations.append(f"{constraint.cell1} × {constraint.cell2}: {val1} == {val2}")

    if violations:
        print("❌ VIOLATIONS FOUND:")
        for v in violations:
            print(f"  - {v}")
        print()
    else:
        print("✅ NO VIOLATIONS - Solution is VALID!")
        print()

    # Show progress per row
    print("=" * 70)
    print("PROGRESS PER ROW")
    print("=" * 70)
    print()

    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        count_0 = sum(1 for x in row if x == 0)
        count_1 = sum(1 for x in row if x == 1)
        count_empty = sum(1 for x in row if x is None)

        row_str = ' '.join(['.' if cell is None else str(cell) for cell in row])
        print(f"Row {r}: {row_str}  | {count_0}⚪ {count_1}⚫ {count_empty}❓")

    print()
    print("=" * 70)
    print("PROGRESS PER COLUMN")
    print("=" * 70)
    print()

    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        count_0 = sum(1 for x in col if x == 0)
        count_1 = sum(1 for x in col if x == 1)
        count_empty = sum(1 for x in col if x is None)

        print(f"Col {c}: {count_0}⚪ {count_1}⚫ {count_empty}❓")

    print()
    return len(violations) == 0


def main():
    grid = create_10x10_simple()

    print("Running simple solver...")
    solver = TangoSolverSimple(grid)
    solved, iterations, time_ms = solver.solve()

    print(f"Solved: {solved} ({iterations} iterations, {time_ms:.2f}ms)")
    print()

    # Analyze
    is_valid = analyze_solution(grid)

    if is_valid:
        print("=" * 70)
        print("✅ CONCLUSION: Solution is VALID (no violations)")
        print("=" * 70)
    else:
        print("=" * 70)
        print("❌ CONCLUSION: Solution has violations")
        print("=" * 70)


if __name__ == "__main__":
    main()
