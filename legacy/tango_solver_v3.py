#!/usr/bin/env python3
"""
Tango Puzzle Solver V3 - With Equality/Inequality Constraints

New features:
- Support for "=" constraints (adjacent cells must be equal)
- Support for "×" constraints (adjacent cells must be different)
- Enhanced constraint validation
- Better suited for real Tango puzzles with visual constraints
"""

from typing import List, Optional, Tuple, Set, Dict
import copy
import time


class Constraint:
    """Represents a constraint between two adjacent cells"""
    def __init__(self, cell1: Tuple[int, int], cell2: Tuple[int, int], constraint_type: str):
        self.cell1 = cell1  # (row, col)
        self.cell2 = cell2  # (row, col)
        self.type = constraint_type  # "=" or "×"


class TangoGridV3:
    """Tango puzzle grid with equality/inequality constraints"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Optional[int]]] = [[None for _ in range(cols)] for _ in range(rows)]
        self.constraints: List[Constraint] = []
        self.domains: List[List[Set[int]]] = [[{0, 1} for _ in range(cols)] for _ in range(rows)]

    def set_cell(self, row: int, col: int, value: Optional[int]):
        """Set a cell value"""
        if value is not None and value not in [0, 1]:
            raise ValueError(f"Cell value must be None, 0, or 1, got {value}")
        self.grid[row][col] = value
        if value is not None:
            self.domains[row][col] = {value}

    def add_constraint(self, row1: int, col1: int, row2: int, col2: int, constraint_type: str):
        """Add equality (=) or inequality (×) constraint between adjacent cells"""
        if constraint_type not in ["=", "×"]:
            raise ValueError(f"Constraint type must be '=' or '×', got {constraint_type}")
        self.constraints.append(Constraint((row1, col1), (row2, col2), constraint_type))

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
        empty.sort(key=lambda x: x[2])
        return [(r, c) for r, c, _ in empty]

    def __str__(self) -> str:
        """String representation of the grid"""
        result = []
        for row in self.grid:
            row_str = ' '.join(['.' if cell is None else str(cell) for cell in row])
            result.append(row_str)
        return '\n'.join(result)

    def copy(self) -> 'TangoGridV3':
        """Create a deep copy of the grid"""
        new_grid = TangoGridV3(self.rows, self.cols)
        new_grid.grid = copy.deepcopy(self.grid)
        new_grid.domains = copy.deepcopy(self.domains)
        new_grid.constraints = copy.deepcopy(self.constraints)
        return new_grid


class TangoSolverV3:
    """V3: Enhanced solver with explicit equality/inequality constraints"""

    def __init__(self, grid: TangoGridV3):
        self.grid = grid
        self.changes_made = False
        self.backtracks = 0

    def solve(self, max_iterations: int = 100) -> Tuple[bool, int, float, int]:
        """
        Solve using hybrid approach with constraint checking

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
        """Apply all constraint rules"""
        # Apply explicit = and × constraints
        self._apply_explicit_constraints()

        # Process rows
        for row in range(self.grid.rows):
            self._process_line(row, is_row=True)

        # Process columns
        for col in range(self.grid.cols):
            self._process_line(col, is_row=False)

    def _apply_explicit_constraints(self):
        """Apply equality and inequality constraints"""
        for constraint in self.grid.constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2
            val1 = self.grid.get_cell(r1, c1)
            val2 = self.grid.get_cell(r2, c2)

            if constraint.type == "=":  # Cells must be equal
                if val1 is not None and val2 is None:
                    self._set_cell_safe(r2, c2, val1)
                elif val2 is not None and val1 is None:
                    self._set_cell_safe(r1, c1, val2)

            elif constraint.type == "×":  # Cells must be different
                if val1 is not None and val2 is None:
                    opposite = 1 - val1
                    self._set_cell_safe(r2, c2, opposite)
                elif val2 is not None and val1 is None:
                    opposite = 1 - val2
                    self._set_cell_safe(r1, c1, opposite)

    def _backtracking_search(self) -> bool:
        """Intelligent backtracking with MRV heuristic"""
        if self.grid.is_complete():
            return True

        empty_cells = self.grid.get_empty_cells()
        if not empty_cells:
            return False

        row, col = empty_cells[0]

        for value in list(self.grid.domains[row][col]):
            old_grid = self.grid.copy()

            self.grid.set_cell(row, col, value)

            if self._is_valid_assignment(row, col, value):
                self._propagate_constraints()

                if self._backtracking_search():
                    return True

            self.backtracks += 1
            self.grid = old_grid

        return False

    def _is_valid_assignment(self, row: int, col: int, value: int) -> bool:
        """Check if assignment violates any constraints"""
        # Check explicit constraints
        for constraint in self.grid.constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2

            if (r1, c1) == (row, col):
                other_val = self.grid.get_cell(r2, c2)
                if other_val is not None:
                    if constraint.type == "=" and value != other_val:
                        return False
                    if constraint.type == "×" and value == other_val:
                        return False

            if (r2, c2) == (row, col):
                other_val = self.grid.get_cell(r1, c1)
                if other_val is not None:
                    if constraint.type == "=" and value != other_val:
                        return False
                    if constraint.type == "×" and value == other_val:
                        return False

        # Check row/column constraints
        if not self._check_line_valid(row, True):
            return False
        if not self._check_line_valid(col, False):
            return False

        return True

    def _check_line_valid(self, index: int, is_row: bool) -> bool:
        """Check if a line violates any constraints"""
        line = self._get_line(index, is_row)
        length = len(line)

        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)

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


def main():
    """Demo V3 with constraints"""
    print("=== Tango Puzzle Solver V3 ===")
    print("With Equality (=) and Inequality (×) Constraints\n")

    # Create a simple test puzzle
    grid = TangoGridV3(4, 4)

    # Add some initial values
    grid.set_cell(0, 0, 0)
    grid.set_cell(1, 3, 1)

    # Add constraints
    # Row 0: cells (0,0) and (0,1) must be different (×)
    grid.add_constraint(0, 0, 0, 1, "×")

    # Row 1: cells (1,0) and (1,1) must be equal (=)
    grid.add_constraint(1, 0, 1, 1, "=")

    print("Initial grid:")
    print(grid)
    print("\nConstraints:")
    for c in grid.constraints:
        print(f"  {c.cell1} {c.type} {c.cell2}")
    print()

    solver = TangoSolverV3(grid)
    solved, iterations, time_ms, backtracks = solver.solve()

    print("Solution:")
    print(grid)
    print(f"\n✓ Solved: {solved}")
    print(f"📊 Stats:")
    print(f"  - Iterations: {iterations}")
    print(f"  - Backtracks: {backtracks}")
    print(f"  - Time: {time_ms:.4f} ms")


if __name__ == "__main__":
    main()
