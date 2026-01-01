#!/usr/bin/env python3
"""
10x10 Puzzle with full constraint mapping (=, ×)

Analyzing the image carefully to extract:
- Initial cell values (◐ = 0, ● = 1)
- Equality constraints (=)
- Inequality constraints (×)
"""

from tango_solver_v3 import TangoGridV3, TangoSolverV3


def create_10x10_with_constraints() -> TangoGridV3:
    """
    Create 10x10 puzzle with all constraints from the image

    Legend:
    - ◐ (blue crescent) = 0
    - ● (yellow circle) = 1
    - = means adjacent cells must be equal
    - × means adjacent cells must be different
    """
    grid = TangoGridV3(10, 10)

    # ===== INITIAL VALUES =====
    # Reading from the image row by row

    # Row 1 (index 1): _ ◐ × _ _ _ _ _ _ _
    grid.set_cell(1, 1, 0)

    # Row 2 (index 2): ● × _ _ ● _ _ = _ ◐
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 9, 0)

    # Row 3 (index 3): _ × _ _ _ _ × _ ● ×
    grid.set_cell(3, 8, 1)

    # Row 4 (index 4): _ _ ◐ _ _ _ _ ◐ _ _
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 7, 0)

    # Row 5 (index 5): = ◐ _ × _ _ ◐ × _ =
    grid.set_cell(5, 1, 0)
    grid.set_cell(5, 6, 0)

    # Row 6 (index 6): _ _ _ _ _ _ _ _ × =
    # No initial values on row 6

    # Row 7 (index 7): _ _ ● _ ● _ _ _ = ●
    grid.set_cell(7, 2, 1)
    grid.set_cell(7, 4, 1)
    grid.set_cell(7, 9, 1)

    # Row 8 (index 8): ◐ _ × × × _ _ _ _ _
    grid.set_cell(8, 0, 0)

    # Row 9 (index 9): _ _ _ = _ ◐ ● _ = ●
    grid.set_cell(9, 5, 0)
    grid.set_cell(9, 6, 1)
    grid.set_cell(9, 9, 1)

    # ===== CONSTRAINTS =====
    # Now adding all = and × constraints from the image

    # Reading constraints carefully from the image:

    # Row 0 constraints
    grid.add_constraint(0, 8, 0, 9, "=")  # Top right has =

    # Row 1 constraints
    grid.add_constraint(1, 1, 1, 2, "×")  # After the ◐ at (1,1)

    # Row 2 constraints
    grid.add_constraint(2, 0, 2, 1, "×")  # After the ● at (2,0)
    grid.add_constraint(2, 7, 2, 8, "=")  # Before the ◐ at (2,9)
    grid.add_constraint(2, 5, 2, 6, "=")  # Middle of row 2

    # Row 3 constraints
    grid.add_constraint(3, 0, 3, 1, "×")  # Left side
    grid.add_constraint(3, 5, 3, 6, "×")  # Middle
    grid.add_constraint(3, 8, 3, 9, "×")  # After the ● at (3,8)

    # Row 4 constraints (no visible constraints in row 4 itself)

    # Row 5 constraints
    grid.add_constraint(5, 0, 5, 1, "=")  # Before the ◐ at (5,1)
    grid.add_constraint(5, 2, 5, 3, "×")  # After (5,1)
    grid.add_constraint(5, 6, 5, 7, "×")  # After the ◐ at (5,6)
    grid.add_constraint(5, 8, 5, 9, "=")  # Right side

    # Row 6 constraints
    grid.add_constraint(6, 7, 6, 8, "×")  # Right side
    grid.add_constraint(6, 8, 6, 9, "=")  # Far right

    # Row 7 constraints
    grid.add_constraint(7, 7, 7, 8, "=")  # Before the ● at (7,9)

    # Row 8 constraints
    grid.add_constraint(8, 1, 8, 2, "×")  # After the ◐ at (8,0)
    grid.add_constraint(8, 2, 8, 3, "×")  # Continuing
    grid.add_constraint(8, 3, 8, 4, "×")  # Triple ×

    # Row 9 constraints
    grid.add_constraint(9, 3, 9, 4, "=")  # Middle
    grid.add_constraint(9, 7, 9, 8, "=")  # Before the ● at (9,9)

    # Vertical constraints (between rows)
    # Note: These are between vertically adjacent cells

    # Between rows (reading column by column where visible)
    grid.add_constraint(4, 0, 5, 0, "=")  # Column 0, between rows 4-5
    grid.add_constraint(5, 0, 6, 0, "=")  # Column 0, between rows 5-6
    grid.add_constraint(6, 6, 7, 6, "=")  # Column 6, between rows 6-7
    grid.add_constraint(5, 9, 6, 9, "=")  # Column 9, between rows 5-6

    return grid


def main():
    print("=" * 70)
    print("10×10 TANGO PUZZLE WITH FULL CONSTRAINTS (V3)")
    print("=" * 70)
    print()

    grid = create_10x10_with_constraints()

    # Count initial cells and constraints
    initial_count = sum(1 for r in range(10) for c in range(10) if grid.get_cell(r, c) is not None)
    total_cells = 100
    fill_percentage = (initial_count / total_cells) * 100

    print(f"Grid size: 10×10")
    print(f"Initial cells: {initial_count}/{total_cells} ({fill_percentage:.1f}% filled)")
    print(f"Constraints: {len(grid.constraints)} (= and ×)")
    print()

    print("Initial grid:")
    print(grid)
    print()

    print("Constraint summary:")
    equals = sum(1 for c in grid.constraints if c.type == "=")
    crosses = sum(1 for c in grid.constraints if c.type == "×")
    print(f"  = constraints: {equals}")
    print(f"  × constraints: {crosses}")
    print()

    solver = TangoSolverV3(grid)
    solved, iterations, time_ms, backtracks = solver.solve()

    print("=" * 70)
    print("SOLUTION")
    print("=" * 70)
    print(grid)
    print()

    print(f"✓ Solved: {solved}")
    print(f"📊 Statistics:")
    print(f"  - Propagation iterations: {iterations}")
    print(f"  - Backtracking steps: {backtracks}")
    print(f"  - Time: {time_ms:.4f} ms")
    print()

    if solved:
        print("Solution with symbols:")
        for row in grid.grid:
            row_str = ' '.join(['◐' if cell == 0 else '●' if cell is not None else '.' for cell in row])
            print(row_str)
    else:
        print("⚠️  Puzzle not fully solved. May need more constraints or clues.")


if __name__ == "__main__":
    main()
