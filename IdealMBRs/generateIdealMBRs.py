import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class MortonCode:
    def __init__(self, scaleFactor=1000):
        self.scaleFactor = scaleFactor

    def z_order_index_to_int(self, x, y):
        x = (x | (x << 16)) & 0x0000FFFF
        x = (x | (x << 8)) & 0x00FF00FF
        x = (x | (x << 4)) & 0x0F0F0F0F
        x = (x | (x << 2)) & 0x33333333
        x = (x | (x << 1)) & 0x55555555

        y = (y | (y << 16)) & 0x0000FFFF
        y = (y | (y << 8)) & 0x00FF00FF
        y = (y | (y << 4)) & 0x0F0F0F0F
        y = (y | (y << 2)) & 0x33333333
        y = (y | (y << 1)) & 0x55555555
        return x | (y << 1)

    def interleave_latlng(self, lat, lng):
        # Latitude = y-coordinate
        # Longitude = x-coordinate
        if lng > 180:
            x = (lng % 180) + 180.0
        elif lng < -180:
            x = (-((-lng) % 180)) + 180.0
        else:
            x = lng + 180.0
        if lat > 90:
            y = (lat % 90) + 90.0
        elif lat < -90:
            y = (-((-lat) % 90)) + 90.0
        else:
            y = lat + 90.0

        x = round(x * self.scaleFactor)
        y = round(y * self.scaleFactor)

        morton_code = self.z_order_index_to_int(x, y)
        return morton_code

# Instantiate MortonCode
#morton = MortonCode(scaleFactor=1000)


# Function to generate Z-ideal boxes (both square and stretched)
def generate_5m_z_ideal_boxes(grid_size, k):
    """Generate approximately 5 million Z-ideal boxes in both forms: squares and stretched rectangles."""
    z_ideal_boxes = []

    # Number of boxes to generate
    #target_count = 5000000    # Ideal MBRs
    target_count = 10    # Ideal queries
    current_count = 0

    # Ideal Squares and Stretched Rectangles Generation Loop
    while current_count < target_count:
        # Ideal Squares
        m = np.random.randint(0, grid_size // (2 ** k))
        n = np.random.randint(0, grid_size // (2 ** k))

        x0 = m * (2 ** k)
        x1 = (m + 1) * (2 ** k) - 1
        y0 = n * (2 ** k)
        y1 = (n + 1) * (2 ** k) - 1

        z_ideal_boxes.append((x0, y0, x1, y1))
        current_count += 1

        if current_count >= target_count:
            break

        # Ideal Stretched Rectangles
        m = np.random.randint(0, grid_size // (2 ** k) // 2) * 2  # Ensures m is even
        n = np.random.randint(0, grid_size // (2 ** k))

        x0 = m * (2 ** k)
        x1 = (m + 2) * (2 ** k) - 1  # Stretches across two blocks in the x-direction
        y0 = n * (2 ** k)
        y1 = (n + 1) * (2 ** k) - 1

        z_ideal_boxes.append((x0, y0, x1, y1))
        current_count += 1

    return z_ideal_boxes



def calculate_z_intervals(mbrs, morton):
    """Calculate Z-index intervals for given MBRs."""
    z_intervals = []

    for mbr in mbrs:
        min_x, min_y, max_x, max_y = mbr

        # Calculate Z-indices for all four corners
        z_bottom_left = morton.z_order_index_to_int(min_x, min_y)
        z_bottom_right = morton.z_order_index_to_int(max_x, min_y)
        z_top_left = morton.z_order_index_to_int(min_x, max_y)
        z_top_right = morton.z_order_index_to_int(max_x, max_y)

        # Determine zmin and zmax
        zmin = min(z_bottom_left, z_bottom_right, z_top_left, z_top_right)
        zmax = max(z_bottom_left, z_bottom_right, z_top_left, z_top_right)

        z_intervals.append((zmin, zmax))

    return z_intervals


# Function to generate the Z-order curve path
def generate_z_order_curve_path(morton, n):
    """Generate the path of the Z-order curve for a given grid size."""
    grid_size = 2 ** n
    indices = np.arange(grid_size ** 2)
    x_grid = indices % grid_size
    y_grid = indices // grid_size

    # Calculate Morton codes using MortonCode class
    morton_codes = np.array([morton.z_order_index_to_int(x, y) for x, y in zip(x_grid, y_grid)])
    sorted_indices = np.argsort(morton_codes)

    x_sorted = x_grid[sorted_indices]
    y_sorted = y_grid[sorted_indices]
    return x_sorted, y_sorted, morton_codes[sorted_indices]


# Function to plot the grid, the generated MBRs, and the Z-order curve
def plot_mbrs_and_z_order(mbrs, morton, n):
    """Plot the grid, the generated MBRs, and the Z-order curve."""
    x_coords, y_coords, z_values = generate_z_order_curve_path(morton, n)
    grid_size = 2 ** n

    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot grid boundaries to visualize the grid cells clearly
    for i in range(grid_size + 1):
        # Vertical lines
        ax.plot([i, i], [0, grid_size], color='black', linewidth=0.5)
        # Horizontal lines
        ax.plot([0, grid_size], [i, i], color='black', linewidth=0.5)

    # Plot MBRs
    for min_x, min_y, max_x, max_y in mbrs[:1000]:  # Limit the number of boxes to plot for clarity
        rect = Rectangle((min_x, min_y), (max_x - min_x + 1), (max_y - min_y + 1),
                         edgecolor='blue', facecolor='lightblue', linewidth=1.0)
        ax.add_patch(rect)

    # Plot Z-order curve
    ax.plot(x_coords + 0.5, y_coords + 0.5, color='red', linewidth=1)

    # Label the Z-order value for each cell
    for i in range(len(x_coords)):
        ax.text(x_coords[i] + 0.5, y_coords[i] + 0.5, str(z_values[i]),
                color='red', fontsize=10, ha='center', va='center')

    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)
    ax.set_aspect('equal')
    plt.title('Ideal MBRs and Z-order Curve')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.gca().invert_yaxis()  # Invert y-axis to match the matrix-like coordinate system
    plt.show()


# Main function to generate and visualize MBRs, Z-order curve
def main():
    # Set grid dimension (for demonstration, but adapted for large-scale generation)
    n = 4  # This creates a grid of 2^10 x 2^10 = 1024 x 1024 cells
    k = 1  # Size scaling for ideal boxes, should be reasonably set
    grid_size = 2 ** n

    # Generate 5 million Z-ideal boxes
    z_ideal_mbrs = generate_5m_z_ideal_boxes(grid_size, k)    # k = 1
    #print(z_ideal_mbrs)
    #np.save("idealMBRs_5M.npy", np.array(z_ideal_mbrs))
    #print(f"5M Z-ideal MBRs saved to idealMBRs_5M.npy")

    # Calculate Z-index intervals for each box
    morton = MortonCode()
    #z_intervals = calculate_z_intervals(z_ideal_mbrs, morton)   # k = 2
    #print(z_intervals)

    # Save the generated Z-ideal boxes to an .npy file
    #np.save("idealQueries.npy", np.array(z_ideal_mbrs))
    #print(f"5 million Z-ideal MBRs saved to idealQueries.npy")

    # Plot only a subset of the generated MBRs to visualize the result
    plot_mbrs_and_z_order(z_ideal_mbrs, morton, n)



if __name__ == "__main__":
    main()
