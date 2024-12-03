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


    def z_order_index_to_long(self, x, y):
        xx = x
        yy = y

        xx = (xx | (xx << 16)) & 0x0000FFFF0000FFFF
        xx = (xx | (xx << 8)) & 0x00FF00FF00FF00FF
        xx = (xx | (xx << 4)) & 0x0F0F0F0F0F0F0F0F
        xx = (xx | (xx << 2)) & 0x3333333333333333
        xx = (xx | (xx << 1)) & 0x5555555555555555

        yy = (yy | (yy << 16)) & 0x0000FFFF0000FFFF
        yy = (yy | (yy << 8)) & 0x00FF00FF00FF00FF
        yy = (yy | (yy << 4)) & 0x0F0F0F0F0F0F0F0F
        yy = (yy | (yy << 2)) & 0x3333333333333333
        yy = (yy | (yy << 1)) & 0x5555555555555555

        return xx | (yy << 1)

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




def generate_non_ideal_mbrs(num_mbrs, min_width, max_width, min_height, max_height, boundary_x, boundary_y):
    """Generate non-ideal MBRs with random sizes and positions."""
    non_ideal_mbrs = []

    for _ in range(num_mbrs):
        # Randomly choose a lower-left corner for the MBR within the geographic boundaries
        min_x = np.random.uniform(-boundary_x, boundary_x)
        min_y = np.random.uniform(-boundary_y, boundary_y)

        # Randomly choose width and height within the specified range
        width = np.random.uniform(min_width, max_width)
        height = np.random.uniform(min_height, max_height)

        # Calculate max_x and max_y for the MBR, ensuring it stays within boundaries
        max_x = min(min_x + width, boundary_x)
        max_y = min(min_y + height, boundary_y)

        non_ideal_mbrs.append((min_x, min_y, max_x, max_y))

    return non_ideal_mbrs

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
    for min_x, min_y, max_x, max_y in mbrs:
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



def main():
    morton = MortonCode()

    num_mbrs = 100
    min_width = 0.5  # Minimum width of MBR
    max_width = 1.0  # Maximum width of MBR
    min_height = 0.5  # Minimum height of MBR
    max_height = 1.0  # Maximum height of MBR
    boundary_x = 180  # Longitude boundaries
    boundary_y = 90  # Latitude boundaries

    # Generate non-ideal MBRs
    non_ideal_mbrs = generate_non_ideal_mbrs(num_mbrs, min_width, max_width, min_height, max_height, boundary_x, boundary_y)

    # Plot only a subset of the generated MBRs to visualize the result
    plot_mbrs_and_z_order(non_ideal_mbrs, morton, n=4)

if __name__ == "__main__":
    main()
