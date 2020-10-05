import os
import h5py
import json
import numpy as np

from teclab import utils

TEST = True

# set dataset directory
data_base_dir = "E:\\tec_data"
if TEST:
    data_base_dir = os.path.join(data_base_dir, 'test')
data_file_pattern = "{year:04d}_{month:02d}_tec.h5"
data_file_name = os.path.join(data_base_dir, data_file_pattern)
# get tree of possible maps
map_tree = utils.get_map_tree(data_base_dir)

grid_file = os.path.join(data_base_dir, "grid.h5")
with h5py.File(grid_file, 'r') as f:
    mlt_vals = f['mlt'][()]
    mlat_vals = f['mlat'][()]
theta_vals = np.pi * (mlt_vals - 6) / 12
radius_vals = 90 - mlat_vals
theta_grid, radius_grid = np.meshgrid(theta_vals, radius_vals)

done_list_file = os.path.join(data_base_dir, "labeled.json")
with open(done_list_file) as f:
    done_list = json.load(f)
if 'list' not in done_list:
    done_list = []
else:
    done_list = done_list['list']

unsure_list_file = os.path.join(data_base_dir, "unsure.json")
with open(unsure_list_file) as f:
    unsure_list = json.load(f)
if 'list' not in unsure_list:
    unsure_list = []
else:
    unsure_list = unsure_list['list']

cartesian_grid_size = (500, 500)


if __name__ == "__main__":
    year = 2012
    month = 6
    print(data_file_name.format(year=year, month=month))
