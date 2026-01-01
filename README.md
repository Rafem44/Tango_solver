# Tango Puzzle Solver

A Python-based solver for Tango puzzles using constraint propagation algorithms.

## About Tango Puzzles

Tango is a binary puzzle game where you fill a grid with 0s and 1s following specific constraint rules.

### Game Rules

1. **Grid**: The puzzle consists of a grid (I×S) that needs to be filled with 0s and 1s
2. **Cell States**: Each cell can be in one of three states:
   - Empty (unknown)
   - 0
   - 1

### Constraint Rules

The solver implements the following constraint rules:

#### Rule 0: Balance Constraint
**Each row and column must have an equal number of 0s and 1s**

For a line of length L (where L is even):
- Number of 0s = L/2
- Number of 1s = L/2

```
Example (4-cell row): [0][0][?][?] → [0][0][1][1]
Example (6-cell row): [1][1][1][?][?][?] → [1][1][1][0][0][0]
```

This constraint is most effective with even-sized grids (4x4, 6x6, 8x8, etc.)

#### Rule 1: Sandwich Rule
**If n-1 = n+1, then n ≠ n+1**

When two neighboring cells have the same value, the cell between them must have the opposite value.

```
Example: [0][?][0] → [0][1][0]
         [1][?][1] → [1][0][1]
```

#### Rule 2: Consecutive Pair Rule
**If n = n+1, then n-1 = n+2 ≠ n**

When two consecutive cells have the same value:
- The cell before them equals the cell two positions after
- Both must be different from the consecutive pair

```
Example: [?][0][0][?] → [1][0][0][1]
         [?][1][1][?] → [0][1][1][0]
```

#### Rule 3: No Three Consecutive
No three consecutive cells can have the same value.

```
Invalid: [0][0][0], [1][1][1]
Valid:   [0][1][0], [1][0][1]
```

## Algorithm

The solver uses constraint propagation:

1. **Process line by line** (rows): Apply all constraint rules to each row
2. **Process column by column**: Apply all constraint rules to each column
3. **Iterate**: Repeat until no more changes can be made or the puzzle is solved

## Usage

### Running the Solver

```bash
python3 tango_solver.py
```

### Using in Your Code

```python
from tango_solver import TangoGrid, TangoSolver

# Create a 5x5 grid
grid = TangoGrid(5, 5)

# Set initial values
grid.set_cell(0, 0, 0)
grid.set_cell(0, 1, 1)
grid.set_cell(0, 2, 0)

# Solve the puzzle
solver = TangoSolver(grid)
is_solved = solver.solve()

# Display the result
print(grid)
print(f"Solved: {is_solved}")
```

## Example Output

```
=== Tango Puzzle Solver ===

Example 1: Grid from image (5x5)
Initial grid:
0 1 0 0 .
. . . . .
. . . . .
. . . . .
. . . . .

After applying constraints:
0 1 0 0 1
. . . . .
. . . . .
. . . . .
. . . . .

========================================

Example 2: 4x4 puzzle with balance constraint
Initial grid:
0 0 . .
1 . 0 .
. 1 . .
. . 1 .

After applying constraints:
0 0 1 1
1 . 0 .
. 1 0 .
. . 1 .
```

## Class Reference

### TangoGrid

Represents a Tango puzzle grid.

**Methods:**
- `__init__(rows, cols)`: Create a new grid
- `set_cell(row, col, value)`: Set a cell value (None, 0, or 1)
- `get_cell(row, col)`: Get a cell value
- `is_complete()`: Check if all cells are filled
- `copy()`: Create a deep copy of the grid

### TangoSolver

Solves Tango puzzles using constraint propagation.

**Methods:**
- `__init__(grid)`: Initialize solver with a grid
- `solve(max_iterations)`: Solve the puzzle (returns True if solved)

## Requirements

- Python 3.6 or higher
- No external dependencies

## License

MIT License

## Author

Created based on the Tango puzzle algorithm specification.
