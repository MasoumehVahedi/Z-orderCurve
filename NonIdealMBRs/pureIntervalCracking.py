import os
import sys
import time
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
cracking_splindex_dir = os.path.join(parent_dir, 'CrackingSPLindex')
sys.path.append(cracking_splindex_dir)

from interval_structures import Interval
from intervalCracking import IntervalCracking

from Zaddress import MortonCode




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
        z_intervals.append([(zmin, zmax), mbr])

    return z_intervals



def main():
    mbrs_path = "nonIdealMBRs_5M.npy"
    mbrs = np.load(mbrs_path, allow_pickle=True)

    query_path = "nonIdealMBRsQueries.npy"
    query_ranges = np.load(query_path, allow_pickle=True)

    morton = MortonCode()

    start_cpu_time = time.time()
    mbr_z_intervals = calculate_z_intervals(mbrs, morton)
    index = IntervalCracking(mbr_z_intervals)

    ######## Range Query ##########
    query_intervals = calculate_z_intervals(query_ranges, morton)
    for i, (interval, mbr) in enumerate(query_intervals):
        query_interval = Interval(interval[0], interval[1])
        results = index.adaptiveSearch(query_interval, mbr)
        print(f"Query {i} results: {len(results)}")

    end_cpu_time = time.time()
    cpu_time = end_cpu_time - start_cpu_time
    print("CPU time for pure interval cracking =", cpu_time, "seconds")


if __name__ == "__main__":
    main()