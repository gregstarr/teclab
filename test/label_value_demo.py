import numpy as np
import h5py
import matplotlib.pyplot as plt
import os
from skimage.util import view_as_windows, pad

from teclab import config


yr = config.done_list[0][0]
month = config.done_list[0][1]
with h5py.File(os.path.join(config.data_file_name.format(year=yr, month=month)), 'r') as f:
    tec = f['tec'][()]
    labels = f['labels'][()]

ind = [i[2] for i in config.done_list]
i = ind[0]
x = tec[:, :, i]
y = labels[:, :, i]

# find min lat
avg_size = 7
patches = view_as_windows(pad(x, (avg_size - 1)//2, mode='wrap'), (avg_size, avg_size)).reshape(x.shape[:2] + (-1,))
x_maxed = np.nanmean(patches, axis=-1)
x_maxed[~y] = np.inf
min_lat = 90 - config.radius_vals[np.argmin(x_maxed, axis=0)]
min_tec = np.nanmin(x_maxed, axis=0)
mask = np.isfinite(min_tec)

# poleward wall
idx = np.argmax(y, axis=0)
pwall_lat = 90 - config.radius_vals[idx]
pwall_tec = x[idx, np.arange(idx.shape[0])]

# equatorward wall
idx = np.argmax(y[::-1], axis=0)
ewall_lat = 30 + config.radius_vals[idx]
ewall_tec = x[::-1][idx, np.arange(idx.shape[0])]

# width

# length?

# depth

# gradients?

# total depletion?

fig = plt.figure()

ax1 = fig.add_subplot(121, projection='polar')
ax1.pcolormesh(config.theta_grid, config.radius_grid, x, vmin=0, vmax=10)
# ax1.plot(config.theta_vals[mask], 90 - pwall_lat[mask], 'b.')
# ax1.plot(config.theta_vals[mask], 90 - ewall_lat[mask], 'b.')
ax1.plot(config.theta_vals[mask], 90 - min_lat[mask], 'r.')
ax1.grid()

ax2 = fig.add_subplot(122, projection='polar')
ax2.pcolormesh(config.theta_grid, config.radius_grid, y)
ax2.grid()

plt.show()