#!/usr/bin/env python3
"""
Test de déduction logique avancée

Implémente la logique décrite par l'utilisateur:
1. Contrainte × → propagation immédiate
2. Balance → si on a N zéros, remplir reste avec des 1
3. Propagation en chaîne
"""

from tango_solver_v5 import TangoGridV5, TangoSolverV5


def test_advanced_deduction():
    """Test avec un cas où la déduction en chaîne est nécessaire"""
    grid = TangoGridV5(8, 8)

    # Exemple simplifié de la logique décrite
    # Supposons row 0, et on a déjà 4 zéros
    # Target = 4, donc si count_zeros = 4, on remplit avec des 1

    print("Test de déduction logique avancée")
    print("=" * 70)
    print()

    # Simulons: row 5, col 3 a une contrainte × avec row 5, col 4
    # Et row 5, col 4 = 1
    grid.add_constraint(5, 3, 5, 4, "×")
    grid.set_cell(5, 4, 1)

    # Donc row 5, col 3 doit être 0
    # Et si on a déjà beaucoup de 0 dans la colonne 3...
    # On peut déduire les cellules au-dessus

    solver = TangoSolverV5(grid)

    print("Grille initiale:")
    for r in range(grid.rows):
        row_str = ' '.join(['.' if grid.get_cell(r, c) is None
                           else str(grid.get_cell(r, c))
                           for c in range(grid.cols)])
        print(f"  {row_str}")

    print()
    print("Résolution...")
    solved, iterations, time_ms = solver.solve()

    print("\nGrille après résolution:")
    for r in range(grid.rows):
        row_str = ' '.join(['.' if grid.get_cell(r, c) is None
                           else str(grid.get_cell(r, c))
                           for c in range(grid.cols)])
        print(f"  {row_str}")

    print()
    print(f"Itérations: {iterations}")
    print(f"Temps: {time_ms:.2f}ms")


if __name__ == "__main__":
    test_advanced_deduction()
