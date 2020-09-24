from scipy.ndimage import map_coordinates
import numpy as np


def polar_to_cart(polar_data, theta_step, range_step, x, y, order=3):
    # "x" and "y" are numpy arrays with the desired cartesian coordinates
    # we make a meshgrid with them
    X, Y = np.meshgrid(x, y)
    # Now that we have the X and Y coordinates of each point in the output plane
    # we can calculate their corresponding theta and range
    Tc = np.degrees(np.arctan2(Y, X)).ravel()
    Rc = (np.sqrt(X**2 + Y**2)).ravel()
    # Negative angles are corrected
    Tc[Tc < 0] += 360
    # Using the known theta and range steps, the coordinates are mapped to
    # those of the data grid
    Tc = Tc / theta_step
    Rc = Rc / range_step
    # An array of polar coordinates is created stacking the previous arrays
    coords = np.vstack((Tc, Rc))
    # To avoid holes in the 360º - 0º boundary, the last column of the data
    # copied in the begining
    polar_data = np.vstack((polar_data, polar_data[-1,:]))
    # The data is mapped to the new coordinates
    # Values outside range are substituted with nans
    cart_data = map_coordinates(polar_data, coords, order=order, mode='constant', cval=np.nan)
    # The data is reshaped and returned
    return cart_data.reshape(len(y), len(x)).T


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    theta, r = np.meshgrid(np.linspace(0, 2 * np.pi, 100), np.linspace(0, 10, 100))
    data = np.sin(theta) * r**2

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')
    ax.pcolormesh(theta, r, data)

    x = y = np.linspace(-10, 10, 500)
    d2 = polar_to_cart(data.T, (theta[0, 1] - theta[0, 0])*180/np.pi, r[1, 0] - r[0, 0], x, y).T
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.pcolormesh(*np.meshgrid(x, y), d2)

    plt.show()
