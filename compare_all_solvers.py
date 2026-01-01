#!/usr/bin/env python3
"""
Compare all solver versions on the 10x10 puzzle
"""

from puzzle_10x10_v3 import create_10x10_with_constraints
from puzzle_10x10_v4 import create_10x10_with_constraints_v4
from tango_solver_simple import create_10x10_simple, TangoSolverSimple
from tango_solver_v3 import TangoSolverV3
from tango_solver_v4 import TangoSolverV4


def count_violations(grid):
    """Count violations in a grid"""
    violations = 0

    # Check three consecutive
    for r in range(grid.rows):
        for c in range(grid.cols - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r, c+1), grid.get_cell(r, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations += 1

    for c in range(grid.cols):
        for r in range(grid.rows - 2):
            vals = [grid.get_cell(r, c), grid.get_cell(r+1, c), grid.get_cell(r+2, c)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                violations += 1

    # Check explicit constraints
    for constraint in grid.constraints:
        r1, c1 = constraint.cell1
        r2, c2 = constraint.cell2
        val1 = grid.get_cell(r1, c1)
        val2 = grid.get_cell(r2, c2)

        if val1 is not None and val2 is not None:
            if constraint.type == "=" and val1 != val2:
                violations += 1
            if constraint.type == "×" and val1 == val2:
                violations += 1

    # Check balance (only for complete rows/cols)
    for r in range(grid.rows):
        row = [grid.get_cell(r, c) for c in range(grid.cols)]
        if None not in row:
            count_0 = sum(1 for x in row if x == 0)
            if count_0 != 5:
                violations += 1

    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        if None not in col:
            count_0 = sum(1 for x in col if x == 0)
            if count_0 != 5:
                violations += 1

    return violations


def main():
    print("=" * 80)
    print("COMPARING ALL SOLVERS ON 10×10 PUZZLE")
    print("=" * 80)
    print()

    results = []

    # V3
    print("Running V3 (with = and × constraints)...")
    grid_v3 = create_10x10_with_constraints()
    solver_v3 = TangoSolverV3(grid_v3)
    solved_v3, iterations_v3, time_v3, backtracks_v3 = solver_v3.solve()
    filled_v3 = sum(1 for r in range(10) for c in range(10) if grid_v3.get_cell(r, c) is not None)
    violations_v3 = count_violations(grid_v3)
    results.append(("V3", filled_v3, violations_v3, iterations_v3, backtracks_v3, time_v3))
    print(f"  Filled: {filled_v3}%, Violations: {violations_v3}, Time: {time_v3:.2f}ms")
    print()

    # V4
    print("Running V4 (strict validation)...")
    grid_v4 = create_10x10_with_constraints_v4()
    solver_v4 = TangoSolverV4(grid_v4)
    solved_v4, iterations_v4, time_v4, backtracks_v4 = solver_v4.solve(max_iterations=200)
    filled_v4 = sum(1 for r in range(10) for c in range(10) if grid_v4.get_cell(r, c) is not None)
    violations_v4 = count_violations(grid_v4)
    results.append(("V4", filled_v4, violations_v4, iterations_v4, backtracks_v4, time_v4))
    print(f"  Filled: {filled_v4}%, Violations: {violations_v4}, Time: {time_v4:.2f}ms")
    print()

    # Simple
    print("Running Simple (V1 + = and × with validation)...")
    grid_simple = create_10x10_simple()
    solver_simple = TangoSolverSimple(grid_simple)
    solved_simple, iterations_simple, time_simple = solver_simple.solve()
    filled_simple = sum(1 for r in range(10) for c in range(10) if grid_simple.get_cell(r, c) is not None)
    violations_simple = count_violations(grid_simple)
    results.append(("Simple", filled_simple, violations_simple, iterations_simple, 0, time_simple))
    print(f"  Filled: {filled_simple}%, Violations: {violations_simple}, Time: {time_simple:.2f}ms")
    print()

    # Summary table
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Solver':<10} {'Filled':<10} {'Violations':<15} {'Iterations':<12} {'Backtracks':<12} {'Time (ms)':<10}")
    print("-" * 80)
    for name, filled, violations, iterations, backtracks, time_ms in results:
        status = "✅ VALID" if violations == 0 else "❌ INVALID"
        print(f"{name:<10} {filled:<10} {status:<15} {iterations:<12} {backtracks:<12} {time_ms:<10.2f}")
    print()

    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()
    print("V3: High completion but produces INVALID solutions with violations")
    print("V4: Valid but slow and low completion due to conservative backtracking")
    print("Simple: Valid but lowest completion - pure propagation is not enough")
    print()
    print("CONCLUSION: This 10×10 puzzle needs backtracking to solve completely,")
    print("            but must use strict validation to avoid invalid solutions.")
    print()


if __name__ == "__main__":
    main()
