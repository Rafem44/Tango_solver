#!/usr/bin/env python3
"""
Tango GUI - Interface graphique pour résoudre les puzzles Tango

Workflow:
1. Charger une image
2. OCR détecte automatiquement la grille et les symboles
3. Utilisateur ajoute manuellement les contraintes = et ×
4. Cliquer sur "Résoudre" pour obtenir la solution
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Tuple
import os

try:
    from tango_ocr_v2 import TangoOCRV2
    from tango_solver_v5 import TangoGridV5, TangoSolverV5
except ImportError:
    print("Erreur: Modules non trouvés")
    print("Assurez-vous que tango_ocr_v2.py et tango_solver_v5.py sont présents")
    exit(1)


class TangoGUI:
    """Interface graphique pour Tango"""

    def __init__(self, root):
        self.root = root
        self.root.title("Tango Puzzle Solver")
        self.root.geometry("800x600")

        # Data
        self.grid_size = (0, 0)
        self.initial_values = []
        self.constraints = []
        self.grid = None
        self.image_path = None

        # Selected constraint type
        self.constraint_type = tk.StringVar(value="=")

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create user interface"""
        # Top frame - Controls
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Load image button
        ttk.Button(top_frame, text="📁 Charger Image",
                  command=self.load_image).pack(side=tk.LEFT, padx=5)

        # Constraint type selector
        ttk.Label(top_frame, text="Type de contrainte:").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(top_frame, text="= (égal)", variable=self.constraint_type,
                       value="=").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="× (différent)", variable=self.constraint_type,
                       value="×").pack(side=tk.LEFT, padx=5)

        # Solve button
        ttk.Button(top_frame, text="🚀 Résoudre",
                  command=self.solve_puzzle).pack(side=tk.RIGHT, padx=5)

        # Clear constraints button
        ttk.Button(top_frame, text="🗑️ Effacer contraintes",
                  command=self.clear_constraints).pack(side=tk.RIGHT, padx=5)

        # Main frame - Split view
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left panel - Initial grid
        left_panel = ttk.LabelFrame(main_frame, text="Grille initiale (OCR)", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.initial_canvas = tk.Canvas(left_panel, bg="white")
        self.initial_canvas.pack(fill=tk.BOTH, expand=True)
        self.initial_canvas.bind("<Button-1>", self.on_canvas_click)

        # Right panel - Solution
        right_panel = ttk.LabelFrame(main_frame, text="Solution", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.solution_canvas = tk.Canvas(right_panel, bg="white")
        self.solution_canvas.pack(fill=tk.BOTH, expand=True)

        # Bottom frame - Status
        self.status_bar = ttk.Label(self.root, text="Chargez une image pour commencer",
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_image(self):
        """Load and process image with OCR"""
        filename = filedialog.askopenfilename(
            title="Sélectionner une image de puzzle Tango",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Tous les fichiers", "*.*")]
        )

        if not filename:
            return

        self.image_path = filename
        self.status_bar.config(text=f"Chargement de {os.path.basename(filename)}...")
        self.root.update()

        try:
            # Run OCR
            ocr = TangoOCRV2(debug=False)
            result = ocr.read_puzzle(filename)

            self.grid_size = result['grid_size']
            self.initial_values = result['initial_values']
            # Don't use OCR constraints - user will add them
            self.constraints = []

            # Create grid
            rows, cols = self.grid_size
            self.grid = TangoGridV5(rows, cols)

            # Set initial values
            for row, col, value in self.initial_values:
                self.grid.set_cell(row, col, value)

            # Display
            self.draw_initial_grid()

            self.status_bar.config(
                text=f"✓ Grille {rows}×{cols} détectée avec {len(self.initial_values)} symboles. "
                     f"Ajoutez les contraintes et cliquez sur Résoudre."
            )

        except Exception as e:
            messagebox.showerror("Erreur OCR", f"Erreur lors de la lecture de l'image:\n{e}")
            self.status_bar.config(text="❌ Erreur lors du chargement")

    def draw_initial_grid(self):
        """Draw initial grid with detected values"""
        self.initial_canvas.delete("all")

        if not self.grid:
            return

        rows, cols = self.grid_size
        canvas_width = self.initial_canvas.winfo_width()
        canvas_height = self.initial_canvas.winfo_height()

        # Ensure minimum size
        if canvas_width < 100:
            canvas_width = 400
        if canvas_height < 100:
            canvas_height = 400

        cell_size = min((canvas_width - 40) // cols, (canvas_height - 40) // rows)
        offset_x = (canvas_width - cell_size * cols) // 2
        offset_y = (canvas_height - cell_size * rows) // 2

        # Draw grid
        for r in range(rows):
            for c in range(cols):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Draw cell
                self.initial_canvas.create_rectangle(x1, y1, x2, y2,
                                                    outline="black", fill="white")

                # Draw value
                value = self.grid.get_cell(r, c)
                if value is not None:
                    color = "orange" if value == 1 else "blue"
                    symbol = "●" if value == 1 else "◐"
                    self.initial_canvas.create_text(x1 + cell_size//2, y1 + cell_size//2,
                                                   text=symbol, font=("Arial", cell_size//2),
                                                   fill=color)

        # Draw constraints
        self._draw_constraints(self.initial_canvas, offset_x, offset_y, cell_size)

        # Store drawing params for click detection
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

    def _draw_constraints(self, canvas, offset_x, offset_y, cell_size):
        """Draw constraint symbols"""
        for (r1, c1), (r2, c2), ctype in self.constraints:
            # Calculate position between cells
            if r1 == r2:  # Horizontal constraint
                x = offset_x + c1 * cell_size + cell_size
                y = offset_y + r1 * cell_size + cell_size // 2
            else:  # Vertical constraint
                x = offset_x + c1 * cell_size + cell_size // 2
                y = offset_y + r1 * cell_size + cell_size

            canvas.create_text(x, y, text=ctype, font=("Arial", cell_size//3, "bold"),
                             fill="red")

    def on_canvas_click(self, event):
        """Handle canvas click to add constraints"""
        if not self.grid:
            return

        # Convert click position to grid position
        x = event.x - self.offset_x
        y = event.y - self.offset_y

        if x < 0 or y < 0:
            return

        # Determine if click is on a border (between cells)
        col_float = x / self.cell_size
        row_float = y / self.cell_size

        col = int(col_float)
        row = int(row_float)

        # Check if click is near a vertical border (between columns)
        col_remainder = col_float - col
        if 0.8 < col_remainder < 1.0 and col < self.grid_size[1] - 1:
            # Vertical border between col and col+1
            self.add_constraint(row, col, row, col + 1)
            return

        # Check if click is near a horizontal border (between rows)
        row_remainder = row_float - row
        if 0.8 < row_remainder < 1.0 and row < self.grid_size[0] - 1:
            # Horizontal border between row and row+1
            self.add_constraint(row, col, row + 1, col)
            return

    def add_constraint(self, r1, c1, r2, c2):
        """Add a constraint between two cells"""
        constraint = ((r1, c1), (r2, c2), self.constraint_type.get())

        # Check if constraint already exists
        for i, ((cr1, cc1), (cr2, cc2), _) in enumerate(self.constraints):
            if (cr1, cc1, cr2, cc2) == (r1, c1, r2, c2) or \
               (cr1, cc1, cr2, cc2) == (r2, c2, r1, c1):
                # Replace existing constraint
                self.constraints[i] = constraint
                self.draw_initial_grid()
                self.status_bar.config(text=f"Contrainte mise à jour: ({r1},{c1}) {self.constraint_type.get()} ({r2},{c2})")
                return

        # Add new constraint
        self.constraints.append(constraint)
        self.draw_initial_grid()
        self.status_bar.config(text=f"Contrainte ajoutée: ({r1},{c1}) {self.constraint_type.get()} ({r2},{c2}) | Total: {len(self.constraints)}")

    def clear_constraints(self):
        """Clear all constraints"""
        self.constraints = []
        self.draw_initial_grid()
        self.status_bar.config(text="Contraintes effacées")

    def solve_puzzle(self):
        """Solve the puzzle with current constraints"""
        if not self.grid:
            messagebox.showwarning("Attention", "Chargez d'abord une image!")
            return

        # Create new grid with constraints
        rows, cols = self.grid_size
        grid = TangoGridV5(rows, cols)

        # Set initial values
        for row, col, value in self.initial_values:
            grid.set_cell(row, col, value)

        # Add constraints
        for (r1, c1), (r2, c2), ctype in self.constraints:
            grid.add_constraint(r1, c1, r2, c2, ctype)

        # Solve
        self.status_bar.config(text="Résolution en cours...")
        self.root.update()

        solver = TangoSolverV5(grid)
        solved, iterations, time_ms = solver.solve(max_iterations=100)

        # Display solution
        self.draw_solution(grid)

        filled = sum(1 for r in range(rows) for c in range(cols)
                    if grid.get_cell(r, c) is not None)
        total = rows * cols

        if solved:
            self.status_bar.config(
                text=f"✓ Puzzle résolu! {iterations} itérations, {time_ms:.2f}ms"
            )
            messagebox.showinfo("Succès", f"Puzzle résolu à 100%!\n"
                                         f"Iterations: {iterations}\n"
                                         f"Temps: {time_ms:.2f}ms")
        else:
            self.status_bar.config(
                text=f"⚠️ Résolution partielle: {filled}/{total} ({filled*100//total}%)"
            )
            messagebox.showwarning("Résolution partielle",
                                  f"Puzzle résolu à {filled*100//total}%\n"
                                  f"Ajoutez plus de contraintes ou vérifiez les valeurs initiales.")

    def draw_solution(self, grid):
        """Draw the solution grid"""
        self.solution_canvas.delete("all")

        rows, cols = self.grid_size
        canvas_width = self.solution_canvas.winfo_width()
        canvas_height = self.solution_canvas.winfo_height()

        if canvas_width < 100:
            canvas_width = 400
        if canvas_height < 100:
            canvas_height = 400

        cell_size = min((canvas_width - 40) // cols, (canvas_height - 40) // rows)
        offset_x = (canvas_width - cell_size * cols) // 2
        offset_y = (canvas_height - cell_size * rows) // 2

        # Draw grid
        for r in range(rows):
            for c in range(cols):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Check if this was an initial value
                was_initial = any(row == r and col == c for row, col, _ in self.initial_values)

                fill_color = "lightyellow" if was_initial else "white"

                # Draw cell
                self.solution_canvas.create_rectangle(x1, y1, x2, y2,
                                                     outline="black", fill=fill_color)

                # Draw value
                value = grid.get_cell(r, c)
                if value is not None:
                    text_color = "darkblue" if was_initial else "green"
                    self.solution_canvas.create_text(x1 + cell_size//2, y1 + cell_size//2,
                                                    text=str(value),
                                                    font=("Arial", cell_size//2, "bold"),
                                                    fill=text_color)


def main():
    """Launch GUI"""
    root = tk.Tk()
    app = TangoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
