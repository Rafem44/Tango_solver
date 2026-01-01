#!/usr/bin/env python3
"""
Tango Puzzle Solver

Based on the algorithm:
- Grid filled with 0s and 1s
- Each cell has 3 states: empty (None), 0, or 1
- Process line by line, then column by column
- Apply constraint rules:
  1. If n-1 = n+1, then n ≠ n+1 (if two neighbors are equal, middle is different)
  2. If n = n+1, then n-1 = n+2 ≠ n (if two consecutive equal, previous equals two positions after)
  3. Equal balance: Each line must have an equal number of 0s and 1s
"""

from typing import List, Optional, Tuple
import copy
import time


class TangoGrid:
    """Represents a Tango puzzle grid"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # Grid: None = empty, 0 or 1 = filled
        self.grid: List[List[Optional[int]]] = [[None for _ in range(cols)] for _ in range(rows)]

    def set_cell(self, row: int, col: int, value: Optional[int]):
        """Set a cell value (None, 0, or 1)"""
        if value is not None and value not in [0, 1]:
            raise ValueError(f"Cell value must be None, 0, or 1, got {value}")
        self.grid[row][col] = value

    def get_cell(self, row: int, col: int) -> Optional[int]:
        """Get a cell value"""
        return self.grid[row][col]

    def is_complete(self) -> bool:
        """Check if all cells are filled"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    return False
        return True

    def __str__(self) -> str:
        """String representation of the grid"""
        result = []
        for row in self.grid:
            row_str = ' '.join(['.' if cell is None else str(cell) for cell in row])
            result.append(row_str)
        return '\n'.join(result)

    def copy(self) -> 'TangoGrid':
        """Create a deep copy of the grid"""
        new_grid = TangoGrid(self.rows, self.cols)
        new_grid.grid = copy.deepcopy(self.grid)
        return new_grid


class TangoSolver:
    """Solves Tango puzzles using constraint propagation"""

    def __init__(self, grid: TangoGrid):
        self.grid = grid
        self.changes_made = False

    def solve(self, max_iterations: int = 100) -> Tuple[bool, int, float]:
        """
        Solve the puzzle using iterative constraint propagation

        Returns:
            Tuple of (is_solved, iterations, elapsed_time_ms)
            - is_solved: True if puzzle is completely solved
            - iterations: Number of iterations performed
            - elapsed_time_ms: Time taken in milliseconds
        """
        start_time = time.time()
        iteration = 0

        while not self.grid.is_complete() and iteration < max_iterations:
            self.changes_made = False

            # Process rows (line by line)
            for row in range(self.grid.rows):
                self._process_line(row, is_row=True)

            # Process columns (column by column)
            for col in range(self.grid.cols):
                self._process_line(col, is_row=False)

            # If no changes were made, we're stuck
            if not self.changes_made:
                break

            iteration += 1

        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return self.grid.is_complete(), iteration, elapsed_time

    def _get_line(self, index: int, is_row: bool) -> List[Optional[int]]:
        """Get a row or column as a list"""
        if is_row:
            return self.grid.grid[index]
        else:
            return [self.grid.grid[row][index] for row in range(self.grid.rows)]

    def _set_cell_safe(self, row: int, col: int, value: int):
        """Set a cell value if it's currently empty"""
        if self.grid.get_cell(row, col) is None:
            self.grid.set_cell(row, col, value)
            self.changes_made = True

    def _process_line(self, index: int, is_row: bool):
        """Process a single row or column applying constraint rules"""
        line = self._get_line(index, is_row)
        length = len(line)

        # Rule 0: Balance constraint - equal number of 0s and 1s
        # Count current 0s and 1s in the line
        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)
        count_empty = sum(1 for cell in line if cell is None)

        # If line length is even, we need equal 0s and 1s
        if length % 2 == 0:
            target = length // 2

            # If we have enough zeros, fill remaining with ones
            if count_zeros == target and count_empty > 0:
                for i in range(length):
                    if line[i] is None:
                        self._set_cell_in_line(index, i, 1, is_row)

            # If we have enough ones, fill remaining with zeros
            elif count_ones == target and count_empty > 0:
                for i in range(length):
                    if line[i] is None:
                        self._set_cell_in_line(index, i, 0, is_row)

        # Refresh line after balance constraint
        line = self._get_line(index, is_row)

        # Apply constraint rules
        for i in range(length):
            # Rule 1: If n-1 = n+1, then n ≠ n+1
            # This means if two neighbors are equal, the middle must be different
            if i > 0 and i < length - 1:
                prev = line[i-1]
                next_val = line[i+1]
                current = line[i]

                if prev is not None and next_val is not None and prev == next_val:
                    # Middle must be different from neighbors
                    if current is None:
                        opposite = 1 - prev
                        self._set_cell_in_line(index, i, opposite, is_row)

            # Rule 2: If n = n+1, then n-1 = n+2 ≠ n
            # If two consecutive cells are equal, the one before equals the one two positions after
            if i < length - 1:
                current = line[i]
                next_val = line[i+1]

                if current is not None and next_val is not None and current == next_val:
                    # n-1 should equal n+2 and both should be different from n
                    opposite = 1 - current

                    # Set n-1 if empty
                    if i > 0 and line[i-1] is None:
                        self._set_cell_in_line(index, i-1, opposite, is_row)

                    # Set n+2 if empty
                    if i + 2 < length and line[i+2] is None:
                        self._set_cell_in_line(index, i+2, opposite, is_row)

            # Additional rule: No three consecutive same values
            if i < length - 2:
                vals = [line[i], line[i+1], line[i+2]]

                # If two are known and equal, the third must be different
                if vals[0] is not None and vals[1] is not None and vals[0] == vals[1] and vals[2] is None:
                    opposite = 1 - vals[0]
                    self._set_cell_in_line(index, i+2, opposite, is_row)

                if vals[1] is not None and vals[2] is not None and vals[1] == vals[2] and vals[0] is None:
                    opposite = 1 - vals[1]
                    self._set_cell_in_line(index, i, opposite, is_row)

                if vals[0] is not None and vals[2] is not None and vals[0] == vals[2] and vals[1] is None:
                    opposite = 1 - vals[0]
                    self._set_cell_in_line(index, i+1, opposite, is_row)

    def _set_cell_in_line(self, line_index: int, position: int, value: int, is_row: bool):
        """Set a cell value in a specific line (row or column)"""
        if is_row:
            self._set_cell_safe(line_index, position, value)
        else:
            self._set_cell_safe(position, line_index, value)


def create_example_grid_1() -> TangoGrid:
    """Create an example Tango puzzle (5x5)"""
    grid = TangoGrid(5, 5)

    # Set initial values from the image
    grid.set_cell(0, 0, 0)
    grid.set_cell(0, 1, 1)
    grid.set_cell(0, 2, 0)
    grid.set_cell(0, 3, 0)

    return grid


def create_example_grid_2() -> TangoGrid:
    """Create a simple test puzzle (4x4 with balance constraint)"""
    grid = TangoGrid(4, 4)

    # Create a pattern with some known values
    # Each row and column should have 2 zeros and 2 ones
    grid.set_cell(0, 0, 0)
    grid.set_cell(0, 1, 0)  # Row 0 has 2 zeros, so rest must be ones
    grid.set_cell(1, 0, 1)
    grid.set_cell(1, 2, 0)
    grid.set_cell(2, 1, 1)
    grid.set_cell(3, 2, 1)

    return grid


def create_example_grid_3() -> TangoGrid:
    """Create a 6x6 puzzle with better demonstration of rules"""
    grid = TangoGrid(6, 6)

    # Each row and column should have 3 zeros and 3 ones
    grid.set_cell(0, 0, 0)
    grid.set_cell(0, 1, 1)
    grid.set_cell(0, 2, 0)
    grid.set_cell(1, 0, 1)
    grid.set_cell(1, 3, 1)
    grid.set_cell(2, 2, 1)
    grid.set_cell(3, 1, 0)
    grid.set_cell(4, 4, 0)
    grid.set_cell(5, 5, 1)

    return grid


def create_grid_from_image() -> TangoGrid:
    """
    Create a 6x6 puzzle from the provided image (first puzzle)
    Diamonds (◆) = 0, Circles (●) = 1, Empty = None
    """
    grid = TangoGrid(6, 6)

    # Row 0: ◆ ◆ _ ● ◆ _
    grid.set_cell(0, 0, 0)
    grid.set_cell(0, 1, 0)
    grid.set_cell(0, 3, 1)
    grid.set_cell(0, 4, 0)

    # Row 1: ◆ ◆ _ _ _ ●
    grid.set_cell(1, 0, 0)
    grid.set_cell(1, 1, 0)
    grid.set_cell(1, 5, 1)

    # Row 2: ● _ _ _ ● ◆
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 5, 0)

    # Row 3: ● ● ◆ ◆ ● ◆
    grid.set_cell(3, 0, 1)
    grid.set_cell(3, 1, 1)
    grid.set_cell(3, 2, 0)
    grid.set_cell(3, 3, 0)
    grid.set_cell(3, 4, 1)
    grid.set_cell(3, 5, 0)

    # Row 4: ◆ ◆ ● _ ◆ ●
    grid.set_cell(4, 0, 0)
    grid.set_cell(4, 1, 0)
    grid.set_cell(4, 2, 1)
    grid.set_cell(4, 4, 0)
    grid.set_cell(4, 5, 1)

    # Row 5: _ ● ◆ _ _ ◆
    grid.set_cell(5, 1, 1)
    grid.set_cell(5, 2, 0)
    grid.set_cell(5, 5, 0)

    return grid


def create_grid_from_image_2() -> TangoGrid:
    """
    Create a 6x6 puzzle from the second provided image
    Diamonds (◆) = 0, Circles (●) = 1, Empty = None
    """
    grid = TangoGrid(6, 6)

    # Row 0: ● _ _ _ ◆ _
    grid.set_cell(0, 0, 1)
    grid.set_cell(0, 4, 0)

    # Row 1: _ _ ◆ _ _ _
    grid.set_cell(1, 2, 0)

    # Row 2: _ _ _ _ _ ◆
    grid.set_cell(2, 5, 0)

    # Row 3: _ _ _ ◆ ● ◆
    grid.set_cell(3, 3, 0)
    grid.set_cell(3, 4, 1)
    grid.set_cell(3, 5, 0)

    # Row 4: _ _ ◆ ◆ ● ●
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 3, 0)
    grid.set_cell(4, 4, 1)
    grid.set_cell(4, 5, 1)

    # Row 5: _ _ _ ● _ ◆
    grid.set_cell(5, 3, 1)
    grid.set_cell(5, 5, 0)

    return grid


def main():
    """Main execution"""
    print("=== Tango Puzzle Solver ===\n")

    # Example 1: From the image
    print("Example 1: Grid from image (5x5)")
    print("Initial grid:")
    grid1 = create_example_grid_1()
    print(grid1)
    print()

    solver1 = TangoSolver(grid1)
    solved1, iterations1, time1 = solver1.solve()

    print("After applying constraints:")
    print(grid1)
    print(f"Solved: {solved1}")
    print(f"Iterations: {iterations1}")
    print(f"Time: {time1:.3f} ms\n")

    # Example 2: 4x4 Test puzzle with balance
    print("=" * 40)
    print("\nExample 2: 4x4 puzzle with balance constraint")
    print("Initial grid:")
    grid2 = create_example_grid_2()
    print(grid2)
    print()

    solver2 = TangoSolver(grid2)
    solved2, iterations2, time2 = solver2.solve()

    print("After applying constraints:")
    print(grid2)
    print(f"Solved: {solved2}")
    print(f"Iterations: {iterations2}")
    print(f"Time: {time2:.3f} ms\n")

    # Example 3: 6x6 puzzle
    print("=" * 40)
    print("\nExample 3: 6x6 puzzle")
    print("Initial grid:")
    grid3 = create_example_grid_3()
    print(grid3)
    print()

    solver3 = TangoSolver(grid3)
    solved3, iterations3, time3 = solver3.solve()

    print("After applying constraints:")
    print(grid3)
    print(f"Solved: {solved3}")
    print(f"Iterations: {iterations3}")
    print(f"Time: {time3:.3f} ms\n")

    # Example 4: Puzzle from user's image
    print("=" * 40)
    print("\nExample 4: Puzzle from image (◆=0, ●=1)")
    print("Initial grid:")
    grid4 = create_grid_from_image()
    print(grid4)
    print()

    solver4 = TangoSolver(grid4)
    solved4, iterations4, time4 = solver4.solve()

    print("After applying constraints:")
    print(grid4)
    print(f"Solved: {solved4}")
    print(f"Iterations: {iterations4}")
    print(f"Time: {time4:.3f} ms\n")

    # Display with symbols for better visualization
    if solved4:
        print("Solution with symbols:")
        for row in grid4.grid:
            row_str = ' '.join(['◆' if cell == 0 else '●' for cell in row])
            print(row_str)

    # Example 5: Second puzzle from user's image (more challenging)
    print("\n" + "=" * 40)
    print("\nExample 5: Second puzzle from image (◆=0, ●=1)")
    print("Initial grid:")
    grid5 = create_grid_from_image_2()
    print(grid5)
    print()

    solver5 = TangoSolver(grid5)
    solved5, iterations5, time5 = solver5.solve()

    print("After applying constraints:")
    print(grid5)
    print(f"Solved: {solved5}")
    print(f"Iterations: {iterations5}")
    print(f"Time: {time5:.3f} ms\n")

    # Display with symbols for better visualization
    if solved5:
        print("Solution with symbols:")
        for row in grid5.grid:
            row_str = ' '.join(['◆' if cell == 0 else '●' for cell in row])
            print(row_str)


if __name__ == "__main__":
    main()
