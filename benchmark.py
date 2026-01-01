#!/usr/bin/env python3
"""
Benchmark: Compare V1 vs V2 Tango Solvers
"""

import sys
from tango_solver import TangoGrid, TangoSolver
from tango_solver_v2 import TangoGridV2, TangoSolverV2


def convert_to_v1(grid_v2: TangoGridV2) -> TangoGrid:
    """Convert V2 grid to V1 grid"""
    grid = TangoGrid(grid_v2.rows, grid_v2.cols)
    for r in range(grid_v2.rows):
        for c in range(grid_v2.cols):
            if grid_v2.grid[r][c] is not None:
                grid.set_cell(r, c, grid_v2.grid[r][c])
    return grid


def create_puzzle_1_v1() -> TangoGrid:
    """Puzzle 1 for V1"""
    grid = TangoGrid(6, 6)
    grid.set_cell(0, 0, 0)
    grid.set_cell(0, 1, 0)
    grid.set_cell(0, 3, 1)
    grid.set_cell(0, 4, 0)
    grid.set_cell(1, 0, 0)
    grid.set_cell(1, 1, 0)
    grid.set_cell(1, 5, 1)
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 5, 0)
    grid.set_cell(3, 0, 1)
    grid.set_cell(3, 1, 1)
    grid.set_cell(3, 2, 0)
    grid.set_cell(3, 3, 0)
    grid.set_cell(3, 4, 1)
    grid.set_cell(3, 5, 0)
    grid.set_cell(4, 0, 0)
    grid.set_cell(4, 1, 0)
    grid.set_cell(4, 2, 1)
    grid.set_cell(4, 4, 0)
    grid.set_cell(4, 5, 1)
    grid.set_cell(5, 1, 1)
    grid.set_cell(5, 2, 0)
    grid.set_cell(5, 5, 0)
    return grid


def create_puzzle_2_v1() -> TangoGrid:
    """Puzzle 2 for V1"""
    grid = TangoGrid(6, 6)
    grid.set_cell(0, 0, 1)
    grid.set_cell(0, 4, 0)
    grid.set_cell(1, 2, 0)
    grid.set_cell(2, 5, 0)
    grid.set_cell(3, 3, 0)
    grid.set_cell(3, 4, 1)
    grid.set_cell(3, 5, 0)
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 3, 0)
    grid.set_cell(4, 4, 1)
    grid.set_cell(4, 5, 1)
    grid.set_cell(5, 3, 1)
    grid.set_cell(5, 5, 0)
    return grid


def create_puzzle_1_v2() -> TangoGridV2:
    """Puzzle 1 for V2"""
    grid = TangoGridV2(6, 6)
    grid.set_cell(0, 0, 0)
    grid.set_cell(0, 1, 0)
    grid.set_cell(0, 3, 1)
    grid.set_cell(0, 4, 0)
    grid.set_cell(1, 0, 0)
    grid.set_cell(1, 1, 0)
    grid.set_cell(1, 5, 1)
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 5, 0)
    grid.set_cell(3, 0, 1)
    grid.set_cell(3, 1, 1)
    grid.set_cell(3, 2, 0)
    grid.set_cell(3, 3, 0)
    grid.set_cell(3, 4, 1)
    grid.set_cell(3, 5, 0)
    grid.set_cell(4, 0, 0)
    grid.set_cell(4, 1, 0)
    grid.set_cell(4, 2, 1)
    grid.set_cell(4, 4, 0)
    grid.set_cell(4, 5, 1)
    grid.set_cell(5, 1, 1)
    grid.set_cell(5, 2, 0)
    grid.set_cell(5, 5, 0)
    return grid


def create_puzzle_2_v2() -> TangoGridV2:
    """Puzzle 2 for V2"""
    grid = TangoGridV2(6, 6)
    grid.set_cell(0, 0, 1)
    grid.set_cell(0, 4, 0)
    grid.set_cell(1, 2, 0)
    grid.set_cell(2, 5, 0)
    grid.set_cell(3, 3, 0)
    grid.set_cell(3, 4, 1)
    grid.set_cell(3, 5, 0)
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 3, 0)
    grid.set_cell(4, 4, 1)
    grid.set_cell(4, 5, 1)
    grid.set_cell(5, 3, 1)
    grid.set_cell(5, 5, 0)
    return grid


def main():
    print("=" * 70)
    print("TANGO SOLVER BENCHMARK: V1 vs V2")
    print("=" * 70)
    print()

    # Benchmark Puzzle 1
    print("📋 PUZZLE 1: 18 initial cells (50% filled)")
    print("-" * 70)

    # V1
    grid1_v1 = create_puzzle_1_v1()
    solver1_v1 = TangoSolver(grid1_v1)
    solved1_v1, iter1_v1, time1_v1 = solver1_v1.solve()

    print(f"V1 (Pure Constraint Propagation):")
    print(f"  ✓ Solved: {solved1_v1}")
    print(f"  ⏱️  Time: {time1_v1:.4f} ms")
    print(f"  🔄 Iterations: {iter1_v1}")
    print()

    # V2
    grid1_v2 = create_puzzle_1_v2()
    solver1_v2 = TangoSolverV2(grid1_v2)
    solved1_v2, iter1_v2, time1_v2, back1_v2 = solver1_v2.solve()

    print(f"V2 (Hybrid: Propagation + Backtracking):")
    print(f"  ✓ Solved: {solved1_v2}")
    print(f"  ⏱️  Time: {time1_v2:.4f} ms")
    print(f"  🔄 Iterations: {iter1_v2}")
    print(f"  🔙 Backtracks: {back1_v2}")
    print()

    # Comparison
    speedup1 = time1_v1 / time1_v2 if time1_v2 > 0 else float('inf')
    winner1 = "V1" if time1_v1 < time1_v2 else "V2"
    diff1 = abs(time1_v1 - time1_v2)

    print(f"🏆 Winner: {winner1} (faster by {diff1:.4f} ms)")
    print(f"📊 Speedup: {speedup1:.2f}x")
    print()

    # Benchmark Puzzle 2
    print("=" * 70)
    print("📋 PUZZLE 2: 11 initial cells (31% filled) - HARDER")
    print("-" * 70)

    # V1
    grid2_v1 = create_puzzle_2_v1()
    solver2_v1 = TangoSolver(grid2_v1)
    solved2_v1, iter2_v1, time2_v1 = solver2_v1.solve()

    print(f"V1 (Pure Constraint Propagation):")
    print(f"  ✓ Solved: {solved2_v1}")
    print(f"  ⏱️  Time: {time2_v1:.4f} ms")
    print(f"  🔄 Iterations: {iter2_v1}")
    print()

    # V2
    grid2_v2 = create_puzzle_2_v2()
    solver2_v2 = TangoSolverV2(grid2_v2)
    solved2_v2, iter2_v2, time2_v2, back2_v2 = solver2_v2.solve()

    print(f"V2 (Hybrid: Propagation + Backtracking):")
    print(f"  ✓ Solved: {solved2_v2}")
    print(f"  ⏱️  Time: {time2_v2:.4f} ms")
    print(f"  🔄 Iterations: {iter2_v2}")
    print(f"  🔙 Backtracks: {back2_v2}")
    print()

    # Comparison
    speedup2 = time2_v1 / time2_v2 if time2_v2 > 0 else float('inf')
    winner2 = "V1" if time2_v1 < time2_v2 else "V2"
    diff2 = abs(time2_v1 - time2_v2)

    print(f"🏆 Winner: {winner2} (faster by {diff2:.4f} ms)")
    print(f"📊 Speedup: {speedup2:.2f}x")
    print()

    # Overall Summary
    print("=" * 70)
    print("📊 OVERALL SUMMARY")
    print("=" * 70)

    total_v1 = time1_v1 + time2_v1
    total_v2 = time1_v2 + time2_v2
    overall_winner = "V1" if total_v1 < total_v2 else "V2"
    overall_speedup = max(total_v1, total_v2) / min(total_v1, total_v2)

    print(f"V1 Total Time: {total_v1:.4f} ms")
    print(f"V2 Total Time: {total_v2:.4f} ms")
    print()
    print(f"🏆 Overall Winner: {overall_winner}")
    print(f"📈 Overall Speedup: {overall_speedup:.2f}x")
    print()

    # Analysis
    print("=" * 70)
    print("🔍 ANALYSIS")
    print("=" * 70)
    print()
    print("V1 Strengths:")
    print("  - Simpler implementation")
    print("  - Faster on easy puzzles (less overhead)")
    print("  - Pure constraint propagation")
    print()
    print("V2 Strengths:")
    print("  - Intelligent backtracking with MRV heuristic")
    print("  - Can solve puzzles that V1 cannot")
    print("  - Domain tracking for forward checking")
    print("  - Better for harder puzzles requiring search")
    print()

    if back1_v2 == 0 and back2_v2 == 0:
        print("💡 Note: These puzzles were solved by pure constraint propagation")
        print("   in both versions. Backtracking was not needed!")
        print("   Try harder puzzles to see V2's backtracking advantage.")


if __name__ == "__main__":
    main()
