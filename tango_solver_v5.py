#!/usr/bin/env python3
"""
Tango Solver V5 - Enhanced constraint propagation

New logic improvements:
1. Advanced counting rule: if missing_0 == 0, fill all empty with 1 (and vice versa)
2. Immediate constraint propagation: propagate = and × after each change
3. Implicit constraints: = between n and n+1 implies × between n-1 and n, and between n+1 and n+2
4. Keep existing rules: sandwich, two consecutive
"""

import time
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Constraint:
    """Represents a constraint between two cells"""
    cell1: Tuple[int, int]  # (row, col)
    cell2: Tuple[int, int]  # (row, col)
    type: str  # "=" or "×"


class TangoGridV5:
    """Grid with explicit constraints"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.constraints = []  # List of Constraint objects

    def get_cell(self, row: int, col: int) -> Optional[int]:
        """Get cell value"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def set_cell(self, row: int, col: int, value: int):
        """Set cell value"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = value

    def add_constraint(self, r1: int, c1: int, r2: int, c2: int, constraint_type: str):
        """Add a constraint between two cells"""
        constraint = Constraint(
            cell1=(r1, c1),
            cell2=(r2, c2),
            type=constraint_type
        )
        self.constraints.append(constraint)

    def is_complete(self) -> bool:
        """Check if grid is completely filled"""
        for row in self.grid:
            if None in row:
                return False
        return True

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates"""
        empty = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    empty.append((r, c))
        return empty


class TangoSolverV5:
    """
    Enhanced Tango solver with improved constraint propagation
    """

    def __init__(self, grid: TangoGridV5):
        self.grid = grid
        self.changes_made = False
        self.implicit_constraints = []  # Store implicit constraints from = rules

        # Generate implicit constraints at initialization
        self._generate_implicit_constraints()

    def _generate_implicit_constraints(self):
        """
        Generate implicit × constraints from = constraints

        Rule: If (n) = (n+1), then:
        - (n-1) × (n) - to avoid three consecutive
        - (n+1) × (n+2) - to avoid three consecutive
        """
        for constraint in self.grid.constraints:
            if constraint.type != "=":
                continue

            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2

            # Check if constraint is horizontal (same row)
            if r1 == r2:
                row = r1
                # Constraint is between (row, c1) and (row, c2)
                # Assume c2 = c1 + 1 for adjacent cells

                # Add implicit × between (row, c1-1) and (row, c1)
                if c1 > 0:
                    implicit = Constraint(
                        cell1=(row, c1-1),
                        cell2=(row, c1),
                        type="×"
                    )
                    self.implicit_constraints.append(implicit)

                # Add implicit × between (row, c2) and (row, c2+1)
                if c2 < self.grid.cols - 1:
                    implicit = Constraint(
                        cell1=(row, c2),
                        cell2=(row, c2+1),
                        type="×"
                    )
                    self.implicit_constraints.append(implicit)

            # Check if constraint is vertical (same column)
            elif c1 == c2:
                col = c1
                # Constraint is between (r1, col) and (r2, col)
                # Assume r2 = r1 + 1 for adjacent cells

                # Add implicit × between (r1-1, col) and (r1, col)
                if r1 > 0:
                    implicit = Constraint(
                        cell1=(r1-1, col),
                        cell2=(r1, col),
                        type="×"
                    )
                    self.implicit_constraints.append(implicit)

                # Add implicit × between (r2, col) and (r2+1, col)
                if r2 < self.grid.rows - 1:
                    implicit = Constraint(
                        cell1=(r2, col),
                        cell2=(r2+1, col),
                        type="×"
                    )
                    self.implicit_constraints.append(implicit)

    def solve(self, max_iterations: int = 100) -> Tuple[bool, int, float]:
        """
        Solve the puzzle using enhanced constraint propagation

        Returns:
            (is_solved, iterations, elapsed_time_ms)
        """
        start_time = time.time()
        iteration = 0

        while not self.grid.is_complete() and iteration < max_iterations:
            self.changes_made = False

            # Apply explicit and implicit constraints
            self._apply_all_constraints()

            # Apply advanced counting rule
            self._apply_counting_rule()

            # Process rows with traditional rules
            for row in range(self.grid.rows):
                self._process_line(row, is_row=True)

            # Process columns with traditional rules
            for col in range(self.grid.cols):
                self._process_line(col, is_row=False)

            if not self.changes_made:
                break

            iteration += 1

        elapsed_time = (time.time() - start_time) * 1000
        return self.grid.is_complete(), iteration, elapsed_time

    def _apply_all_constraints(self):
        """
        Apply all explicit and implicit constraints

        For = constraints: if one cell has a value, copy to the other
        For × constraints: if one cell has a value, set other to opposite
        """
        # Combine explicit and implicit constraints
        all_constraints = self.grid.constraints + self.implicit_constraints

        for constraint in all_constraints:
            r1, c1 = constraint.cell1
            r2, c2 = constraint.cell2
            val1 = self.grid.get_cell(r1, c1)
            val2 = self.grid.get_cell(r2, c2)

            if constraint.type == "=":
                # Equal constraint
                if val1 is not None and val2 is None:
                    self._set_cell_safe(r2, c2, val1)
                elif val2 is not None and val1 is None:
                    self._set_cell_safe(r1, c1, val2)

            elif constraint.type == "×":
                # Different constraint
                if val1 is not None and val2 is None:
                    opposite = 1 - val1
                    self._set_cell_safe(r2, c2, opposite)
                elif val2 is not None and val1 is None:
                    opposite = 1 - val2
                    self._set_cell_safe(r1, c1, opposite)

    def _apply_counting_rule(self):
        """
        Advanced counting rule:
        - Count zeros and ones in each line
        - If missing_0 == 0, fill all empty with 1
        - If missing_1 == 0, fill all empty with 0
        """
        # For rows
        for row in range(self.grid.rows):
            self._apply_counting_for_line(row, is_row=True)

        # For columns
        for col in range(self.grid.cols):
            self._apply_counting_for_line(col, is_row=False)

    def _apply_counting_for_line(self, index: int, is_row: bool):
        """Apply counting rule for a specific line"""
        line = self._get_line(index, is_row)
        length = len(line)
        target = length // 2

        # Count values
        count_zeros = sum(1 for cell in line if cell == 0)
        count_ones = sum(1 for cell in line if cell == 1)
        count_empty = sum(1 for cell in line if cell is None)

        # Calculate missing
        missing_zeros = target - count_zeros
        missing_ones = target - count_ones

        # If missing_0 == 0, fill all empty with 1
        if missing_zeros == 0 and count_empty > 0:
            for i in range(length):
                if line[i] is None:
                    self._set_cell_in_line(index, i, 1, is_row)

        # If missing_1 == 0, fill all empty with 0
        elif missing_ones == 0 and count_empty > 0:
            for i in range(length):
                if line[i] is None:
                    self._set_cell_in_line(index, i, 0, is_row)

    def _process_line(self, index: int, is_row: bool):
        """Process a line with traditional constraint rules"""
        line = self._get_line(index, is_row)
        length = len(line)

        # Rule 1: Sandwich - If n-1 = n+1, then n ≠ n+1
        for i in range(1, length - 1):
            prev = line[i-1]
            next_val = line[i+1]
            current = line[i]

            if prev is not None and next_val is not None and prev == next_val and current is None:
                opposite = 1 - prev
                self._set_cell_in_line(index, i, opposite, is_row)

        # Refresh line
        line = self._get_line(index, is_row)

        # Rule 2: Two consecutive - If n = n+1, then n-1 ≠ n and n+2 ≠ n+1
        for i in range(length - 1):
            current = line[i]
            next_val = line[i+1]

            if current is not None and next_val is not None and current == next_val:
                opposite = 1 - current

                # Set n-1
                if i > 0 and line[i-1] is None:
                    self._set_cell_in_line(index, i-1, opposite, is_row)

                # Set n+2
                if i+2 < length and line[i+2] is None:
                    self._set_cell_in_line(index, i+2, opposite, is_row)

    def _get_line(self, index: int, is_row: bool) -> List[Optional[int]]:
        """Get a row or column as a list"""
        if is_row:
            return self.grid.grid[index]
        else:
            return [self.grid.grid[row][index] for row in range(self.grid.rows)]

    def _set_cell_in_line(self, index: int, pos: int, value: int, is_row: bool):
        """Set a cell value in a line"""
        if is_row:
            self._set_cell_safe(index, pos, value)
        else:
            self._set_cell_safe(pos, index, value)

    def _set_cell_safe(self, row: int, col: int, value: int):
        """Set a cell value if it's currently empty and valid"""
        if self.grid.get_cell(row, col) is None:
            if self._is_valid_assignment(row, col, value):
                self.grid.set_cell(row, col, value)
                self.changes_made = True

    def _is_valid_assignment(self, row: int, col: int, value: int) -> bool:
        """Check if assignment is valid (doesn't violate constraints)"""
        # Check explicit constraints
        all_constraints = self.grid.constraints + self.implicit_constraints

        for constraint in all_constraints:
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

        # Check three consecutive
        old_val = self.grid.get_cell(row, col)
        self.grid.set_cell(row, col, value)

        valid = True

        # Check in row
        for c in range(max(0, col - 2), min(self.grid.cols - 2, col + 1)):
            vals = [self.grid.get_cell(row, c),
                   self.grid.get_cell(row, c+1),
                   self.grid.get_cell(row, c+2)]
            if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                valid = False
                break

        # Check in column
        if valid:
            for r in range(max(0, row - 2), min(self.grid.rows - 2, row + 1)):
                vals = [self.grid.get_cell(r, col),
                       self.grid.get_cell(r+1, col),
                       self.grid.get_cell(r+2, col)]
                if all(v is not None for v in vals) and vals[0] == vals[1] == vals[2]:
                    valid = False
                    break

        # Check balance
        if valid:
            max_count = self.grid.cols // 2
            row_vals = [self.grid.get_cell(row, c) for c in range(self.grid.cols)]
            count_0 = sum(1 for x in row_vals if x == 0)
            count_1 = sum(1 for x in row_vals if x == 1)
            if count_0 > max_count or count_1 > max_count:
                valid = False

        if valid:
            max_count = self.grid.rows // 2
            col_vals = [self.grid.get_cell(r, col) for r in range(self.grid.rows)]
            count_0 = sum(1 for x in col_vals if x == 0)
            count_1 = sum(1 for x in col_vals if x == 1)
            if count_0 > max_count or count_1 > max_count:
                valid = False

        # Restore
        self.grid.set_cell(row, col, old_val)

        return valid


def main():
    """Test V5 solver"""
    # Create a simple 6×6 test
    grid = TangoGridV5(6, 6)

    # Add some initial values
    grid.set_cell(0, 0, 1)
    grid.set_cell(0, 1, 0)

    # Add a = constraint
    grid.add_constraint(2, 2, 2, 3, "=")

    # Add a × constraint
    grid.add_constraint(1, 1, 1, 2, "×")

    print("=" * 70)
    print("TANGO SOLVER V5 - Enhanced Constraint Propagation")
    print("=" * 70)
    print()

    solver = TangoSolverV5(grid)

    print(f"Explicit constraints: {len(grid.constraints)}")
    print(f"Implicit constraints: {len(solver.implicit_constraints)}")
    print()

    solved, iterations, time_ms = solver.solve()

    print(f"Solved: {solved}")
    print(f"Iterations: {iterations}")
    print(f"Time: {time_ms:.4f} ms")


if __name__ == "__main__":
    main()
