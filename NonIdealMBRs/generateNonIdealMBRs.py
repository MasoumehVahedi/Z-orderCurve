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




# Function to generate non-ideal MBRs (integer-based)
def generate_non_ideal_mbrs(num_mbrs, grid_size, min_box_size, max_box_size):
    """Generate non-ideal MBRs with random integer coordinates and sizes."""
    non_ideal_mbrs = []

    for _ in range(num_mbrs):
        # Randomly choose a lower-left corner for the MBR within the geographic boundaries
        min_x = np.random.randint(0, grid_size)
        min_y = np.random.randint(0, grid_size)

        # Randomly choose width and height within the specified range
        width = np.random.randint(min_box_size, max_box_size + 1)
        height = np.random.randint(min_box_size, max_box_size + 1)

        # Calculate max_x and max_y for the MBR, ensuring it stays within boundaries
        max_x = min(min_x + width, grid_size - 1)
        max_y = min(min_y + height, grid_size - 1)

        non_ideal_mbrs.append((min_x, min_y, max_x, max_y))

    return non_ideal_mbrs





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
        zmin = int(min(z_bottom_left, z_bottom_right, z_top_left, z_top_right))
        zmax = int(max(z_bottom_left, z_bottom_right, z_top_left, z_top_right))

        z_intervals.append((zmin, zmax))

    return z_intervals




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
    #num_mbrs = 500000   # for non_ideal_mbrs
    num_mbrs = 5   # for non_ideal_queries
    n = 4           # This creates a grid of 2^10 x 2^10 = 1024 x 1024 cells
    grid_size = 2 ** n
    #min_box_size = 0.5   # for non_ideal_mbrs
    #max_box_size = 1.0   # for non_ideal_mbrs
    min_box_size = 1.0    # for non_ideal_queries
    max_box_size = 1.5    # for non_ideal_queries

    # Generate non-ideal MBRs
    non_ideal_mbrs = generate_non_ideal_mbrs(num_mbrs, grid_size, min_box_size, max_box_size)
    #print(non_ideal_mbrs[:10])
    #np.save("nonIdealMBRs_5M.npy", np.array(non_ideal_mbrs))

    #non_ideal_queries = generate_non_ideal_mbrs(num_mbrs, grid_size, min_box_size, max_box_size)
    #print(non_ideal_queries[:10])

    #np.save("nonIdealMBRsQueries.npy", np.array(non_ideal_queries))

    # Calculate Z-index intervals for each box
    morton = MortonCode()
    #z_intervals = calculate_z_intervals(non_ideal_mbrs, morton)
    #print(z_intervals)

    plot_mbrs_and_z_order(non_ideal_mbrs, morton, n=4)



if __name__ == "__main__":
    main()
