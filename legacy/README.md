# Legacy Solvers

This folder contains previous versions of the Tango solver, kept for reference and historical purposes.

## Files

### Solvers (old versions)
- **tango_solver.py** - V1: Basic constraint propagation
- **tango_solver_v2.py** - V2: V1 + backtracking with MRV heuristic
- **tango_solver_v3.py** - V3: V2 + explicit = and × constraints (has bugs)
- **tango_solver_v4.py** - V4: V3 + strict validation (too conservative)
- **tango_solver_simple.py** - Simple: V1 + constraints with validation

## Why are these here?

These versions were part of the development process but have been superseded by **V5** (available in the root directory).

## Current Recommendation

**Use `tango_solver_v5.py`** from the root directory - it's the best solver with:
- ✅ 97% completion rate on difficult puzzles
- ✅ 0 violations
- ✅ Implicit constraint generation
- ✅ Advanced counting rules
- ✅ Fast execution (~0.7ms)

## Issues with older versions

- **V3**: Produces invalid solutions with constraint violations
- **V4**: Too conservative, only reaches ~35% completion
- **Simple**: Similar to V4, conservative approach
- **V1-V2**: Don't support explicit = and × constraints

## Do not delete

These files are kept for:
1. Reference and learning
2. Comparison with new implementations
3. Historical tracking of the solver evolution
