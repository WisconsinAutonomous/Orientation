import wa_simulator as wa
import matplotlib.pyplot as plt
import math
import time


# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=False)
parser.add_argument("-p", "--plot", action="store_true", help="Plot results", default=False)
parser.add_argument("-s", "--segments", type=int, help="Number of segments", default=50)
parser.add_argument("-n", "--nodes", type=int, help="Number of nodes per segment", default=5)
args = parser.parse_args()


def main():
    """
    main method. sets up track 
    """
    # Load data points from a csv file
    wa.set_wa_data_directory('..')

    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",")

    # Create the path
    path = wa.WASplinePath(points, num_points=1000, is_closed=True)
    # Create the track with a constant width
    track = wa.create_constant_width_track(path, width=10)

    curv = track.center.calc_curvature()

    fix, ax = plt.subplots()

    ax.axes.set_aspect('equal')
    for i in range(len(track.center.get_points())):
        if i % 50 == 0:
            ax.annotate(curv[i], (track.center.get_points()[i][0], track.center.get_points()[i][1]))
            ax.scatter(track.center.get_points()[i][0], track.center.get_points()[i][1], color='red')
            print(curv[i])

    track.center.plot()
    
    get_path(track, num_segments=args.segments, nodes_per_segment=args.nodes)


class Node:
    """
    Represents a Node with x, y values and visited status
    Attributes
        x, y (float): the x and y values of the node's location
        edges (list): list of edges connected to the node
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


def create_segment(track, index, size):
    """
    Generate Node objects from left to right boundaries (CENTERLINE BASED)
    Args:
        track (WATrack): track to generate Nodes on
        index (int): index of point on center line
        size (int): number of Node objects on segment
    Returns:
        list : a list of Nodes along a segmentat
    """
    nodes = []

    center_point = wa.WAVector(track.center.get_points()[index].tolist())
    left = track.left.calc_closest_point(center_point)
    right = track.right.calc_closest_point(center_point)

    x_dist = left.x - right.x
    y_dist = left.y - right.y

    #left = outer border, right = inner
    for i in range(size):
        node_x = left.x - (x_dist / (size - 1)) * i
        node_y = left.y - (y_dist / (size - 1)) * i
        nodes.append(Node(node_x, node_y))

    return nodes


def get_path(track, num_segments=50, nodes_per_segment=5):
    """
    finds minimum curvature path on a given track
    Args:
        track (WATrack): track to find path on
        num_segments (int): number of segments
        nodes_per_segment (int): number of nodes per segment
    Returns:
        WASplinePath : Dijkstra's shortest path
    """
    original_track = track
    width = 7
    track = wa.create_constant_width_track(track.center, width=width)

    # ------------
    # Create nodes
    # ------------

    print("Creating node set...")

    segments = [] # array of segments throughout the track
    for i in range(num_segments):
        index = int(i*(len(track.center.get_points())/num_segments))
        segments.append(create_segment(track, index, nodes_per_segment))
        if args.plot:
            for j in range(nodes_per_segment):
                plt.scatter(segments[i][j].x, segments[i][j].y, color='blue')
    print("All nodes created")

    # --------------------
    # Shortest path search
    # --------------------

    # pick the point on the segment based off the curvature of the splines
    # possibly incorporate min distance also
    # print('here')
    # print(track.left.calc_curvature())  # keep track if the point idx and use that to get the curvature at each point
    # track.right.calc_curvature

    ## PLACEHOLDER

    points = []
    for segment in segments:
        points.append((segment[0].x, segment[0].y, 0))

    path = wa.WASplinePath(points, num_points=1000)

    # ------------
    # Plot results
    # ------------

    if args.plot:
        # 1 - all nodes
        print("Plotting nodes")
        plt.subplot(1, 2, 1) 
        plt.axis('equal')
        # plot nodes 
        for segment in segments:
            for node in segment: 
                plt.plot(node.x, node.y, "ko")
        # plot selected nodes
        for point in points:
            plt.plot(point[0], point[1], "ro")
        track.left.plot("black", show=False)
        track.right.plot("black", show=False)
        path.plot("red", show=False)
        original_track.left.plot("black", show=False)
        original_track.right.plot("black", show=False)

        # 2 - final path
        plt.subplot(1, 2, 2) 
        plt.axis('equal')
        # plot
        path.plot("red", show=False)
        original_track.left.plot("black", show=False)
        original_track.right.plot("black")

    return path


if __name__ == "__main__":
    main()