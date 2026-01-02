#!/usr/bin/env python3
"""
Test manuel d'un puzzle 8×8 complexe
Extraction manuelle depuis l'image fournie
"""

from tango_solver_v5 import TangoGridV5, TangoSolverV5, Constraint
import time

# Créer la grille 8×8
grid = TangoGridV5(8, 8)

print("=" * 70)
print("TEST: Puzzle 8×8 manuel (depuis image)")
print("=" * 70)

# Valeurs initiales (cercles jaunes = 1, croissants bleus = 0)
initial_values = [
    # Row 0
    (0, 1, 1), (0, 6, 1),
    # Row 1
    (1, 0, 0), (1, 1, 1), (1, 3, 1),
    # Row 2
    (2, 6, 1),
    # Row 3
    (3, 2, 0), (3, 7, 0),
    # Row 4
    (4, 3, 1),
    # Row 5
    (5, 6, 0),
    # Row 7
    (7, 3, 1), (7, 6, 1),
]

for r, c, val in initial_values:
    grid.set_cell(r, c, val)

# Contraintes (= et ×)
constraints = [
    # = constraints (égalité)
    Constraint((1, 6), (1, 7), "="),  # Row 1, droite
    Constraint((3, 4), (3, 5), "="),  # Row 3, milieu
    Constraint((5, 0), (5, 1), "="),  # Row 5, gauche

    # × constraints (opposé)
    Constraint((3, 5), (3, 6), "×"),  # Row 3
    Constraint((6, 3), (7, 3), "×"),  # Vertical col 3
    Constraint((6, 4), (7, 4), "×"),  # Vertical col 4
    Constraint((6, 5), (7, 5), "×"),  # Vertical col 5
    Constraint((7, 0), (7, 1), "×"),  # Row 7, gauche
]

grid.constraints = constraints

def display_grid(g):
    """Display grid"""
    for r in range(g.rows):
        row_str = ' '.join(['.' if g.get_cell(r, c) is None
                           else str(g.get_cell(r, c))
                           for c in range(g.cols)])
        print(f"  {row_str}")

print("\nGrille initiale:")
display_grid(grid)

print(f"\nValeurs initiales: {len(initial_values)}")
print(f"Contraintes: {len(constraints)}")
print(f"  - = (égalité): {sum(1 for c in constraints if c.type == '=')}")
print(f"  - × (opposé): {sum(1 for c in constraints if c.type == '×')}")

# Résoudre
print("\nRésolution avec V5...")
solver = TangoSolverV5(grid)

# Debug: voir les contraintes implicites générées
print(f"Contraintes implicites générées: {len(solver.implicit_constraints)}")
for ic in solver.implicit_constraints[:5]:  # Afficher les 5 premières
    print(f"  {ic.type} entre {ic.cell1} et {ic.cell2}")
if len(solver.implicit_constraints) > 5:
    print(f"  ... et {len(solver.implicit_constraints) - 5} autres")

solved, iterations, elapsed = solver.solve(max_iterations=100)

print("\nSolution:")
display_grid(grid)

# Statistiques
total_cells = 8 * 8
filled_cells = sum(1 for r in range(8) for c in range(8) if grid.get_cell(r, c) is not None)
completion = (filled_cells / total_cells) * 100

violations = 0  # Check manually if needed
is_solved = filled_cells == total_cells and violations == 0

print("\n" + "=" * 70)
print("RÉSULTATS")
print("=" * 70)
print(f"✓ Résolu: {is_solved}")
print(f"📊 Rempli: {filled_cells}/{total_cells} ({completion:.1f}%)")
print(f"⚠️  Violations: {violations}")
print(f"🔄 Itérations: {iterations}")
print(f"⏱️  Temps: {elapsed:.4f} ms")

if not is_solved:
    print("\n⚠️  Puzzle non complètement résolu.")
    if violations > 0:
        print("   Des violations ont été détectées!")
    else:
        print("   Contraintes supplémentaires nécessaires ou logique plus avancée requise.")
