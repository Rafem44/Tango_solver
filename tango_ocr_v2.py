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

        Improved strategy:
        1. Look for dark regions between cells
        2. Use multiple thresholds and techniques
        3. Better classification with shape analysis
        """
        constraints = []

        # Create better text mask with adaptive thresholding
        gray = self.gray.copy()

        # Try multiple threshold methods
        _, binary1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 11, 2)

        # Combine both
        text_mask = cv2.bitwise_or(binary1, binary2)

        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        text_mask = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)

        if self.debug:
            cv2.imwrite('/tmp/debug_text_mask_improved.png', text_mask)
            debug_constraints = self.img.copy()

        # Create cell grid
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
                    constraint_type = self._detect_constraint_between_cells(
                        cell1, cell2, text_mask, 'horizontal'
                    )

                    if constraint_type:
                        constraints.append(((r, c), (r, c+1), constraint_type))

                        if self.debug:
                            # Draw constraint on debug image
                            cx = (cell1.x + cell1.width + cell2.x) // 2
                            cy = (cell1.y + cell2.y + cell2.height) // 2
                            cv2.putText(debug_constraints, constraint_type,
                                      (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX,
                                      0.5, (0, 0, 255), 2)

        # Check vertical constraints (between rows)
        for r in range(rows - 1):
            for c in range(cols):
                cell1 = cell_grid.get((r, c))
                cell2 = cell_grid.get((r+1, c))

                if cell1 and cell2:
                    constraint_type = self._detect_constraint_between_cells(
                        cell1, cell2, text_mask, 'vertical'
                    )

                    if constraint_type:
                        constraints.append(((r, c), (r+1, c), constraint_type))

                        if self.debug:
                            cx = (cell1.x + cell2.x + cell2.width) // 2
                            cy = (cell1.y + cell1.height + cell2.y) // 2
                            cv2.putText(debug_constraints, constraint_type,
                                      (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX,
                                      0.5, (0, 0, 255), 2)

        if self.debug:
            cv2.imwrite('/tmp/debug_constraints_detected.png', debug_constraints)

        return constraints

    def _detect_constraint_between_cells(self, cell1: Cell, cell2: Cell,
                                        text_mask: np.ndarray,
                                        direction: str) -> Optional[str]:
        """
        Detect constraint between two adjacent cells

        Args:
            cell1, cell2: Adjacent cells
            text_mask: Binary mask of text regions
            direction: 'horizontal' or 'vertical'

        Returns:
            "=" or "×" or None
        """
        if direction == 'horizontal':
            # Region between horizontally adjacent cells
            between_x = cell1.x + cell1.width
            between_w = cell2.x - (cell1.x + cell1.width)
            between_y = cell1.y + cell1.height // 3
            between_h = cell1.height // 3
        else:  # vertical
            # Region between vertically adjacent cells
            between_x = cell1.x + cell1.width // 3
            between_w = cell1.width // 3
            between_y = cell1.y + cell1.height
            between_h = cell2.y - (cell1.y + cell1.height)

        # Check bounds
        if between_w <= 0 or between_h <= 0:
            return None

        # Extract ROI
        roi = text_mask[between_y:between_y+between_h,
                       between_x:between_x+between_w]

        if roi.size == 0:
            return None

        # Count dark pixels
        dark_pixels = cv2.countNonZero(roi)
        total_pixels = roi.size
        dark_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0

        # Need significant dark content
        if dark_ratio < 0.1:
            return None

        # Classify the symbol
        return self._classify_constraint_improved(roi, direction)

    def _classify_constraint(self, roi: np.ndarray) -> Optional[str]:
        """
        Old classification method (kept for compatibility)
        """
        return self._classify_constraint_improved(roi, 'horizontal')

    def _classify_constraint_improved(self, roi: np.ndarray, direction: str) -> Optional[str]:
        """
        Improved constraint classification

        Strategy:
        - = symbol: two horizontal lines (high horizontal density)
        - × symbol: diagonal crossing (high corner/diagonal activity)
        """
        if roi.size == 0 or roi.shape[0] < 3 or roi.shape[1] < 3:
            return None

        h, w = roi.shape

        # Analyze different regions
        # Divide ROI into 3x3 grid
        third_h = h // 3
        third_w = w // 3

        if third_h == 0 or third_w == 0:
            return None

        # Extract 9 regions
        regions = []
        for i in range(3):
            for j in range(3):
                y1, y2 = i * third_h, (i + 1) * third_h if i < 2 else h
                x1, x2 = j * third_w, (j + 1) * third_w if j < 2 else w
                region = roi[y1:y2, x1:x2]
                density = np.sum(region > 0) / region.size if region.size > 0 else 0
                regions.append(density)

        # regions layout:
        # 0 1 2
        # 3 4 5
        # 6 7 8

        # For = : expect high density in middle row (3, 4, 5) and possibly top/bottom
        middle_row_density = (regions[3] + regions[4] + regions[5]) / 3

        # For × : expect high density in corners (0, 2, 6, 8) and center (4)
        corner_density = (regions[0] + regions[2] + regions[6] + regions[8]) / 4
        center_density = regions[4]

        # Additional analysis: count horizontal vs diagonal lines
        # Horizontal lines (for =)
        horizontal_score = 0
        for i in range(h):
            row_sum = np.sum(roi[i, :] > 0)
            if row_sum > w * 0.5:  # More than half the row is dark
                horizontal_score += 1

        # Diagonal analysis (for ×)
        # Check main diagonal
        diag1_score = sum(roi[min(i, h-1), min(i, w-1)] > 0 for i in range(min(h, w)))
        # Check anti-diagonal
        diag2_score = sum(roi[min(i, h-1), max(0, w-1-i)] > 0 for i in range(min(h, w)))
        diagonal_score = diag1_score + diag2_score

        # Decision logic
        # = tends to have:
        #   - High horizontal_score (at least 2 horizontal lines)
        #   - High middle_row_density
        # × tends to have:
        #   - High diagonal_score
        #   - High corner_density
        #   - High center_density

        equals_score = horizontal_score * 2 + middle_row_density * 10
        cross_score = diagonal_score + corner_density * 10 + center_density * 5

        if self.debug:
            print(f"  ROI {roi.shape}: = score={equals_score:.2f}, × score={cross_score:.2f}")
            print(f"    horizontal_score={horizontal_score}, diagonal_score={diagonal_score}")
            print(f"    middle_row={middle_row_density:.2f}, corners={corner_density:.2f}")

        # Require a clear winner
        if equals_score > cross_score and equals_score > 3:
            return "="
        elif cross_score > equals_score and cross_score > 3:
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
