"""
    Interval Cracking illustrates how cracking (i.e., dynamically partitioning data based on queries) can speed up future range queries.

    1- Core Concepts in Interval Cracking:

        - Dynamic Cracking: The IntervalCracking class dynamically partitions (cracks) the data based on
                            the query range. This helps in segregating data into smaller chunks that are more manageable and quicker to access
                            in subsequent queries.

        - Left, Overlapped, and Right Pieces: The data is partitioned into "left", "Overlapped", and "right" pieces based on the query,
                             and we keep track of how the data is partitioned and what ranges each partition covers.


    2- How Cracking Helps Speed Up Subsequent Queries:

        -Partitioning Data: By splitting data into left and right partitions around the query range,
                            subsequent queries can be optimised by only searching relevant partitions.
                            For example, a new query that falls entirely within the bounds of a previous
                            query's left piece only needs to search within that left partition, skipping the rest.
        -Reduced Search Space: Each partition effectively reduces the dataset's size that needs to be searched in future queries.
        -Dynamic Adaptation: As more queries are processed, the data becomes increasingly partitioned in a way that
                             reflects actual query patterns, leading to more efficient retrievals.

"""


import math
from collections import deque

from interval_structures import Interval, IntervalTree, IntervalTreeEntry, IntervalTreeNode



# ----------------------------------------------------------------------- #
#                           Interval Cracking Class
# ----------------------------------------------------------------------- #

class IntervalCracking:
    def __init__(self, intervals, max_entries=128, min_entries=None, FIRST_INIT=21474836, END_INIT=-21474836):
        self.max_entries = max_entries
        self.min_entries = min_entries or math.ceil(max_entries / 2)
        self.FIRST_INIT = FIRST_INIT
        self.END_INIT = END_INIT
        self.tree = IntervalTree()
        root_node = self.tree.root

        # Create a root node that includes all intervals as the initial tree structure
        overall_interval = self.calculate_bounding_interval([(Interval(interval[0], interval[1])) for interval in intervals])
        root_node.entries.append(IntervalTreeEntry(overall_interval))
        root_node.is_leaf = False

        # Create the first level of children nodes containing the intervals
        initial_node = IntervalTreeNode(is_leaf=True, parent=root_node, level=1)
        initial_node.entries = [IntervalTreeEntry(Interval(interval[0], interval[1])) for interval in intervals]
        root_node.entries[0].child = initial_node


    def adaptiveSearch(self, query_interval):
        queue = deque([self.tree.root])
        query_results = []

        while queue:
            node = queue.popleft()

            if node.is_leaf:
                results = self.searchAndCrack(query_interval, node)
                if results:
                    query_results.extend(results)
            else:
                for entry in node.entries:
                    if entry.child and self.intervals_overlap(entry.interval, query_interval):
                        queue.append(entry.child)

        return query_results


    def searchAndCrack(self, query_interval, node):
        """
           Performing interval cracking and incremental build the tree data structure:
            1- Left Node: Contains intervals strictly to the left of the query interval.
            2- Right Node: Contains intervals strictly to the right of the query interval.
            3- Overlapped Node: Contains intervals that overlap with the query interval.
        """
        query_results = []

        #if isinstance(node.entries[0], tuple):
        #    node.entries = [IntervalTreeEntry(interval=entry[0], data=entry[1]) for entry in node.entries]
        self.local_intervals = [entry.interval for entry in node.entries]

        # If the number of intervals is small, no need to crack, just search
        if len(node.entries) <= self.max_entries:
            query_results.extend(
                [entry.interval for entry in node.entries if not (entry.interval.max_val < query_interval[0] or entry.interval.min_val > query_interval[1])])
            return query_results


        this_piece_left = 0
        this_piece_right = len(self.local_intervals)

        crack_index_min = self.crackOnAxisMax(self.local_intervals, this_piece_left, this_piece_right,
                                              query_interval[0], Interval(self.FIRST_INIT, self.END_INIT),
                                              Interval(self.FIRST_INIT, self.END_INIT), False)

        left_intervals = self.local_intervals[:crack_index_min]

        crack_index_max = self.crackOnAxisMin(self.local_intervals, crack_index_min, this_piece_right,
                                              query_interval[1], Interval(self.FIRST_INIT, self.END_INIT),
                                              Interval(self.FIRST_INIT, self.END_INIT), True)

        right_intervals = self.local_intervals[crack_index_max:]
        overlapped_intervals = self.local_intervals[crack_index_min:crack_index_max]

        node.entries.clear()  # Clearing the current node entries

        if left_intervals:
            left_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            left_child.entries = [IntervalTreeEntry(interval) for interval in left_intervals]
            left_bounding_interval = self.calculate_bounding_interval(left_intervals)
            node.is_leaf = False
            node.entries.append(IntervalTreeEntry(left_bounding_interval, child=left_child))

        if right_intervals:
            right_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            right_child.entries = [IntervalTreeEntry(interval) for interval in right_intervals]
            right_bounding_interval = self.calculate_bounding_interval(right_intervals)
            node.is_leaf = False
            node.entries.append(IntervalTreeEntry(right_bounding_interval, child=right_child))

        if overlapped_intervals:
            overlapped_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            overlapped_child.entries = [IntervalTreeEntry(interval) for interval in overlapped_intervals]
            overlapped_bounding_interval = self.calculate_bounding_interval(overlapped_intervals)
            node.is_leaf = False
            node.entries.append(IntervalTreeEntry(overlapped_bounding_interval, child=overlapped_child))

        return overlapped_intervals

    def calculate_bounding_interval(self, intervals):
        min_val = min(interval.min_val for interval in intervals)
        max_val = max(interval.max_val for interval in intervals)
        return Interval(min_val, max_val)

    def intervals_overlap(self, interval1, interval2):
        return not (interval1.max_val < interval2[0] or interval1.min_val > interval2[1])
        #return not (interval1.max_val < interval2.min_val or interval1.min_val > interval2.max_val)

    def crackOnAxisMin(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        return self.partition(intervals, low, high, crack_value, left_rect, right_rect, check_min)

    def crackOnAxisMax(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        return self.partition(intervals, low, high, crack_value, left_rect, right_rect, check_min)

    def partition(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        """
           Partitions MBR z-intervals around a pivot value.

           :param low: Lower index of the range to partition
           :param high: Upper index of the range to partition
           :param pivot: The pivot value to partition around
           :param left_rect: Interval representing the left boundary
           :param right_rect: Interval representing the right boundary
           :param check_min: Boolean flag to check against the minimum value of intervals
        """
        x1, x2 = low, high - 1

        if check_min:
            while x1 <= x2:
                if intervals[x1].min_val < crack_value:
                    if intervals[x1].max_val > left_rect.max_val:
                        left_rect.max_val = intervals[x1].max_val
                    x1 += 1
                else:
                    while x2 >= x1 and intervals[x2].min_val >= crack_value:
                        if intervals[x2].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2].min_val
                        if intervals[x2].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2].max_val
                        x2 -= 1

                    if x1 < x2:
                        intervals[x1], intervals[x2] = intervals[x2], intervals[x1]
                        if intervals[x1].max_val > left_rect.max_val:
                            left_rect.max_val = intervals[x1].max_val
                        if intervals[x2].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2].min_val
                        if intervals[x2].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2].max_val
                        x2 -= 1
                        x1 += 1
        else:
            while x1 <= x2:
                if intervals[x1].max_val < crack_value:
                    if intervals[x1].min_val < left_rect.min_val:
                        left_rect.min_val = intervals[x1].min_val
                    if intervals[x1].max_val > left_rect.max_val:
                        left_rect.max_val = intervals[x1].max_val
                    x1 += 1
                else:
                    while x2 >= x1 and intervals[x2].max_val >= crack_value:
                        if intervals[x2].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2].min_val
                        if intervals[x2].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2].max_val
                        x2 -= 1

                    if x1 < x2:
                        intervals[x1], intervals[x2] = intervals[x2], intervals[x1]
                        if intervals[x1].min_val < left_rect.min_val:
                            left_rect.min_val = intervals[x1].min_val
                        if intervals[x1].max_val > left_rect.max_val:
                            left_rect.max_val = intervals[x1].max_val
                        if intervals[x2].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2].min_val
                        if intervals[x2].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2].max_val
                        x2 -= 1
                        x1 += 1
        return x1


    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.tree.root

        result = []
        queue = deque([(node, level)])
        while queue:
            node, level = queue.popleft()
            for entry in node.entries:
                if entry.child:
                    result.append(' ' * 4 * level + f'Node {level}: Interval = {entry.interval}')
                    queue.append((entry.child, level + 1))
                else:
                    result.append(' ' * 4 * level + f'Leaf {level + 1}: {entry.interval}')
        return result