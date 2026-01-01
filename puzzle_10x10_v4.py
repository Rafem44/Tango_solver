#!/usr/bin/env python3
"""
10x10 Puzzle with V4 (strict validation)
"""

from tango_solver_v4 import TangoGridV4, TangoSolverV4


def create_10x10_with_constraints_v4() -> TangoGridV4:
    """Create 10x10 puzzle for V4 with all constraints"""
    grid = TangoGridV4(10, 10)

    # Initial values
    grid.set_cell(1, 1, 0)
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 9, 0)
    grid.set_cell(3, 8, 1)
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 7, 0)
    grid.set_cell(5, 1, 0)
    grid.set_cell(5, 6, 0)
    grid.set_cell(7, 2, 1)
    grid.set_cell(7, 4, 1)
    grid.set_cell(7, 9, 1)
    grid.set_cell(8, 0, 0)
    grid.set_cell(9, 5, 0)
    grid.set_cell(9, 6, 1)
    grid.set_cell(9, 9, 1)

    # Constraints
    grid.add_constraint(0, 8, 0, 9, "=")
    grid.add_constraint(1, 1, 1, 2, "×")
    grid.add_constraint(2, 0, 2, 1, "×")
    grid.add_constraint(2, 7, 2, 8, "=")
    grid.add_constraint(2, 5, 2, 6, "=")
    grid.add_constraint(3, 0, 3, 1, "×")
    grid.add_constraint(3, 5, 3, 6, "×")
    grid.add_constraint(3, 8, 3, 9, "×")
    grid.add_constraint(5, 0, 5, 1, "=")
    grid.add_constraint(5, 2, 5, 3, "×")
    grid.add_constraint(5, 6, 5, 7, "×")
    grid.add_constraint(5, 8, 5, 9, "=")
    grid.add_constraint(6, 7, 6, 8, "×")
    grid.add_constraint(6, 8, 6, 9, "=")
    grid.add_constraint(7, 7, 7, 8, "=")
    grid.add_constraint(8, 1, 8, 2, "×")
    grid.add_constraint(8, 2, 8, 3, "×")
    grid.add_constraint(8, 3, 8, 4, "×")
    grid.add_constraint(9, 3, 9, 4, "=")
    grid.add_constraint(9, 7, 9, 8, "=")
    grid.add_constraint(4, 0, 5, 0, "=")
    grid.add_constraint(5, 0, 6, 0, "=")
    grid.add_constraint(6, 6, 7, 6, "=")
    grid.add_constraint(5, 9, 6, 9, "=")

    return grid


def main():
    print("=" * 70)
    print("10×10 TANGO PUZZLE - V4 WITH STRICT VALIDATION")
    print("=" * 70)
    print()

    grid = create_10x10_with_constraints_v4()

    initial_count = sum(1 for r in range(10) for c in range(10) if grid.get_cell(r, c) is not None)
    print(f"Initial cells: {initial_count}/100 ({initial_count}%)")
    print(f"Constraints: {len(grid.constraints)}")
    print()

    print("Initial grid:")
    print(grid)
    print()

    solver = TangoSolverV4(grid)
    solved, iterations, time_ms, backtracks = solver.solve(max_iterations=200)

    print("=" * 70)
    print("SOLUTION")
    print("=" * 70)
    print(grid)
    print()

    print(f"✓ Solved: {solved}")
    print(f"📊 Statistics:")
    print(f"  - Propagation iterations: {iterations}")
    print(f"  - Backtracking steps: {backtracks}")
    print(f"  - Validations performed: {solver.validations}")
    print(f"  - Time: {time_ms:.4f} ms")
    print()

    if solved:
        print("Solution with symbols:")
        for row in grid.grid:
            row_str = ' '.join(['◐' if cell == 0 else '●' if cell is not None else '.' for cell in row])
            print(row_str)
        print()

        # Verify solution
        print("=" * 70)
        print("VALIDATION CHECK")
        print("=" * 70)

        errors = []

        # Check three consecutive
        for r in range(10):
            for c in range(8):
                vals = [grid.get_cell(r, c), grid.get_cell(r, c+1), grid.get_cell(r, c+2)]
                if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                    errors.append(f"Row {r}, cols {c}-{c+2}: Three consecutive {vals[0]}s")

        for c in range(10):
            for r in range(8):
                vals = [grid.get_cell(r, c), grid.get_cell(r+1, c), grid.get_cell(r+2, c)]
                if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                    errors.append(f"Col {c}, rows {r}-{r+2}: Three consecutive {vals[0]}s")

        # Check balance
        for r in range(10):
            row = [grid.get_cell(r, c) for c in range(10)]
            count_0 = sum(1 for x in row if x == 0)
            count_1 = sum(1 for x in row if x == 1)
            if count_0 != 5 or count_1 != 5:
                errors.append(f"Row {r}: Balance violated ({count_0} zeros, {count_1} ones)")

        for c in range(10):
            col = [grid.get_cell(r, c) for r in range(10)]
            count_0 = sum(1 for x in col if x == 0)
            count_1 = sum(1 for x in col if x == 1)
            if count_0 != 5 or count_1 != 5:
                errors.append(f"Col {c}: Balance violated ({count_0} zeros, {count_1} ones)")

        # Check constraints
        for constraint in grid.constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2
            val1 = grid.get_cell(r1, c1)
            val2 = grid.get_cell(r2, c2)

            if val1 is not None and val2 is not None:
                if constraint.type == "=" and val1 != val2:
                    errors.append(f"{constraint.cell1} = {constraint.cell2}: {val1} ≠ {val2}")
                if constraint.type == "×" and val1 == val2:
                    errors.append(f"{constraint.cell1} × {constraint.cell2}: {val1} == {val2}")

        if errors:
            print("❌ ERRORS FOUND:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("✅ ALL CONSTRAINTS SATISFIED!")
            print("✅ Solution is VALID!")


if __name__ == "__main__":
    main()
