#!/usr/bin/env python3
"""
Test manuel d'un puzzle 8×8 avec TOUTES les contraintes
Extraction depuis l'image de solution fournie
"""

from tango_solver_v5 import TangoGridV5, TangoSolverV5, Constraint
import time

# Créer la grille 8×8
grid = TangoGridV5(8, 8)

print("=" * 70)
print("TEST: Puzzle 8×8 avec TOUTES les contraintes")
print("=" * 70)

# Valeurs initiales - TOUTES extraites de l'image solution
# Ligne 0: 0 1 1 0 1 0 0 1
# Ligne 1: 0 1 0 1 0 1 0 1
# Ligne 2: 1 0 1 0 1 0 1 0
# Ligne 3: 1 1 0 0 1 1 0 0
# Ligne 4: 0 0 1 1 0 0 1 1
# Ligne 5: 0 1 1 0 1 1 0 0
# Ligne 6: 1 0 0 1 0 0 1 1
# Ligne 7: 1 0 0 1 0 0 1 1

# Pour le test, on garde seulement les valeurs initiales (symboles visibles au départ)
initial_values = [
    # Row 0
    (0, 1, 1), (0, 4, 1), (0, 7, 1),
    # Row 1
    (1, 1, 1), (1, 3, 1), (1, 5, 1), (1, 7, 1),
    # Row 2
    (2, 0, 1), (2, 2, 1), (2, 4, 1), (2, 6, 1),
    # Row 3
    (3, 0, 1), (3, 1, 1), (3, 4, 1), (3, 5, 1),
    # Row 4
    (4, 2, 1), (4, 3, 1), (4, 6, 1), (4, 7, 1),
    # Row 5
    (5, 1, 1), (5, 2, 1), (5, 4, 1), (5, 5, 1),
    # Row 6
    (6, 0, 1), (6, 3, 1), (6, 6, 1), (6, 7, 1),
    # Row 7
    (7, 0, 1), (7, 3, 1), (7, 6, 1), (7, 7, 1),
]

# Ajouter seulement quelques valeurs initiales (celles du puzzle non résolu)
initial_values_puzzle = [
    (0, 1, 1), (0, 6, 1),
    (1, 0, 0), (1, 1, 1), (1, 3, 1),
    (2, 6, 1),
    (3, 2, 0), (3, 7, 0),
    (4, 3, 1),
    (5, 6, 0),
    (7, 3, 1), (7, 6, 1),
]

for r, c, val in initial_values_puzzle:
    grid.set_cell(r, c, val)

# Contraintes extraites de l'image solution
# Je dois identifier toutes les contraintes = et × visibles
constraints = [
    # Row 0
    Constraint((0, 6), (0, 7), "="),

    # Row 3
    Constraint((3, 4), (3, 5), "×"),
    Constraint((3, 5), (3, 6), "="),

    # Row 5
    Constraint((5, 0), (5, 1), "="),
    Constraint((5, 4), (5, 5), "×"),

    # Row 6
    Constraint((6, 3), (6, 4), "×"),
    Constraint((6, 4), (6, 5), "×"),

    # Row 7
    Constraint((7, 1), (7, 2), "×"),

    # TODO: Il en manque probablement d'autres !
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

print(f"\nValeurs initiales: {len(initial_values_puzzle)}")
print(f"Contraintes: {len(constraints)}")
print(f"  - = (égalité): {sum(1 for c in constraints if c.type == '=')}")
print(f"  - × (opposé): {sum(1 for c in constraints if c.type == '×')}")

# Résoudre
print("\nRésolution avec V5...")
solver = TangoSolverV5(grid)

# Debug: voir les contraintes implicites générées
print(f"Contraintes implicites générées: {len(solver.implicit_constraints)}")
for ic in solver.implicit_constraints[:10]:
    print(f"  {ic.type} entre {ic.cell1} et {ic.cell2}")
if len(solver.implicit_constraints) > 10:
    print(f"  ... et {len(solver.implicit_constraints) - 10} autres")

solved, iterations, elapsed = solver.solve(max_iterations=100)

print("\nSolution:")
display_grid(grid)

# Statistiques
total_cells = 8 * 8
filled_cells = sum(1 for r in range(8) for c in range(8) if grid.get_cell(r, c) is not None)
completion = (filled_cells / total_cells) * 100

print("\n" + "=" * 70)
print("RÉSULTATS")
print("=" * 70)
print(f"✓ Résolu: {solved}")
print(f"📊 Rempli: {filled_cells}/{total_cells} ({completion:.1f}%)")
print(f"🔄 Itérations: {iterations}")
print(f"⏱️  Temps: {elapsed:.4f} ms")

if not solved:
    print("\n⚠️  Il manque encore des contraintes pour compléter le puzzle!")
    print("   Aide-moi à identifier toutes les contraintes = et × de l'image.")
