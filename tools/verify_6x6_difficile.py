#!/usr/bin/env python3
"""
Verify the 6×6 DIFFICILE solution
"""

from puzzle_6x6_difficile import create_6x6_difficile
from tango_solver_simple import TangoSolverSimple


def verify_solution(grid):
    """Verify the solution has no violations"""
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()

    violations = []

    # Check three consecutive in rows
    for r in range(grid.rows):
        for c in range(grid.cols - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r, c+1), grid.get_cell(r, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations.append(f"❌ Row {r}, cols {c}-{c+2}: Three consecutive {vals[0]}s")

    # Check three consecutive in columns
    for c in range(grid.cols):
        for r in range(grid.rows - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r+1, c), grid.get_cell(r+2, c)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations.append(f"❌ Col {c}, rows {r}-{r+2}: Three consecutive {vals[0]}s")

    # Check balance (3 zeros and 3 ones per row/col)
    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        count_0 = sum(1 for x in row if x == 0)
        count_1 = sum(1 for x in row if x == 1)
        if count_0 != 3 or count_1 != 3:
            violations.append(f"❌ Row {r}: Balance violated ({count_0}⚪ {count_1}⚫ expected 3⚪ 3⚫)")

    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        count_0 = sum(1 for x in col if x == 0)
        count_1 = sum(1 for x in col if x == 1)
        if count_0 != 3 or count_1 != 3:
            violations.append(f"❌ Col {c}: Balance violated ({count_0}⚪ {count_1}⚫ expected 3⚪ 3⚫)")

    # Check explicit constraints
    for constraint in grid.constraints:
        r1, c1 = constraint.cell1
        r2, c2 = constraint.cell2
        val1 = grid.get_cell(r1, c1)
        val2 = grid.get_cell(r2, c2)

        if val1 is not None and val2 is not None:
            if constraint.type == "=" and val1 != val2:
                violations.append(f"❌ Constraint ({r1},{c1}) = ({r2},{c2}): {val1} ≠ {val2}")
            if constraint.type == "×" and val1 == val2:
                violations.append(f"❌ Constraint ({r1},{c1}) × ({r2},{c2}): {val1} == {val2}")

    if violations:
        print("VIOLATIONS FOUND:")
        for v in violations:
            print(f"  {v}")
        print()
        return False
    else:
        print("✅ NO VIOLATIONS - SOLUTION IS VALID!")
        print()

        # Show balance details
        print("Balance check:")
        for r in range(grid.rows):
            row = [grid.get_cell(r, c) for c in range(grid.cols)]
            count_0 = sum(1 for x in row if x == 0)
            count_1 = sum(1 for x in row if x == 1)
            row_str = ' '.join([str(x) for x in row])
            print(f"  Row {r}: {row_str} | {count_0}⚪ {count_1}⚫")

        print()
        for c in range(grid.cols):
            col = [grid.get_cell(r, c) for r in range(grid.rows)]
            count_0 = sum(1 for x in col if x == 0)
            count_1 = sum(1 for x in col if x == 1)
            print(f"  Col {c}: {count_0}⚪ {count_1}⚫")

        print()

        # Show constraint validation
        print("Constraint validation:")
        for constraint in grid.constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2
            val1 = grid.get_cell(r1, c1)
            val2 = grid.get_cell(r2, c2)
            print(f"  ({r1},{c1}) {constraint.type} ({r2},{c2}): {val1} {constraint.type} {val2} ✓")

        print()
        return True


def main():
    grid = create_6x6_difficile()
    solver = TangoSolverSimple(grid)
    solved, iterations, time_ms = solver.solve(max_iterations=50)

    print(f"Solved: {solved}")
    print(f"Iterations: {iterations}")
    print(f"Time: {time_ms:.4f} ms")
    print()

    # Display solution
    print("Solution:")
    for r in range(grid.rows):
        row_str = ' '.join([str(grid.get_cell(r, c)) for c in range(grid.cols)])
        print(f"  {row_str}")
    print()

    # Verify
    is_valid = verify_solution(grid)

    if is_valid and solved:
        print("=" * 70)
        print("🎉 PUZZLE COMPLÈTEMENT RÉSOLU ET VALIDE!")
        print("=" * 70)


if __name__ == "__main__":
    main()
