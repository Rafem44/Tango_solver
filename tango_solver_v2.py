#!/usr/bin/env python3
"""
Tango Puzzle Solver V2 - Optimized with Backtracking

Improvements over V1:
- Hybrid approach: Constraint propagation + intelligent backtracking
- MRV heuristic (Minimum Remaining Values) - choose cell with fewest options
- Forward checking - eliminate impossible values
- More efficient constraint checking
- Early termination when solution found
"""

from typing import List, Optional, Tuple, Set
import copy
import time


class TangoGridV2:
    """Optimized Tango puzzle grid with domain tracking"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # Grid: None = empty, 0 or 1 = filled
        self.grid: List[List[Optional[int]]] = [[None for _ in range(cols)] for _ in range(rows)]
        # Track possible values for each cell
        self.domains: List[List[Set[int]]] = [[{0, 1} for _ in range(cols)] for _ in range(rows)]

    def set_cell(self, row: int, col: int, value: Optional[int]):
        """Set a cell value and update domain"""
        if value is not None and value not in [0, 1]:
            raise ValueError(f"Cell value must be None, 0, or 1, got {value}")
        self.grid[row][col] = value
        if value is not None:
            self.domains[row][col] = {value}

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

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cells sorted by domain size (MRV heuristic)"""
        empty = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    empty.append((row, col, len(self.domains[row][col])))
        # Sort by domain size (smallest first - MRV heuristic)
        empty.sort(key=lambda x: x[2])
        return [(r, c) for r, c, _ in empty]

    def __str__(self) -> str:
        """String representation of the grid"""
        result = []
        for row in self.grid:
            row_str = ' '.join(['.' if cell is None else str(cell) for cell in row])
            result.append(row_str)
        return '\n'.join(result)

    def copy(self) -> 'TangoGridV2':
        """Create a deep copy of the grid"""
        new_grid = TangoGridV2(self.rows, self.cols)
        new_grid.grid = copy.deepcopy(self.grid)
        new_grid.domains = copy.deepcopy(self.domains)
        return new_grid


class TangoSolverV2:
    """V2: Hybrid solver with constraint propagation + backtracking"""

    def __init__(self, grid: TangoGridV2):
        self.grid = grid
        self.changes_made = False
        self.backtracks = 0

    def solve(self, max_iterations: int = 100) -> Tuple[bool, int, float, int]:
        """
        Solve using hybrid approach: propagation + backtracking

        Returns:
            Tuple of (is_solved, iterations, elapsed_time_ms, backtracks)
        """
        start_time = time.time()

        # Phase 1: Constraint propagation
        iteration = 0
        while not self.grid.is_complete() and iteration < max_iterations:
            self.changes_made = False
            self._propagate_constraints()

            if not self.changes_made:
                break
            iteration += 1

        # Phase 2: Backtracking if needed
        if not self.grid.is_complete():
            self._backtracking_search()

        elapsed_time = (time.time() - start_time) * 1000
        return self.grid.is_complete(), iteration, elapsed_time, self.backtracks

    def _propagate_constraints(self):
        """Apply all constraint rules to rows and columns"""
        # Process rows
        for row in range(self.grid.rows):
            self._process_line(row, is_row=True)

        # Process columns
        for col in range(self.grid.cols):
            self._process_line(col, is_row=False)

    def _backtracking_search(self) -> bool:
        """Intelligent backtracking with MRV heuristic"""
        if self.grid.is_complete():
            return True

        # MRV: Choose cell with minimum remaining values
        empty_cells = self.grid.get_empty_cells()
        if not empty_cells:
            return False

        row, col = empty_cells[0]

        # Try each possible value
        for value in list(self.grid.domains[row][col]):
            # Save state
            old_grid = self.grid.copy()

            # Try assignment
            self.grid.set_cell(row, col, value)

            # Forward checking & constraint propagation
            if self._is_valid_assignment(row, col, value):
                self._propagate_constraints()

                # Recurse
                if self._backtracking_search():
                    return True

            # Backtrack
            self.backtracks += 1
            self.grid = old_grid

        return False

    def _is_valid_assignment(self, row: int, col: int, value: int) -> bool:
        """Check if assignment violates any constraints"""
        # Check row constraints
        if not self._check_line_valid(row, True):
            return False

        # Check column constraints
        if not self._check_line_valid(col, False):
            return False

        return True

    def _check_line_valid(self, index: int, is_row: bool) -> bool:
        """Check if a line violates any constraints"""
        line = self._get_line(index, is_row)
        length = len(line)

        # Count values
        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)

        # Check balance constraint
        if length % 2 == 0:
            target = length // 2
            if count_zeros > target or count_ones > target:
                return False

        # Check no three consecutive
        for i in range(length - 2):
            if line[i] is not None and line[i+1] is not None and line[i+2] is not None:
                if line[i] == line[i+1] == line[i+2]:
                    return False

        return True

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

        # Rule 0: Balance constraint
        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)
        count_empty = sum(1 for cell in line if cell is None)

        if length % 2 == 0:
            target = length // 2

            # Fill remaining cells if one value is complete
            if count_zeros == target and count_empty > 0:
                for i in range(length):
                    if line[i] is None:
                        self._set_cell_in_line(index, i, 1, is_row)
            elif count_ones == target and count_empty > 0:
                for i in range(length):
                    if line[i] is None:
                        self._set_cell_in_line(index, i, 0, is_row)

        # Refresh line
        line = self._get_line(index, is_row)

        # Rule 1: Sandwich rule
        for i in range(1, length - 1):
            prev = line[i-1]
            next_val = line[i+1]
            current = line[i]

            if prev is not None and next_val is not None and prev == next_val and current is None:
                opposite = 1 - prev
                self._set_cell_in_line(index, i, opposite, is_row)

        # Rule 2: Consecutive pair rule
        line = self._get_line(index, is_row)
        for i in range(length - 1):
            current = line[i]
            next_val = line[i+1]

            if current is not None and next_val is not None and current == next_val:
                opposite = 1 - current

                if i > 0 and line[i-1] is None:
                    self._set_cell_in_line(index, i-1, opposite, is_row)
                if i + 2 < length and line[i+2] is None:
                    self._set_cell_in_line(index, i+2, opposite, is_row)

        # Rule 3: No three consecutive
        line = self._get_line(index, is_row)
        for i in range(length - 2):
            vals = [line[i], line[i+1], line[i+2]]

            if vals[0] is not None and vals[1] is not None and vals[0] == vals[1] and vals[2] is None:
                self._set_cell_in_line(index, i+2, 1 - vals[0], is_row)
            if vals[1] is not None and vals[2] is not None and vals[1] == vals[2] and vals[0] is None:
                self._set_cell_in_line(index, i, 1 - vals[1], is_row)
            if vals[0] is not None and vals[2] is not None and vals[0] == vals[2] and vals[1] is None:
                self._set_cell_in_line(index, i+1, 1 - vals[0], is_row)

    def _set_cell_in_line(self, line_index: int, position: int, value: int, is_row: bool):
        """Set a cell value in a specific line"""
        if is_row:
            self._set_cell_safe(line_index, position, value)
        else:
            self._set_cell_safe(position, line_index, value)


# Import example grid creators from V1
def create_grid_from_image_v2() -> TangoGridV2:
    """First puzzle for V2"""
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


def create_grid_from_image_2_v2() -> TangoGridV2:
    """Second puzzle for V2"""
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
    """Compare V1 vs V2 performance"""
    print("=== Tango Puzzle Solver V2 ===")
    print("Hybrid: Constraint Propagation + Intelligent Backtracking\n")

    # Test Puzzle 1
    print("=" * 60)
    print("Puzzle 1 - 18 initial cells (50% filled)")
    print("=" * 60)
    grid1 = create_grid_from_image_v2()
    print("Initial grid:")
    print(grid1)
    print()

    solver1 = TangoSolverV2(grid1)
    solved1, iterations1, time1, backtracks1 = solver1.solve()

    print("Solution:")
    print(grid1)
    print(f"\n✓ Solved: {solved1}")
    print(f"📊 Stats:")
    print(f"  - Propagation iterations: {iterations1}")
    print(f"  - Backtracking steps: {backtracks1}")
    print(f"  - Time: {time1:.4f} ms")

    if solved1:
        print("\nSymbolic representation:")
        for row in grid1.grid:
            row_str = ' '.join(['◆' if cell == 0 else '●' for cell in row])
            print(row_str)

    # Test Puzzle 2
    print("\n" + "=" * 60)
    print("Puzzle 2 - 11 initial cells (31% filled) [HARDER]")
    print("=" * 60)
    grid2 = create_grid_from_image_2_v2()
    print("Initial grid:")
    print(grid2)
    print()

    solver2 = TangoSolverV2(grid2)
    solved2, iterations2, time2, backtracks2 = solver2.solve()

    print("Solution:")
    print(grid2)
    print(f"\n✓ Solved: {solved2}")
    print(f"📊 Stats:")
    print(f"  - Propagation iterations: {iterations2}")
    print(f"  - Backtracking steps: {backtracks2}")
    print(f"  - Time: {time2:.4f} ms")

    if solved2:
        print("\nSymbolic representation:")
        for row in grid2.grid:
            row_str = ' '.join(['◆' if cell == 0 else '●' for cell in row])
            print(row_str)

    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Puzzle 1: {time1:.4f} ms ({iterations1} iter, {backtracks1} backtracks)")
    print(f"Puzzle 2: {time2:.4f} ms ({iterations2} iter, {backtracks2} backtracks)")
    print(f"Total time: {time1 + time2:.4f} ms")


if __name__ == "__main__":
    main()
