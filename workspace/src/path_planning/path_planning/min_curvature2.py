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
    
    get_path(track, num_segments=args.segments, nodes_per_segment=args.nodes)


class Segment:
    """
    Creates a segment with left and right edges

    Attributes
    ----------
        left : WAVector
            point on left edge of segment
        right : WAVector
            point on right edge of segment
        x_dist : float
            difference between left and right x values
        y_dist : float
            difference between left and right y values
    """

    def __init__(self, track, index):
        self.left = track.left.calc_closest_point(wa.WAVector(track.center.get_points()[index].tolist()))
        self.right = track.right.calc_closest_point(wa.WAVector(track.center.get_points()[index].tolist()))

        self.x_dist = self.left.x - self.right.x
        self.y_dist = self.left.y - self.right.y


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
        segments.append(Segment(track, index))
    print("All nodes created")

    # -------------
    # Generate path
    # -------------

    curv = track.center.calc_curvature()

    points = []
    # for segment in segments:
    for i in range(0, len(segments)):
        alpha = (min(max(curv[i], -.05), .05) + .05) * 10
        # print(alpha)
        print(curv[i], alpha)
        point_x = segments[i].left.x + (segments[i].right.x - segments[i].left.x) * alpha
        point_y = segments[i].left.y + (segments[i].right.y - segments[i].left.y) * alpha
        points.append([point_x, point_y, 0])

    path = wa.WASplinePath(points, num_points=1000)

    # ------------
    # Plot results
    # ------------

    if args.plot:
        # 1
        fix, ax = plt.subplots()

        ax.axes.set_aspect('equal')
        for i in range(len(track.center.get_points())):
            if i % 50 == 0:
                ax.annotate(curv[i], (track.center.get_points()[i][0], track.center.get_points()[i][1]))
                ax.scatter(track.center.get_points()[i][0], track.center.get_points()[i][1], color='red')

        track.center.plot()

        # 2
        print("Plotting")
        plt.subplot(1, 2, 1) 
        plt.axis('equal')
        for i in range(num_segments):
            plt.plot([segments[i].left.x, segments[i].right.x], [segments[i].left.y, segments[i].right.y], 'r-')
        # plot selected points
        for point in points:
            plt.plot(point[0], point[1], "ro")
        track.left.plot("black", show=False)
        track.right.plot("black", show=False)
        path.plot("red", show=False)
        original_track.left.plot("black", show=False)
        original_track.right.plot("black", show=False)

        # 3 - final path
        plt.subplot(1, 2, 2) 
        plt.axis('equal')
        # plot
        path.plot("red", show=False)
        original_track.left.plot("black", show=False)
        original_track.right.plot("black")

    return path


if __name__ == "__main__":
    main()