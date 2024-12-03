class Interval:
    def __init__(self, low, high):
        self.low = low
        self.high = high

    def __repr__(self):
        return f"[{self.low}, {self.high}]"



class Node:
    def __init__(self, median, intervals):
        self.median = median            # Median value for splitting
        self.intervals = intervals      # Overlapping intervals at this node
        self.left = None                # Left child
        self.right = None               # Right child

    def __str__(self):
        return f"Node(Median: {self.median}, Intervals: {self.intervals})"



class BalancedIntervalTree:
    def __init__(self, intervals):
        self.root = self.build_tree(intervals)

    def build_tree(self, intervals):
        if not intervals:
            return None

        # Collect all start and end points
        points = [point for interval in intervals for point in (interval.low, interval.high)]
        median = self.compute_median(points)

        # Split intervals into left, overlapping, and right
        left_intervals = []
        overlapping_intervals = []
        right_intervals = []

        for interval in intervals:
            if interval.high < median:
                left_intervals.append(interval)
            elif interval.low > median:
                right_intervals.append(interval)
            else:
                overlapping_intervals.append(interval)

        # Create node with overlapping intervals and store median
        node = Node(median, overlapping_intervals)

        # Safeguard against infinite recursion:
        # If no progress is made in splitting, stop recursion
        if len(overlapping_intervals) == len(intervals):
            return node

        # Recursively build left and right subtrees
        node.left = self.build_tree(left_intervals)
        node.right = self.build_tree(right_intervals)

        return node

    def compute_median(self, points):
        sorted_points = sorted(points)
        n = len(sorted_points)
        mid = n // 2
        if n == 0:
            return None
        if n % 2 == 0:
            return (sorted_points[mid - 1] + sorted_points[mid]) / 2
        else:
            return sorted_points[mid]

    def search(self, node, target_interval, result):
        if node is None:
            return

        # Check for overlap with the intervals at this node
        for interval in node.intervals:
            if interval.low <= target_interval.high and interval.high >= target_interval.low:
                result.append(interval)

        # Decide whether to search left subtree
        if node.left and target_interval.low <= node.median:
            self.search(node.left, target_interval, result)

        # Decide whether to search right subtree
        if node.right and target_interval.high >= node.median:
            self.search(node.right, target_interval, result)

    def query(self, target_interval):
        result = []
        self.search(self.root, target_interval, result)
        return result

    def print_tree(self, node=None, level=0, prefix="Root: "):
        if node is None:
            node = self.root

        indent = ' ' * (level * 4)
        print(f"{indent}{prefix}Median: {node.median}, Intervals: {node.intervals}")

        if node.left:
            self.print_tree(node.left, level + 1, prefix="L--- ")
        if node.right:
            self.print_tree(node.right, level + 1, prefix="R--- ")



# Example intervals
"""intervals = [
    Interval(1, 5),
    Interval(3, 7),
    Interval(4, 6),
    Interval(6, 10),
    Interval(8, 9),
    Interval(9, 11)
]

# Build the tree
tree = BalancedIntervalTree(intervals)

# Print the tree structure
tree.print_tree()

# Query the tree
#target = Interval(5, 8)
target = Interval(2, 6)
result = tree.query(target)
print(f"\nOverlapping intervals with {target}: {result}")"""
