import wa_simulator as wa
import matplotlib.pyplot as plt
import math
import time


# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=False)
parser.add_argument("-s", "--segments", type=int, help="Number of segments", default=50)
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
    
    get_path(track, num_segments=args.segments)


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


def get_path(track, num_segments=50):
    """
    finds minimum curvature path on a given track
    Args:
        track (WATrack): track to find path on
        num_segments (int): number of segments
    Returns:
        WASplinePath : Dijkstra's shortest path
    """
    original_track = track
    width = 7
    track = wa.create_constant_width_track(track.center, width=width)

    # ------------
    # Create segments
    # ------------

    # print("Creating segments...")

    segments = [] # array of segments throughout the track
    for i in range(num_segments):
        idx = int(1000*i/num_segments)
        segments.append(Segment(track, idx))
    # print("All nodes created")

    # -------------
    # Generate path
    # -------------

    curv = track.center.calc_curvature()
    min_curv = min(curv)
    max_curv = max(curv)

    points = []
    alphas = []
    # for segment in segments:
    for i in range(0, num_segments):
        idx = int(len(curv)*i/num_segments)
        # shift curvature + scale up to get alpha
        alphas.append((curv[idx] + abs(min_curv)) / (abs(max_curv) + abs(min_curv)))
        # print(alpha)
        print(curv[idx], alphas[i])
        point_x = segments[i].right.x + (segments[i].left.x - segments[i].right.x) * alphas[i]
        point_y = segments[i].right.y + (segments[i].left.y - segments[i].right.y) * alphas[i]
        points.append([point_x, point_y, 0])

    path = wa.WASplinePath(points, num_points=1000)

    # ------------
    # Plot results
    # ------------

    # 1
    plt.axis('equal')
    for i in range(len(track.center.get_points())):
        if i % 50 == 0:
            plt.annotate(curv[i], (track.center.get_points()[i][0], track.center.get_points()[i][1]))
            plt.scatter(track.center.get_points()[i][0], track.center.get_points()[i][1], color='red')
    track.center.plot()

    # 2
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

    # data
    num_points = len(path.get_points())
    plt.plot(range(num_points), path.calc_curvature(), label="path curvature")
    plt.plot(range(num_points), track.center.calc_curvature(), label="track curvature")
    plt.plot(range(0, num_points, int(num_points/num_segments)), alphas, label="alphas")
    plt.legend()
    plt.show()

    return path


if __name__ == "__main__":
    main()