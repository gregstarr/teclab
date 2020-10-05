from scipy.ndimage import map_coordinates
import numpy as np
import glob
import datetime
import h5py
import os
import json


def get_map_tree(data_dir):
    """Search through dataset at location `data_dir` and get a tree structure which
    indicates what maps are in the dataset.

    year: [
        month:
            'index': [ind],
            'datetime': [dt]
    ]

    Parameters
    ----------
    data_dir: str

    Returns
    -------
    map_tree: dict
    """
    files = glob.glob(os.path.join(data_dir, "*tec.h5"))
    timestamps = []
    for file in files:
        with h5py.File(file, 'r') as f:
            timestamps.append(f['start_time'][()])
    timestamps = np.concatenate(timestamps)
    datetimes = np.array([datetime.datetime.utcfromtimestamp(ts) for ts in timestamps])
    years = np.array([dt.year for dt in datetimes])
    months = np.array([dt.month for dt in datetimes])
    tree = {}
    for yr in np.unique(years):
        for mn in range(1, 13):
            mask = (years == yr) * (months == mn)
            if mask.sum() == 0:
                continue
            if yr not in tree:
                tree[yr] = {}
            tree[yr][mn] = {}
            tree[yr][mn]['index'] = np.arange(mask.sum())
            tree[yr][mn]['datetime'] = datetimes[mask]
    return tree


def update_h5(current_map, new_labels):
    """Write `labels` to its corresponding h5 file.

    Parameters
    ----------
    current_map: dict
    new_labels: numpy.ndarray
    """
    with h5py.File(current_map['h5_file'], 'r+') as f:
        labels = f['labels'][()]
        labels[:, :, current_map['index']] = new_labels
        f['labels'][()] = labels


def update_done_list(fn, done_list: list, current_map):
    """If not unsure about the current map, add it to the done list and write the done list to its json file.

    Parameters
    ----------
    fn: str
    done_list: list
    current_map: dict
    """
    index_tuple = (int(current_map['year']), int(current_map['month']), int(current_map['index']))
    if not current_map['unsure'] and index_tuple not in done_list:
        done_list.append(index_tuple)
        with open(fn, 'w') as f:
            json.dump({'list': done_list}, f)


def update_unsure_list(fn, unsure_list: list, current_map):
    """Update `unsure_list` so that it agrees with `current_map`, then write the updated list to the
    `unsure_list` json.

    Parameters
    ----------
    fn: str
    unsure_list: list
    current_map: dict
    """
    index_tuple = (int(current_map['year']), int(current_map['month']), int(current_map['index']))
    if current_map['unsure'] and index_tuple not in unsure_list:
        unsure_list.append(index_tuple)
    elif not current_map['unsure'] and index_tuple in unsure_list:
        unsure_list.remove(index_tuple)

    with open(fn, 'w') as f:
        json.dump({'list': unsure_list}, f)


def open_map(current_map):
    index = current_map['index']
    with h5py.File(current_map['h5_file'], 'r') as f:
        tec = f['tec'][()]
        labels = f['labels'][()]
        start_time = f['start_time'][()]
    return tec[:, :, index], labels[:, :, index], start_time[index]


if __name__ == "__main__":
    pass
