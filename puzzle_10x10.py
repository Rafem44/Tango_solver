#!/usr/bin/env python3
"""
Test the 10x10 puzzle from the user's image
"""

from tango_solver import TangoGrid, TangoSolver
from tango_solver_v2 import TangoGridV2, TangoSolverV2


def create_10x10_puzzle_v1() -> TangoGrid:
    """
    Create the 10x10 puzzle from the image
    Croissant bleu (◐) = 0, Cercle jaune (●) = 1
    """
    grid = TangoGrid(10, 10)

    # Analyzing the grid from the image row by row
    # Row 0: _ _ _ _ _ _ _ _ _ _
    # (appears empty)

    # Row 1: _ ◐ _ _ _ _ _ _ _ _
    grid.set_cell(1, 1, 0)

    # Row 2: ● _ _ _ ● _ _ _ _ ◐
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 9, 0)

    # Row 3: _ _ _ _ _ _ _ _ ● _
    grid.set_cell(3, 8, 1)

    # Row 4: _ _ ◐ _ _ _ _ ◐ _ _
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 7, 0)

    # Row 5: _ ◐ _ _ _ _ ● _ _ _
    grid.set_cell(5, 1, 0)
    grid.set_cell(5, 6, 1)

    # Row 6: _ _ _ _ _ _ _ _ _ _
    # (appears empty)

    # Row 7: _ _ ● _ ● _ _ _ _ ●
    grid.set_cell(7, 2, 1)
    grid.set_cell(7, 4, 1)
    grid.set_cell(7, 9, 1)

    # Row 8: ◐ _ _ _ _ _ _ _ _ _
    grid.set_cell(8, 0, 0)

    # Row 9: _ _ _ _ _ ◐ ● _ _ ●
    grid.set_cell(9, 5, 0)
    grid.set_cell(9, 6, 1)
    grid.set_cell(9, 9, 1)

    return grid


def create_10x10_puzzle_v2() -> TangoGridV2:
    """
    Create the 10x10 puzzle for V2
    """
    grid = TangoGridV2(10, 10)

    # Row 1
    grid.set_cell(1, 1, 0)

    # Row 2
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 9, 0)

    # Row 3
    grid.set_cell(3, 8, 1)

    # Row 4
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 7, 0)

    # Row 5
    grid.set_cell(5, 1, 0)
    grid.set_cell(5, 6, 1)

    # Row 7
    grid.set_cell(7, 2, 1)
    grid.set_cell(7, 4, 1)
    grid.set_cell(7, 9, 1)

    # Row 8
    grid.set_cell(8, 0, 0)

    # Row 9
    grid.set_cell(9, 5, 0)
    grid.set_cell(9, 6, 1)
    grid.set_cell(9, 9, 1)

    return grid


def main():
    print("=" * 70)
    print("TESTING 10×10 PUZZLE FROM IMAGE")
    print("=" * 70)
    print()

    # Count initial cells
    initial_count = 13  # Counted from the image
    total_cells = 100
    fill_percentage = (initial_count / total_cells) * 100

    print(f"Grid size: 10×10")
    print(f"Initial cells: {initial_count}/{total_cells} ({fill_percentage:.1f}% filled)")
    print()

    # Test V1
    print("🔷 TESTING V1 (Pure Constraint Propagation)")
    print("-" * 70)
    grid_v1 = create_10x10_puzzle_v1()
    print("Initial grid:")
    print(grid_v1)
    print()

    solver_v1 = TangoSolver(grid_v1)
    solved_v1, iter_v1, time_v1 = solver_v1.solve()

    print("Result:")
    print(grid_v1)
    print()
    print(f"✓ Solved: {solved_v1}")
    print(f"🔄 Iterations: {iter_v1}")
    print(f"⏱️  Time: {time_v1:.4f} ms")
    print()

    if solved_v1:
        print("Solution with symbols:")
        for row in grid_v1.grid:
            row_str = ' '.join(['◐' if cell == 0 else '●' if cell is not None else '.' for cell in row])
            print(row_str)

    print()
    print("=" * 70)

    # Test V2
    print("🔶 TESTING V2 (Hybrid: Propagation + Backtracking)")
    print("-" * 70)
    grid_v2 = create_10x10_puzzle_v2()
    print("Initial grid:")
    print(grid_v2)
    print()

    solver_v2 = TangoSolverV2(grid_v2)
    solved_v2, iter_v2, time_v2, back_v2 = solver_v2.solve()

    print("Result:")
    print(grid_v2)
    print()
    print(f"✓ Solved: {solved_v2}")
    print(f"🔄 Iterations: {iter_v2}")
    print(f"🔙 Backtracks: {back_v2}")
    print(f"⏱️  Time: {time_v2:.4f} ms")
    print()

    if solved_v2:
        print("Solution with symbols:")
        for row in grid_v2.grid:
            row_str = ' '.join(['◐' if cell == 0 else '●' if cell is not None else '.' for cell in row])
            print(row_str)

    print()
    print("=" * 70)
    print("📊 COMPARISON")
    print("=" * 70)

    if solved_v1 and solved_v2:
        winner = "V1" if time_v1 < time_v2 else "V2"
        speedup = max(time_v1, time_v2) / min(time_v1, time_v2)
        print(f"Both versions solved the puzzle!")
        print(f"🏆 Winner: {winner}")
        print(f"📈 Speedup: {speedup:.2f}x")
    elif solved_v2 and not solved_v1:
        print("🏆 V2 WINS - V1 could not solve this puzzle!")
        print("V2 needed backtracking to find the solution.")
    elif solved_v1 and not solved_v2:
        print("🏆 V1 WINS - V2 failed (unexpected!)")
    else:
        print("⚠️  Neither version could solve this puzzle.")
        print("The puzzle may need more initial clues or be unsolvable.")


if __name__ == "__main__":
    main()
