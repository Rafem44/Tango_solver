#!/usr/bin/env python3
"""
Tango Solver Simple: V1 + Explicit Constraints (= and ×)

Keep V1's simple and effective propagation, just add = and × constraints
"""

from typing import List, Optional, Tuple
import copy
import time


class Constraint:
    """Constraint between two cells"""
    def __init__(self, cell1: Tuple[int, int], cell2: Tuple[int, int], constraint_type: str):
        self.cell1 = cell1
        self.cell2 = cell2
        self.type = constraint_type


class TangoGridSimple:
    """Simple Tango grid with = and × constraints"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Optional[int]]] = [[None for _ in range(cols)] for _ in range(rows)]
        self.constraints: List[Constraint] = []

    def set_cell(self, row: int, col: int, value: Optional[int]):
        if value is not None and value not in [0, 1]:
            raise ValueError(f"Cell value must be None, 0, or 1")
        self.grid[row][col] = value

    def add_constraint(self, row1: int, col1: int, row2: int, col2: int, constraint_type: str):
        if constraint_type not in ["=", "×"]:
            raise ValueError(f"Constraint type must be '=' or '×'")
        self.constraints.append(Constraint((row1, col1), (row2, col2), constraint_type))

    def get_cell(self, row: int, col: int) -> Optional[int]:
        return self.grid[row][col]

    def is_complete(self) -> bool:
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    return False
        return True

    def __str__(self) -> str:
        result = []
        for row in self.grid:
            row_str = ' '.join(['.' if cell is None else str(cell) for cell in row])
            result.append(row_str)
        return '\n'.join(result)


class TangoSolverSimple:
    """Simple solver: V1 propagation + = and × constraints"""

    def __init__(self, grid: TangoGridSimple):
        self.grid = grid
        self.changes_made = False

    def solve(self, max_iterations: int = 100) -> Tuple[bool, int, float]:
        """Solve using simple iterative constraint propagation"""
        start_time = time.time()
        iteration = 0

        while not self.grid.is_complete() and iteration < max_iterations:
            self.changes_made = False

            # Apply explicit = and × constraints FIRST
            self._apply_explicit_constraints()

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

        elapsed_time = (time.time() - start_time) * 1000
        return self.grid.is_complete(), iteration, elapsed_time

    def _apply_explicit_constraints(self):
        """Apply = and × constraints"""
        for constraint in self.grid.constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2
            val1 = self.grid.get_cell(r1, c1)
            val2 = self.grid.get_cell(r2, c2)

            if constraint.type == "=":  # Must be equal
                if val1 is not None and val2 is None:
                    self._set_cell_safe(r2, c2, val1)
                elif val2 is not None and val1 is None:
                    self._set_cell_safe(r1, c1, val2)

            elif constraint.type == "×":  # Must be different
                if val1 is not None and val2 is None:
                    opposite = 1 - val1
                    self._set_cell_safe(r2, c2, opposite)
                elif val2 is not None and val1 is None:
                    opposite = 1 - val2
                    self._set_cell_safe(r1, c1, opposite)

    def _get_line(self, index: int, is_row: bool) -> List[Optional[int]]:
        """Get a row or column as a list"""
        if is_row:
            return self.grid.grid[index]
        else:
            return [self.grid.grid[row][index] for row in range(self.grid.rows)]

    def _set_cell_safe(self, row: int, col: int, value: int):
        """Set a cell value if it's currently empty and doesn't violate constraints"""
        if self.grid.get_cell(row, col) is None:
            # Basic validation before setting
            if self._is_valid_assignment(row, col, value):
                self.grid.set_cell(row, col, value)
                self.changes_made = True

    def _is_valid_assignment(self, row: int, col: int, value: int) -> bool:
        """Check if assignment would violate explicit constraints or three consecutive rule"""
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

        # Temporarily set the value to check three consecutive
        old_val = self.grid.get_cell(row, col)
        self.grid.set_cell(row, col, value)

        # Check three consecutive in row
        valid = True
        for c in range(max(0, col - 2), min(self.grid.cols - 2, col + 1)):
            vals = [self.grid.get_cell(row, c),
                   self.grid.get_cell(row, c+1),
                   self.grid.get_cell(row, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                valid = False
                break

        # Check three consecutive in column
        if valid:
            for r in range(max(0, row - 2), min(self.grid.rows - 2, row + 1)):
                vals = [self.grid.get_cell(r, col),
                       self.grid.get_cell(r+1, col),
                       self.grid.get_cell(r+2, col)]
                if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                    valid = False
                    break

        # Check balance constraints
        if valid:
            # Check row balance
            row_vals = [self.grid.get_cell(row, c) for c in range(self.grid.cols)]
            count_0 = sum(1 for x in row_vals if x == 0)
            count_1 = sum(1 for x in row_vals if x == 1)
            if count_0 > 5 or count_1 > 5:
                valid = False

        if valid:
            # Check column balance
            col_vals = [self.grid.get_cell(r, col) for r in range(self.grid.rows)]
            count_0 = sum(1 for x in col_vals if x == 0)
            count_1 = sum(1 for x in col_vals if x == 1)
            if count_0 > 5 or count_1 > 5:
                valid = False

        # Restore
        self.grid.set_cell(row, col, old_val)

        return valid

    def _process_line(self, index: int, is_row: bool):
        """Process a single row or column applying constraint rules (V1 style)"""
        line = self._get_line(index, is_row)
        length = len(line)

        # Rule 0: Balance constraint - equal number of 0s and 1s
        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)
        count_empty = sum(1 for cell in line if cell is None)

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

        # Rule 1: Sandwich rule - If n-1 = n+1, then n ≠ n+1
        for i in range(1, length - 1):
            prev = line[i-1]
            next_val = line[i+1]
            current = line[i]

            if prev is not None and next_val is not None and prev == next_val and current is None:
                opposite = 1 - prev
                self._set_cell_in_line(index, i, opposite, is_row)

        # Rule 2: Consecutive pair rule - If n = n+1, then n-1 = n+2 ≠ n
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
                opposite = 1 - vals[0]
                self._set_cell_in_line(index, i+2, opposite, is_row)
            if vals[1] is not None and vals[2] is not None and vals[1] == vals[2] and vals[0] is None:
                opposite = 1 - vals[1]
                self._set_cell_in_line(index, i, opposite, is_row)
            if vals[0] is not None and vals[2] is not None and vals[0] == vals[2] and vals[1] is None:
                opposite = 1 - vals[0]
                self._set_cell_in_line(index, i+1, opposite, is_row)

    def _set_cell_in_line(self, line_index: int, position: int, value: int, is_row: bool):
        """Set a cell value in a specific line"""
        if is_row:
            self._set_cell_safe(line_index, position, value)
        else:
            self._set_cell_safe(position, line_index, value)


def create_10x10_simple() -> TangoGridSimple:
    """10x10 puzzle with all constraints for simple solver"""
    grid = TangoGridSimple(10, 10)

    # Initial values (same as before)
    grid.set_cell(1, 1, 0)
    grid.set_cell(2, 0, 1)
    grid.set_cell(2, 4, 1)
    grid.set_cell(2, 9, 0)
    grid.set_cell(3, 8, 1)
    grid.set_cell(4, 2, 0)
    grid.set_cell(4, 7, 0)
    grid.set_cell(5, 1, 0)
    grid.set_cell(5, 6, 0)
    grid.set_cell(7, 2, 1)
    grid.set_cell(7, 4, 1)
    grid.set_cell(7, 9, 1)
    grid.set_cell(8, 0, 0)
    grid.set_cell(9, 5, 0)
    grid.set_cell(9, 6, 1)
    grid.set_cell(9, 9, 1)

    # All constraints
    grid.add_constraint(0, 8, 0, 9, "=")
    grid.add_constraint(1, 1, 1, 2, "×")
    grid.add_constraint(2, 0, 2, 1, "×")
    grid.add_constraint(2, 7, 2, 8, "=")
    grid.add_constraint(2, 5, 2, 6, "=")
    grid.add_constraint(3, 0, 3, 1, "×")
    grid.add_constraint(3, 5, 3, 6, "×")
    grid.add_constraint(3, 8, 3, 9, "×")
    grid.add_constraint(5, 0, 5, 1, "=")
    grid.add_constraint(5, 2, 5, 3, "×")
    grid.add_constraint(5, 6, 5, 7, "×")
    grid.add_constraint(5, 8, 5, 9, "=")
    grid.add_constraint(6, 7, 6, 8, "×")
    grid.add_constraint(6, 8, 6, 9, "=")
    grid.add_constraint(7, 7, 7, 8, "=")
    grid.add_constraint(8, 1, 8, 2, "×")
    grid.add_constraint(8, 2, 8, 3, "×")
    grid.add_constraint(8, 3, 8, 4, "×")
    grid.add_constraint(9, 3, 9, 4, "=")
    grid.add_constraint(9, 7, 9, 8, "=")
    grid.add_constraint(4, 0, 5, 0, "=")
    grid.add_constraint(5, 0, 6, 0, "=")
    grid.add_constraint(6, 6, 7, 6, "=")
    grid.add_constraint(5, 9, 6, 9, "=")

    return grid


def main():
    print("=" * 70)
    print("SIMPLE TANGO SOLVER (V1 + = and × constraints)")
    print("=" * 70)
    print()

    grid = create_10x10_simple()

    initial_count = sum(1 for r in range(10) for c in range(10) if grid.get_cell(r, c) is not None)
    print(f"Initial: {initial_count}/100 cells")
    print(f"Constraints: {len(grid.constraints)} (= and ×)")
    print()

    print("Initial grid:")
    print(grid)
    print()

    solver = TangoSolverSimple(grid)
    solved, iterations, time_ms = solver.solve()

    print("=" * 70)
    print("SOLUTION")
    print("=" * 70)
    print(grid)
    print()

    filled = sum(1 for r in range(10) for c in range(10) if grid.get_cell(r, c) is not None)
    print(f"✓ Solved: {solved}")
    print(f"📊 Filled: {filled}/100 ({filled}%)")
    print(f"🔄 Iterations: {iterations}")
    print(f"⏱️  Time: {time_ms:.4f} ms")
    print()

    if filled > initial_count:
        print(f"Progress: +{filled - initial_count} cells solved")


if __name__ == "__main__":
    main()
