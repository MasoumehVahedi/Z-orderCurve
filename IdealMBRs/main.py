import os
import sys
import time
import numpy as np

from Zaddress import MortonCode
from intervalTree import BalancedIntervalTree, Interval



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

        z_intervals.append(Interval(zmin, zmax))

    return z_intervals




def search(mbrs, queries):
    start_time = time.time()
    # Calculate intervals from the data
    morton = MortonCode()
    intervals = calculate_z_intervals(mbrs, morton)

    # Sort intervals and build the balanced tree directly
    intervals.sort(key=lambda interval: interval.low)
    balancedTree_index = BalancedIntervalTree(intervals)
    tree_build_time = time.time() - start_time
    print(f"Time to build the tree: {tree_build_time:.4f} seconds")

    # Process queries
    query_intervals = calculate_z_intervals(queries, morton)
    total_start_time = time.time()
    for index, query_interval in enumerate(query_intervals):
        results = balancedTree_index.query(query_interval)
        print(f"Results for query {index + 1} with {query_interval}: {len(results)} matching entries")

    total_end_time = time.time()
    total_query_time = total_end_time - total_start_time
    print(f"Total time for all queries: {total_query_time} seconds")




def main():
    mbrs = np.load("idealMBRs_5M.npy", allow_pickle=True)
    queries = np.load("idealQueries.npy", allow_pickle=True)

    search(mbrs, queries)



if __name__ == "__main__":
    main()


