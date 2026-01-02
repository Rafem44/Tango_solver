#!/usr/bin/env python3
"""
Tango OCR V2 - Improved puzzle recognition

Enhanced OCR with better grid detection, cell segmentation,
and symbol recognition specifically for Tango puzzles.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Cell:
    """Cell in the grid"""
    row: int
    col: int
    value: Optional[int]  # None, 0, or 1
    x: int  # pixel coordinates
    y: int
    width: int
    height: int


@dataclass
class Constraint:
    """Constraint between cells"""
    cell1: Tuple[int, int]
    cell2: Tuple[int, int]
    type: str  # "=" or "×"


class TangoOCRV2:
    """Improved OCR for Tango puzzles"""

    def __init__(self, debug=False):
        self.debug = debug
        self.img = None
        self.gray = None
        self.grid_contour = None
        self.cells = []
        self.grid_size = (0, 0)

    def read_puzzle(self, image_path: str) -> dict:
        """
        Read puzzle from image with improved detection

        Returns:
            dict with grid_size, initial_values, constraints
        """
        # Load image
        self.img = cv2.imread(image_path)
        if self.img is None:
            raise ValueError(f"Could not load image: {image_path}")

        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        if self.debug:
            print(f"Image loaded: {self.img.shape}")
            cv2.imwrite('/tmp/debug_original.png', self.img)

        # Step 1: Detect grid
        grid_rect = self._detect_grid_contour()
        if grid_rect is None:
            raise ValueError("Could not detect grid")

        if self.debug:
            print(f"Grid detected: {grid_rect}")

        # Step 2: Determine grid size (count cells)
        grid_size = self._determine_grid_size(grid_rect)
        self.grid_size = grid_size

        if self.debug:
            print(f"Grid size: {grid_size[0]}×{grid_size[1]}")

        # Step 3: Segment cells
        cells = self._segment_cells(grid_rect, grid_size)
        self.cells = cells

        # Step 4: Detect symbols in cells
        initial_values = self._detect_symbols(cells)

        if self.debug:
            print(f"Detected {len(initial_values)} initial values")

        # Step 5: Detect constraints
        constraints = self._detect_constraints(cells, grid_rect)

        if self.debug:
            print(f"Detected {len(constraints)} constraints")

        return {
            'grid_size': grid_size,
            'initial_values': initial_values,
            'constraints': constraints
        }

    def _detect_grid_contour(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the main grid using contour detection

        Returns:
            (x, y, width, height) of grid rectangle
        """
        # Apply thresholding
        _, thresh = cv2.threshold(self.gray, 240, 255, cv2.THRESH_BINARY_INV)

        if self.debug:
            cv2.imwrite('/tmp/debug_thresh.png', thresh)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Find largest rectangular contour
        largest_area = 0
        best_rect = None

        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            # Filter: must be reasonably square and large enough
            aspect_ratio = w / h if h > 0 else 0
            if 0.8 < aspect_ratio < 1.2 and area > largest_area and area > 10000:
                largest_area = area
                best_rect = (x, y, w, h)

        if self.debug and best_rect:
            debug_img = self.img.copy()
            x, y, w, h = best_rect
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.imwrite('/tmp/debug_grid_detection.png', debug_img)

        return best_rect

    def _determine_grid_size(self, grid_rect: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        Determine grid size by detecting cell boundaries

        For now, we'll try common sizes and pick the one that fits best
        """
        x, y, w, h = grid_rect

        # Try common grid sizes
        for size in [6, 8, 10, 12]:
            # Check if dimensions are divisible
            cell_width = w / size
            cell_height = h / size

            # If cells are roughly square and reasonable size
            aspect = cell_width / cell_height if cell_height > 0 else 0
            if 0.9 < aspect < 1.1 and 40 < cell_width < 200:
                return (size, size)

        # Default to 6×6
        return (6, 6)

    def _segment_cells(self, grid_rect: Tuple[int, int, int, int],
                      grid_size: Tuple[int, int]) -> List[Cell]:
        """
        Segment grid into individual cells
        """
        x, y, w, h = grid_rect
        rows, cols = grid_size

        cells = []
        cell_width = w / cols
        cell_height = h / rows

        for r in range(rows):
            for c in range(cols):
                cell_x = int(x + c * cell_width)
                cell_y = int(y + r * cell_height)
                cell_w = int(cell_width)
                cell_h = int(cell_height)

                cell = Cell(
                    row=r, col=c, value=None,
                    x=cell_x, y=cell_y,
                    width=cell_w, height=cell_h
                )
                cells.append(cell)

        if self.debug:
            debug_img = self.img.copy()
            for cell in cells:
                cv2.rectangle(debug_img,
                            (cell.x, cell.y),
                            (cell.x + cell.width, cell.y + cell.height),
                            (255, 0, 0), 1)
            cv2.imwrite('/tmp/debug_cells.png', debug_img)

        return cells

    def _detect_symbols(self, cells: List[Cell]) -> List[Tuple[int, int, int]]:
        """
        Detect orange circles (1) and blue crescents (0) in cells
        """
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        initial_values = []

        # Color ranges (adjusted for better detection)
        # Orange: broader range
        orange_lower = np.array([0, 120, 120])
        orange_upper = np.array([30, 255, 255])

        # Blue: adjusted range
        blue_lower = np.array([90, 80, 80])
        blue_upper = np.array([140, 255, 255])

        debug_img = self.img.copy() if self.debug else None

        for cell in cells:
            # Extract cell ROI with padding to avoid border
            padding = 5
            roi_x = cell.x + padding
            roi_y = cell.y + padding
            roi_w = cell.width - 2*padding
            roi_h = cell.height - 2*padding

            if roi_w <= 0 or roi_h <= 0:
                continue

            cell_roi_hsv = hsv[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

            # Detect orange
            orange_mask = cv2.inRange(cell_roi_hsv, orange_lower, orange_upper)
            orange_pixels = cv2.countNonZero(orange_mask)

            # Detect blue
            blue_mask = cv2.inRange(cell_roi_hsv, blue_lower, blue_upper)
            blue_pixels = cv2.countNonZero(blue_mask)

            # Threshold: at least 100 pixels
            if orange_pixels > 100:
                initial_values.append((cell.row, cell.col, 1))
                cell.value = 1
                if self.debug:
                    cv2.putText(debug_img, "1",
                              (cell.x + cell.width//2 - 10, cell.y + cell.height//2 + 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            elif blue_pixels > 100:
                initial_values.append((cell.row, cell.col, 0))
                cell.value = 0
                if self.debug:
                    cv2.putText(debug_img, "0",
                              (cell.x + cell.width//2 - 10, cell.y + cell.height//2 + 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 0), 2)

        if self.debug:
            cv2.imwrite('/tmp/debug_symbols.png', debug_img)

        return initial_values

    def _detect_constraints(self, cells: List[Cell],
                          grid_rect: Tuple[int, int, int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int], str]]:
        """
        Detect = and × constraints between cells

        Strategy: Look for dark text between cells
        """
        constraints = []

        # Convert to grayscale for text detection
        gray = self.gray.copy()

        # Threshold for dark text
        _, text_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        if self.debug:
            cv2.imwrite('/tmp/debug_text_mask.png', text_mask)

        # Create a grid to track cells
        rows, cols = self.grid_size
        cell_grid = {}
        for cell in cells:
            cell_grid[(cell.row, cell.col)] = cell

        # Check horizontal constraints (between columns)
        for r in range(rows):
            for c in range(cols - 1):
                cell1 = cell_grid.get((r, c))
                cell2 = cell_grid.get((r, c+1))

                if cell1 and cell2:
                    # Region between cells
                    between_x = cell1.x + cell1.width
                    between_y = cell1.y + cell1.height // 4
                    between_w = cell2.x - (cell1.x + cell1.width)
                    between_h = cell1.height // 2

                    if between_w > 0 and between_h > 0:
                        roi = text_mask[between_y:between_y+between_h,
                                       between_x:between_x+between_w]

                        # Count dark pixels
                        dark_pixels = cv2.countNonZero(roi)

                        # If enough dark pixels, there's probably a symbol
                        if dark_pixels > 20:
                            # Try to distinguish = from ×
                            # Simple heuristic: × has more diagonal structure
                            constraint_type = self._classify_constraint(roi)
                            if constraint_type:
                                constraints.append(((r, c), (r, c+1), constraint_type))

        # Check vertical constraints (between rows)
        for r in range(rows - 1):
            for c in range(cols):
                cell1 = cell_grid.get((r, c))
                cell2 = cell_grid.get((r+1, c))

                if cell1 and cell2:
                    # Region between cells
                    between_x = cell1.x + cell1.width // 4
                    between_y = cell1.y + cell1.height
                    between_w = cell1.width // 2
                    between_h = cell2.y - (cell1.y + cell1.height)

                    if between_w > 0 and between_h > 0:
                        roi = text_mask[between_y:between_y+between_h,
                                       between_x:between_x+between_w]

                        dark_pixels = cv2.countNonZero(roi)

                        if dark_pixels > 20:
                            constraint_type = self._classify_constraint(roi)
                            if constraint_type:
                                constraints.append(((r, c), (r+1, c), constraint_type))

        return constraints

    def _classify_constraint(self, roi: np.ndarray) -> Optional[str]:
        """
        Classify constraint as = or ×

        Simple heuristic:
        - = has horizontal structure
        - × has diagonal structure
        """
        if roi.size == 0:
            return None

        h, w = roi.shape

        # Analyze structure
        # For =: expect two horizontal lines
        # For ×: expect diagonal pattern

        # Simple approach: look at center row vs corners
        if h > 2 and w > 2:
            center = roi[h//2, :]
            corners = roi[0, 0] + roi[0, -1] + roi[-1, 0] + roi[-1, -1]

            center_sum = np.sum(center > 0)

            # If center row has many pixels, likely =
            if center_sum > w * 0.5:
                return "="
            # If corners are active, likely ×
            elif corners > 200:
                return "×"

        return None

    def visualize(self, output_path: str = '/tmp/tango_ocr_debug.png'):
        """Create visualization of detection"""
        if self.img is None:
            return

        debug_img = self.img.copy()

        # Draw cells
        for cell in self.cells:
            color = (200, 200, 200)
            if cell.value == 1:
                color = (0, 165, 255)  # Orange
            elif cell.value == 0:
                color = (255, 100, 0)  # Blue

            cv2.rectangle(debug_img, (cell.x, cell.y),
                         (cell.x + cell.width, cell.y + cell.height),
                         color, 2)

        cv2.imwrite(output_path, debug_img)
        if self.debug:
            print(f"Visualization saved: {output_path}")


def main():
    """Test the improved OCR"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tango_ocr_v2.py <image_path>")
        return

    image_path = sys.argv[1]

    print("=" * 70)
    print("TANGO OCR V2 - IMPROVED RECOGNITION")
    print("=" * 70)
    print()

    ocr = TangoOCRV2(debug=True)

    try:
        result = ocr.read_puzzle(image_path)

        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Grid size: {result['grid_size'][0]}×{result['grid_size'][1]}")
        print(f"\nInitial values: {len(result['initial_values'])}")
        for row, col, val in result['initial_values']:
            symbol = "🟠" if val == 1 else "🌙"
            print(f"  ({row},{col}) = {val} {symbol}")

        print(f"\nConstraints: {len(result['constraints'])}")
        for (r1, c1), (r2, c2), ctype in result['constraints']:
            print(f"  ({r1},{c1}) {ctype} ({r2},{c2})")

        ocr.visualize()
        print("\n✓ Debug images saved to /tmp/debug_*.png")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
