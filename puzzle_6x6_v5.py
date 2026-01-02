#!/usr/bin/env python3
"""
Test Tango Solver V5 on 6×6 DIFFICILE puzzle
"""

from tango_solver_v5 import TangoGridV5, TangoSolverV5


def create_6x6_difficile_v5():
    """Create the 6×6 DIFFICILE puzzle for V5 solver"""
    grid = TangoGridV5(6, 6)

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
    """Display the grid"""
    for r in range(grid.rows):
        row_str = ' '.join(['.' if grid.get_cell(r, c) is None
                           else str(grid.get_cell(r, c))
                           for c in range(grid.cols)])
        print(f"  {row_str}")


def validate_solution(grid):
    """Validate the solution"""
    violations = []

    # Check three consecutive
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

    # Check balance
    target = grid.cols // 2
    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        if None not in row:
            count_0 = sum(1 for x in row if x == 0)
            count_1 = sum(1 for x in row if x == 1)
            if count_0 != target or count_1 != target:
                violations.append(f"Row {r}: Balance violated ({count_0}⚪ {count_1}⚫ expected {target}⚪ {target}⚫)")

    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        if None not in col:
            count_0 = sum(1 for x in col if x == 0)
            count_1 = sum(1 for x in col if x == 1)
            if count_0 != target or count_1 != target:
                violations.append(f"Col {c}: Balance violated ({count_0}⚪ {count_1}⚫ expected {target}⚪ {target}⚫)")

    # Check explicit constraints
    for constraint in grid.constraints:
        r1, c1 = constraint.cell1
        r2, c2 = constraint.cell2
        val1 = grid.get_cell(r1, c1)
        val2 = grid.get_cell(r2, c2)

        if val1 is not None and val2 is not None:
            if constraint.type == "=" and val1 != val2:
                violations.append(f"Constraint ({r1},{c1}) = ({r2},{c2}): {val1} ≠ {val2}")
            if constraint.type == "×" and val1 == val2:
                violations.append(f"Constraint ({r1},{c1}) × ({r2},{c2}): {val1} == {val2}")

    return violations


def main():
    print("=" * 70)
    print("TANGO SOLVER V5 - 6×6 DIFFICILE PUZZLE")
    print("=" * 70)
    print()

    grid = create_6x6_difficile_v5()
    solver = TangoSolverV5(grid)

    initial_count = sum(1 for r in range(6) for c in range(6)
                       if grid.get_cell(r, c) is not None)

    print(f"Initial: {initial_count}/36 cells")
    print(f"Explicit constraints: {len(grid.constraints)}")
    print(f"Implicit constraints: {len(solver.implicit_constraints)}")
    print()

    print("Implicit constraints generated:")
    for constraint in solver.implicit_constraints:
        r1, c1 = constraint.cell1
        r2, c2 = constraint.cell2
        print(f"  ({r1},{c1}) {constraint.type} ({r2},{c2})")
    print()

    print("Initial grid:")
    display_grid(grid)
    print()

    print("=" * 70)
    print("SOLVING...")
    print("=" * 70)
    print()

    solved, iterations, time_ms = solver.solve(max_iterations=50)

    print("Solution:")
    display_grid(grid)
    print()

    filled_count = sum(1 for r in range(6) for c in range(6)
                      if grid.get_cell(r, c) is not None)

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✓ Solved: {solved}")
    print(f"📊 Filled: {filled_count}/36 ({filled_count*100//36}%)")
    print(f"🔄 Iterations: {iterations}")
    print(f"⏱️  Time: {time_ms:.4f} ms")
    print(f"Progress: +{filled_count - initial_count} cells")
    print()

    # Validate
    violations = validate_solution(grid)
    if violations:
        print("❌ VIOLATIONS FOUND:")
        for v in violations:
            print(f"  {v}")
    else:
        print("✅ NO VIOLATIONS - Solution is VALID!")

    if solved and not violations:
        print()
        print("🎉 PUZZLE COMPLÈTEMENT RÉSOLU!")

    print()


if __name__ == "__main__":
    main()
