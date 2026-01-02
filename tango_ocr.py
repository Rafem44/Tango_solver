#!/usr/bin/env python3
"""
Tango OCR - Automatic puzzle recognition from images

This module reads Tango puzzle images and automatically extracts:
- Grid size (number of rows and columns)
- Initial cell values (Orange 🟠 = 1, Blue 🌙 = 0)
- Constraints (= and × symbols)
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Cell:
    """Represents a cell in the grid"""
    row: int
    col: int
    value: Optional[int]  # None, 0, or 1
    x: int  # pixel x coordinate
    y: int  # pixel y coordinate
    width: int
    height: int


@dataclass
class Constraint:
    """Represents a constraint between two cells"""
    cell1: Tuple[int, int]  # (row, col)
    cell2: Tuple[int, int]  # (row, col)
    constraint_type: str  # "=" or "×"
    x: int  # pixel x coordinate
    y: int  # pixel y coordinate


class TangoOCR:
    """OCR system for reading Tango puzzles from images"""

    def __init__(self, debug=False):
        self.debug = debug
        self.cells = []
        self.constraints = []
        self.grid_size = (0, 0)  # (rows, cols)

    def read_puzzle(self, image_path: str) -> dict:
        """
        Read a puzzle from an image file

        Returns:
            dict with keys:
                - 'grid_size': (rows, cols)
                - 'initial_values': list of (row, col, value)
                - 'constraints': list of ((r1,c1), (r2,c2), type)
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        if self.debug:
            print(f"Image loaded: {img.shape}")

        # Detect grid
        grid_size = self._detect_grid_size(img)
        self.grid_size = grid_size

        if self.debug:
            print(f"Detected grid size: {grid_size[0]}×{grid_size[1]}")

        # Detect cells
        cells = self._detect_cells(img, grid_size)
        self.cells = cells

        # Detect cell values (orange circles and blue moons)
        initial_values = self._detect_cell_values(img, cells)

        if self.debug:
            print(f"Detected {len(initial_values)} initial values")

        # Detect constraints (= and ×)
        constraints = self._detect_constraints(img, cells)
        self.constraints = constraints

        if self.debug:
            print(f"Detected {len(constraints)} constraints")

        return {
            'grid_size': grid_size,
            'initial_values': initial_values,
            'constraints': constraints
        }

    def _detect_grid_size(self, img: np.ndarray) -> Tuple[int, int]:
        """
        Detect the grid size by finding horizontal and vertical lines

        Strategy:
        1. Convert to grayscale
        2. Apply edge detection
        3. Find horizontal and vertical lines using Hough transform
        4. Count the number of grid lines to determine rows and columns
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Detect edges
        edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(
            edges, 1, np.pi/180, threshold=100,
            minLineLength=100, maxLineGap=10
        )

        if lines is None:
            # Fallback: try to detect grid cells by color/shape
            return self._detect_grid_size_by_cells(img)

        # Separate horizontal and vertical lines
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calculate angle
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

            # Horizontal line (angle close to 0 or 180)
            if angle < 10 or angle > 170:
                horizontal_lines.append((y1 + y2) // 2)  # Average y position

            # Vertical line (angle close to 90)
            elif 80 < angle < 100:
                vertical_lines.append((x1 + x2) // 2)  # Average x position

        # Remove duplicates (lines that are very close to each other)
        horizontal_lines = self._merge_close_lines(horizontal_lines)
        vertical_lines = self._merge_close_lines(vertical_lines)

        # Number of cells = number of lines - 1
        rows = len(horizontal_lines) - 1 if len(horizontal_lines) > 1 else 0
        cols = len(vertical_lines) - 1 if len(vertical_lines) > 1 else 0

        # Validate: should be at least 4×4 and at most 12×12
        if rows < 4 or rows > 12 or cols < 4 or cols > 12:
            # Fallback
            return self._detect_grid_size_by_cells(img)

        return (rows, cols)

    def _detect_grid_size_by_cells(self, img: np.ndarray) -> Tuple[int, int]:
        """
        Fallback method: detect grid size by counting cell shapes

        For now, we'll use a simple heuristic based on image aspect ratio
        and common Tango grid sizes (6×6, 8×8, 10×10)
        """
        height, width = img.shape[:2]
        aspect_ratio = width / height

        # Assume square grid for now
        if 0.9 <= aspect_ratio <= 1.1:
            # Probably square grid
            # Try common sizes: 6×6, 8×8, 10×10
            # Default to 6×6 as it's common
            return (6, 6)

        return (6, 6)  # Default fallback

    def _merge_close_lines(self, lines: List[int], threshold: int = 10) -> List[int]:
        """Merge lines that are very close to each other"""
        if not lines:
            return []

        sorted_lines = sorted(lines)
        merged = [sorted_lines[0]]

        for line in sorted_lines[1:]:
            if line - merged[-1] > threshold:
                merged.append(line)

        return merged

    def _detect_cells(self, img: np.ndarray, grid_size: Tuple[int, int]) -> List[Cell]:
        """
        Detect cell positions in the grid

        Strategy:
        1. Divide the image into a grid based on grid_size
        2. Create Cell objects for each grid position
        """
        rows, cols = grid_size
        height, width = img.shape[:2]

        # Find the grid area (excluding headers, etc.)
        # Assume the grid occupies the central portion of the image
        # We need to find the actual grid boundaries

        # For now, use a simple heuristic
        # Assume grid starts at y=100 and has equal cell sizes
        grid_top = 100  # pixels from top
        grid_left = 30  # pixels from left
        grid_height = height - grid_top - 100  # leave space at bottom
        grid_width = width - grid_left - 30  # leave space at right

        cell_height = grid_height / rows
        cell_width = grid_width / cols

        cells = []
        for r in range(rows):
            for c in range(cols):
                x = int(grid_left + c * cell_width)
                y = int(grid_top + r * cell_height)
                w = int(cell_width)
                h = int(cell_height)

                cell = Cell(
                    row=r, col=c, value=None,
                    x=x, y=y, width=w, height=h
                )
                cells.append(cell)

        return cells

    def _detect_cell_values(self, img: np.ndarray, cells: List[Cell]) -> List[Tuple[int, int, int]]:
        """
        Detect cell values by color detection

        Strategy:
        - Orange circles (🟠) = 1 (HSV range for orange)
        - Blue crescents (🌙) = 0 (HSV range for blue)
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        initial_values = []

        # Define color ranges in HSV
        # Orange: H=10-25, S=100-255, V=100-255
        orange_lower = np.array([5, 100, 100])
        orange_upper = np.array([25, 255, 255])

        # Blue: H=100-130, S=100-255, V=100-255
        blue_lower = np.array([100, 100, 100])
        blue_upper = np.array([130, 255, 255])

        for cell in cells:
            # Extract cell region
            cell_roi = hsv[cell.y:cell.y+cell.height, cell.x:cell.x+cell.width]

            # Check for orange
            orange_mask = cv2.inRange(cell_roi, orange_lower, orange_upper)
            orange_pixels = cv2.countNonZero(orange_mask)

            # Check for blue
            blue_mask = cv2.inRange(cell_roi, blue_lower, blue_upper)
            blue_pixels = cv2.countNonZero(blue_mask)

            # Threshold: at least 50 pixels of the color
            if orange_pixels > 50:
                initial_values.append((cell.row, cell.col, 1))
                cell.value = 1
            elif blue_pixels > 50:
                initial_values.append((cell.row, cell.col, 0))
                cell.value = 0

        return initial_values

    def _detect_constraints(self, img: np.ndarray, cells: List[Cell]) -> List[Tuple[Tuple[int, int], Tuple[int, int], str]]:
        """
        Detect constraint symbols (= and ×)

        Strategy:
        1. Look for text/symbols between cells
        2. Use template matching or OCR to recognize = and ×
        """
        # For now, return empty list
        # This is complex and would require template matching or OCR
        # We'll implement this in a future iteration

        constraints = []

        # TODO: Implement constraint detection
        # This could use:
        # - Template matching with pre-made templates of = and × symbols
        # - Tesseract OCR
        # - Contour detection for simple shapes

        return constraints

    def visualize_detection(self, image_path: str, output_path: str = None):
        """
        Visualize the detected grid, cells, and values

        Args:
            image_path: Path to input image
            output_path: Path to save visualization (optional)
        """
        img = cv2.imread(image_path)

        # Draw grid cells
        for cell in self.cells:
            # Draw rectangle
            color = (200, 200, 200)  # Gray
            if cell.value == 1:
                color = (0, 165, 255)  # Orange (BGR)
            elif cell.value == 0:
                color = (255, 100, 0)  # Blue (BGR)

            cv2.rectangle(img, (cell.x, cell.y),
                         (cell.x + cell.width, cell.y + cell.height),
                         color, 2)

            # Draw value
            if cell.value is not None:
                cv2.putText(img, str(cell.value),
                           (cell.x + cell.width // 2 - 10, cell.y + cell.height // 2 + 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        if output_path:
            cv2.imwrite(output_path, img)
            print(f"Visualization saved to: {output_path}")
        else:
            cv2.imshow("Tango OCR Detection", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


def main():
    """Test the OCR system"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tango_ocr.py <image_path>")
        return

    image_path = sys.argv[1]

    ocr = TangoOCR(debug=True)

    print("=" * 70)
    print("TANGO OCR - AUTOMATIC PUZZLE RECOGNITION")
    print("=" * 70)
    print()

    try:
        result = ocr.read_puzzle(image_path)

        print("\nResults:")
        print(f"Grid size: {result['grid_size'][0]}×{result['grid_size'][1]}")
        print(f"Initial values: {len(result['initial_values'])}")
        for row, col, val in result['initial_values']:
            print(f"  ({row},{col}) = {val}")
        print(f"Constraints: {len(result['constraints'])}")

        # Visualize
        output_path = image_path.replace('.', '_detected.')
        ocr.visualize_detection(image_path, output_path)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
