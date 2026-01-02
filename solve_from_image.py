#!/usr/bin/env python3
"""
Solve Tango puzzles directly from images using OCR

This script combines OCR detection with the Tango solver to automatically
solve puzzles from screenshots or photos.

Usage:
    python solve_from_image.py <image_path>
"""

import sys
import os

try:
    from tango_ocr import TangoOCR
    from tango_solver_simple import TangoGridSimple, TangoSolverSimple
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nMake sure to install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def solve_puzzle_from_image(image_path: str, debug: bool = False):
    """
    Read a puzzle from an image and solve it

    Args:
        image_path: Path to the puzzle image
        debug: Whether to show debug information

    Returns:
        Tuple of (grid, solved, iterations, time_ms)
    """
    print("=" * 70)
    print("TANGO SOLVER - FROM IMAGE")
    print("=" * 70)
    print()

    # Step 1: OCR - Read the puzzle
    print("Step 1: Reading puzzle from image...")
    ocr = TangoOCR(debug=debug)

    try:
        result = ocr.read_puzzle(image_path)
    except Exception as e:
        print(f"❌ Error reading image: {e}")
        return None

    grid_size = result['grid_size']
    initial_values = result['initial_values']
    constraints = result['constraints']

    print(f"✓ Detected {grid_size[0]}×{grid_size[1]} grid")
    print(f"✓ Found {len(initial_values)} initial values")
    print(f"✓ Found {len(constraints)} constraints")
    print()

    # Step 2: Create grid
    print("Step 2: Creating grid...")
    rows, cols = grid_size
    grid = TangoGridSimple(rows, cols)

    # Set initial values
    for row, col, value in initial_values:
        grid.set_cell(row, col, value)
        if debug:
            print(f"  Set ({row},{col}) = {value}")

    # Add constraints
    for (r1, c1), (r2, c2), constraint_type in constraints:
        grid.add_constraint(r1, c1, r2, c2, constraint_type)
        if debug:
            print(f"  Constraint ({r1},{c1}) {constraint_type} ({r2},{c2})")

    print(f"✓ Grid created with {len(initial_values)} initial cells")
    print()

    # Display initial grid
    print("Initial grid:")
    display_grid(grid)
    print()

    # Step 3: Solve
    print("=" * 70)
    print("Step 3: Solving puzzle...")
    print("=" * 70)
    print()

    solver = TangoSolverSimple(grid)
    solved, iterations, time_ms = solver.solve(max_iterations=100)

    # Display solution
    print("Solution:")
    display_grid(grid)
    print()

    # Statistics
    filled_count = sum(1 for r in range(rows) for c in range(cols)
                      if grid.get_cell(r, c) is not None)
    total_cells = rows * cols

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✓ Solved: {solved}")
    print(f"📊 Filled: {filled_count}/{total_cells} ({filled_count*100//total_cells}%)")
    print(f"🔄 Iterations: {iterations}")
    print(f"⏱️  Time: {time_ms:.4f} ms")
    print()

    if solved:
        print("🎉 PUZZLE SOLVED SUCCESSFULLY!")
    else:
        print("⚠️  Puzzle partially solved (may need backtracking)")

    print()

    # Validate
    violations = validate_solution(grid)
    if violations:
        print("❌ VIOLATIONS FOUND:")
        for v in violations:
            print(f"  {v}")
    else:
        print("✅ NO VIOLATIONS - Solution is valid!")

    print()

    return grid, solved, iterations, time_ms


def display_grid(grid):
    """Display the grid in a readable format"""
    for r in range(grid.rows):
        row_str = ' '.join(['.' if grid.get_cell(r, c) is None
                           else str(grid.get_cell(r, c))
                           for c in range(grid.cols)])
        print(f"  {row_str}")


def validate_solution(grid):
    """Validate the solution for violations"""
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
            if count_0 != target:
                violations.append(f"Row {r}: Balance violated ({count_0} zeros, expected {target})")

    for c in range(grid.cols):
        col = [grid.get_cell(r, c) for r in range(grid.rows)]
        if None not in col:
            count_0 = sum(1 for x in col if x == 0)
            if count_0 != target:
                violations.append(f"Col {c}: Balance violated ({count_0} zeros, expected {target})")

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
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python solve_from_image.py <image_path> [--debug]")
        print()
        print("Example:")
        print("  python solve_from_image.py puzzle.png")
        print("  python solve_from_image.py puzzle.jpg --debug")
        return

    image_path = sys.argv[1]
    debug = "--debug" in sys.argv

    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return

    solve_puzzle_from_image(image_path, debug=debug)


if __name__ == "__main__":
    main()
