from rtree import index
from shapely.geometry import shape
from shapely.geometry import box, Polygon
import geopandas as gpd
import pickle


import time
import math
import numpy as np
import subprocess


def Rtree_indexing(LandPolygons):
    print('--------R-tree indexing----------')
    # R-tree index creation
    settings = index.Property()
    #storage = DictStorage()
    idx = index.Index(properties=settings)
    for id, geom in enumerate(LandPolygons):
        idx.insert(id, geom, obj=geom)

    return idx


def range_query(idx, QueryFile):
    print("---------- Range Query -----------")
    total_time_query = 0
    for i, query_range in enumerate(QueryFile, start=1):
        start_query_time = time.time()
        print(f"\nQuery {i}: Searching intervals that overlap with {query_range}")
        potential = list(idx.intersection(query_range, objects=True))
        print("Potential result: ", len(potential))

        end_query_time = time.time()
        query_time = end_query_time - start_query_time
        total_time_query += query_time

    print(f"Total time for 10000 range query: {(total_time_query):.4f} s")



def main():
    # Measure training time for R-tree index
    start_idx_time = time.time()

    LandPolygons = np.load("nonIdealMBRs_5M.npy", allow_pickle=True)
    QueryFile = np.load("nonIdealMBRsQueries.npy", allow_pickle=True)

    ############## Index Construction ################
    idx = Rtree_indexing(LandPolygons)
    total_time_idx = time.time() - start_idx_time

    ############## Range Query ################
    range_query(idx, QueryFile)

    print(f"Time for indexing: {total_time_idx:.4f} s")


if __name__ == "__main__":
    main()




