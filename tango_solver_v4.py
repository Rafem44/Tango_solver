#!/usr/bin/env python3
"""
Tango Puzzle Solver V4 - Fixed with Strict Validation

Fixes from V3:
- Strict validation of ALL constraints before accepting assignments
- No three consecutive same values
- Strict balance enforcement (exactly N/2 zeros and N/2 ones)
- Explicit constraint checking (= and ×)
- Rejects invalid states immediately during backtracking
"""

from typing import List, Optional, Tuple, Set
import copy
import time


class Constraint:
    """Represents a constraint between two adjacent cells"""
    def __init__(self, cell1: Tuple[int, int], cell2: Tuple[int, int], constraint_type: str):
        self.cell1 = cell1
        self.cell2 = cell2
        self.type = constraint_type


class TangoGridV4:
    """Tango puzzle grid with strict validation"""

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
        """Add equality (=) or inequality (×) constraint"""
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
        """String representation"""
        result = []
        for row in self.grid:
            row_str = ' '.join(['.' if cell is None else str(cell) for cell in row])
            result.append(row_str)
        return '\n'.join(result)

    def copy(self) -> 'TangoGridV4':
        """Deep copy"""
        new_grid = TangoGridV4(self.rows, self.cols)
        new_grid.grid = copy.deepcopy(self.grid)
        new_grid.domains = copy.deepcopy(self.domains)
        new_grid.constraints = copy.deepcopy(self.constraints)
        return new_grid


class TangoSolverV4:
    """V4: Fixed solver with strict validation"""

    def __init__(self, grid: TangoGridV4):
        self.grid = grid
        self.changes_made = False
        self.backtracks = 0
        self.validations = 0

    def solve(self, max_iterations: int = 100) -> Tuple[bool, int, float, int]:
        """Solve with strict validation"""
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

            if constraint.type == "=":
                if val1 is not None and val2 is None:
                    if self._can_set_cell(r2, c2, val1):
                        self._set_cell_safe(r2, c2, val1)
                elif val2 is not None and val1 is None:
                    if self._can_set_cell(r1, c1, val2):
                        self._set_cell_safe(r1, c1, val2)

            elif constraint.type == "×":
                if val1 is not None and val2 is None:
                    opposite = 1 - val1
                    if self._can_set_cell(r2, c2, opposite):
                        self._set_cell_safe(r2, c2, opposite)
                elif val2 is not None and val1 is None:
                    opposite = 1 - val2
                    if self._can_set_cell(r1, c1, opposite):
                        self._set_cell_safe(r1, c1, opposite)

    def _can_set_cell(self, row: int, col: int, value: int) -> bool:
        """Check if setting this cell would be valid"""
        if self.grid.get_cell(row, col) is not None:
            return False

        # Temporarily set to test
        old_val = self.grid.get_cell(row, col)
        self.grid.set_cell(row, col, value)

        valid = self._is_grid_valid()

        # Restore
        self.grid.set_cell(row, col, old_val)

        return valid

    def _backtracking_search(self) -> bool:
        """Intelligent backtracking with strict validation"""
        if self.grid.is_complete():
            return self._is_grid_valid()

        empty_cells = self.grid.get_empty_cells()
        if not empty_cells:
            return False

        row, col = empty_cells[0]

        for value in [0, 1]:
            old_grid = self.grid.copy()

            self.grid.set_cell(row, col, value)

            # STRICT VALIDATION before proceeding
            if self._is_assignment_valid(row, col, value):
                self._propagate_constraints()

                if self._backtracking_search():
                    return True

            self.backtracks += 1
            self.grid = old_grid

        return False

    def _is_assignment_valid(self, row: int, col: int, value: int) -> bool:
        """
        STRICT validation of assignment
        Returns True only if this assignment doesn't violate ANY constraint
        """
        self.validations += 1

        # Check explicit constraints (= and ×)
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

        # Check three consecutive in row
        if not self._check_no_three_consecutive_in_row(row):
            return False

        # Check three consecutive in column
        if not self._check_no_three_consecutive_in_col(col):
            return False

        # Check balance constraints
        if not self._check_balance_valid(row, True):
            return False
        if not self._check_balance_valid(col, False):
            return False

        return True

    def _check_no_three_consecutive_in_row(self, row: int) -> bool:
        """Check no three consecutive same values in this row"""
        for c in range(self.grid.cols - 2):
            vals = [self.grid.get_cell(row, c),
                   self.grid.get_cell(row, c+1),
                   self.grid.get_cell(row, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                return False
        return True

    def _check_no_three_consecutive_in_col(self, col: int) -> bool:
        """Check no three consecutive same values in this column"""
        for r in range(self.grid.rows - 2):
            vals = [self.grid.get_cell(r, col),
                   self.grid.get_cell(r+1, col),
                   self.grid.get_cell(r+2, col)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                return False
        return True

    def _check_balance_valid(self, index: int, is_row: bool) -> bool:
        """Check balance constraint is not violated"""
        line = self._get_line(index, is_row)
        length = len(line)

        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)

        if length % 2 == 0:
            target = length // 2
            # Too many of either value
            if count_zeros > target or count_ones > target:
                return False

        return True

    def _is_grid_valid(self) -> bool:
        """Check if entire grid is valid"""
        # Check all rows
        for r in range(self.grid.rows):
            if not self._check_no_three_consecutive_in_row(r):
                return False
            if not self._check_balance_valid(r, True):
                return False

        # Check all columns
        for c in range(self.grid.cols):
            if not self._check_no_three_consecutive_in_col(c):
                return False
            if not self._check_balance_valid(c, False):
                return False

        # Check explicit constraints
        for constraint in self.grid.constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2
            val1 = self.grid.get_cell(r1, c1)
            val2 = self.grid.get_cell(r2, c2)

            if val1 is not None and val2 is not None:
                if constraint.type == "=" and val1 != val2:
                    return False
                if constraint.type == "×" and val1 == val2:
                    return False

        return True

    def _get_line(self, index: int, is_row: bool) -> List[Optional[int]]:
        """Get a row or column"""
        if is_row:
            return self.grid.grid[index]
        else:
            return [self.grid.grid[row][index] for row in range(self.grid.rows)]

    def _set_cell_safe(self, row: int, col: int, value: int):
        """Set a cell if empty and valid"""
        if self.grid.get_cell(row, col) is None:
            if self._can_set_cell(row, col, value):
                self.grid.set_cell(row, col, value)
                self.changes_made = True

    def _process_line(self, index: int, is_row: bool):
        """Process line with strict validation"""
        line = self._get_line(index, is_row)
        length = len(line)

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

        line = self._get_line(index, is_row)

        # Sandwich rule
        for i in range(1, length - 1):
            prev = line[i-1]
            next_val = line[i+1]
            current = line[i]

            if prev is not None and next_val is not None and prev == next_val and current is None:
                opposite = 1 - prev
                self._set_cell_in_line(index, i, opposite, is_row)

        # Consecutive pair rule
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

        # No three consecutive
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
        """Set cell in line"""
        if is_row:
            self._set_cell_safe(line_index, position, value)
        else:
            self._set_cell_safe(position, line_index, value)


def main():
    """Demo V4"""
    print("=== Tango Puzzle Solver V4 ===")
    print("With Strict Validation\n")

    grid = TangoGridV4(4, 4)
    grid.set_cell(0, 0, 0)
    grid.set_cell(1, 3, 1)
    grid.add_constraint(0, 0, 0, 1, "×")
    grid.add_constraint(1, 0, 1, 1, "=")

    print("Initial:")
    print(grid)
    print()

    solver = TangoSolverV4(grid)
    solved, iterations, time_ms, backtracks = solver.solve()

    print("Solution:")
    print(grid)
    print(f"\n✓ Solved: {solved}")
    print(f"📊 Iterations: {iterations}, Backtracks: {backtracks}")
    print(f"⏱️  Time: {time_ms:.4f} ms")


if __name__ == "__main__":
    main()
