# Tango Puzzle Solver 🎯

A comprehensive Python solver for Tango binary logic puzzles with automatic image recognition (OCR).

## ✨ Features

- **Advanced Solver (V5)**: 97% completion rate with zero violations
- **OCR Recognition**: Automatically reads puzzles from screenshots
- **Multiple Solving Strategies**: Constraint propagation + implicit constraint generation
- **Fast Execution**: Solves puzzles in <1ms
- **Zero Dependencies** for core solver (OpenCV optional for OCR)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repo-url>
cd Tango_solver

# Install OCR dependencies (optional, for image recognition)
pip install -r requirements.txt
```

### 2. Solve from Image (Recommended)

```bash
python solve_from_image.py your_puzzle.png
```

### 3. Manual Solving

```python
from tango_solver_v5 import TangoGridV5, TangoSolverV5

# Create grid
grid = TangoGridV5(6, 6)

# Set initial values
grid.set_cell(1, 4, 1)  # Row 1, Col 4 = 1
grid.set_cell(2, 0, 1)  # Row 2, Col 0 = 1

# Add constraints
grid.add_constraint(1, 0, 1, 1, "×")  # Different
grid.add_constraint(3, 0, 3, 1, "=")  # Equal

# Solve
solver = TangoSolverV5(grid)
solved, iterations, time_ms = solver.solve()

print(f"Solved: {solved} in {iterations} iterations ({time_ms:.2f}ms)")
```

## 📁 Project Structure

```
Tango_solver/
├── tango_solver_v5.py      # 🌟 MAIN SOLVER (use this!)
├── tango_ocr.py             # OCR image recognition
├── solve_from_image.py      # Automatic solver from images
├── requirements.txt         # Dependencies for OCR
├── README.md               # This file
│
├── examples/               # Example puzzles
│   ├── puzzle_6x6_v5.py
│   └── puzzle_10x10_v*.py
│
├── tools/                  # Analysis & benchmarking tools
│   ├── benchmark.py
│   ├── compare_all_solvers.py
│   └── verify_*.py
│
├── legacy/                 # Old solver versions (V1-V4)
│   └── README.md          # Info about legacy solvers
│
└── docs/                   # Documentation
    └── OCR_GUIDE.md       # OCR usage guide
```

## 🎮 About Tango Puzzles

Tango is a binary logic puzzle where you fill a grid with 0s and 1s following specific rules:

### Core Rules

1. **Balance**: Each row/column must have equal 0s and 1s
2. **No Three Consecutive**: No three 0s or 1s in a row/column
3. **Sandwich Rule**: If `A _ A`, middle must be opposite of A
4. **Consecutive Pair**: If `AA`, neighbors must be different

### Special Constraints

- **= Symbol**: Adjacent cells must be equal
- **× Symbol**: Adjacent cells must be different

## 🧠 Solver V5 Algorithm

The V5 solver uses advanced constraint propagation:

### 1. **Advanced Counting Rule**
```python
# If a line already has 3 zeros (in 6×6 grid)
# Fill all remaining cells with 1s
if missing_zeros == 0:
    fill_all_empty_with(1)
```

### 2. **Immediate Constraint Propagation**
```python
# If cell A = cell B, and A has value 1
# Immediately set B = 1
propagate_through_constraints()
```

### 3. **Implicit Constraint Generation**
```python
# If cells n and n+1 have = constraint
# Auto-create × constraints:
#   - between n-1 and n
#   - between n+1 and n+2
# This prevents three consecutive!
```

### 4. **Traditional Rules**
- Sandwich detection
- Consecutive pair handling
- Three consecutive prevention

## 📊 Performance Comparison

| Solver | Completion | Violations | Speed |
|--------|-----------|------------|-------|
| **V5** | **97%** ✅ | **0** ✅ | 0.67ms |
| V4 | 35% | 1 ❌ | 7.08ms |
| V3 | 86% | 7 ❌ | 9.76ms |
| Simple | 34% | 0 ✅ | 0.74ms |

*Tested on 6×6 DIFFICILE puzzle with 10/36 initial cells*

## 🖼️ OCR Usage

See [docs/OCR_GUIDE.md](docs/OCR_GUIDE.md) for detailed OCR instructions.

```bash
# Quick OCR test
python solve_from_image.py puzzle.png --debug
```

**OCR Features:**
- ✅ Auto grid size detection
- ✅ Color-based symbol recognition (🟠 = 1, 🌙 = 0)
- 🔨 Constraint detection (= and ×) - in development

## 🛠️ Development Tools

### Benchmarking
```bash
cd tools
python benchmark.py
```

### Solver Comparison
```bash
cd tools
python compare_all_solvers.py
```

### Solution Validation
```bash
cd tools
python verify_6x6_difficile.py
```

## 📚 Examples

Check the `examples/` folder for:
- **puzzle_6x6_v5.py**: 6×6 DIFFICILE puzzle
- **puzzle_10x10_v4.py**: 10×10 puzzle with constraints

Run any example:
```bash
python examples/puzzle_6x6_v5.py
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Template matching for = and × constraint detection
- Support for non-square grids
- Web interface
- More solving strategies

## 📄 License

MIT License

## 👤 Author

Created as part of the Tango puzzle solver project.

---

**Recommended**: Start with `solve_from_image.py` for the easiest experience!
