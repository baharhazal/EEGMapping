"""Analysis functions for EEGMapping project."""

import numpy as np
from scipy.stats import pearsonr

from plots import *
from utilities import *

###################################################################################################
###################################################################################################

def make_topos_dict(datasets, label, eeg_dat_info, pos, SAVE_FIGS=True):
    """
    datasets: list of dict of 4d arrays
    """

    bands = datasets.keys()
    feats = ["CFS", "AMPS", "BWS"]

    corr_dicts = []

    for band in bands:

        cur_data = [dataset[band] for dataset in datasets]
        corr_dicts.append(make_topos_array(cur_data, label + '_' + band,
                          eeg_dat_info, pos, feats, SAVE_FIGS))

    space_corr_dict = {key: val for dd in corr_dicts for key, val in dd.items()}

    return space_corr_dict


def make_topos_array(datasets, label, eeg_dat_info, pos, feats, SAVE_FIGS=True):
    """
    datasets: list of 4d array
    """

    space_corr_dict = dict()

    for feat_in, feat in enumerate(feats):

        topo_dat = np.zeros(shape=[2, 64])

        for ind, dataset in enumerate(datasets):
            topo_dat[ind, :] =  avg_for_topo(dataset, feat_in)

        # Calculate the average data across groups
        avg_dat = np.mean(topo_dat, 0)

        ## Plot topographies - within and across datasets
        plot_topo(topo_dat[0, :], title='D1' + label + feat, eeg_dat_info=eeg_dat_info)
        plot_topo(topo_dat[0, :], title='D2'+ label + feat, eeg_dat_info=eeg_dat_info)
        plot_topo(avg_dat, title='Both_' + label +feat, eeg_dat_info=eeg_dat_info)

        ## Plot scatter plots - across datasets for Ant-Pos & Med-Lat
        plot_space_scatter(avg_dat, pos[:, 0], 'Both_' + label + feat + "_medial_to_anterior_plot")
        plot_space_scatter(avg_dat, pos[:, 1], 'Both_' + label + feat + "_posterior_to_anterior_plot")

        space_corr_dict['Both_' + state + '_' + band + '_' +  feat +'_' + "M_L"] = \
            pearsonr(abs(pos[:, 0]), np.nanmedian(topo_dat,0))
        space_corr_dict['Both_' + state + '_' + band + '_' +  feat + '_' + "P_A"] = \
            pearsonr(pos[:, 1], np.nanmedian(topo_dat,0))

        return space_corr_dict


def run_dict_across_blocks(label, dataset, ch_indices, SAVE_FIGS):
    """
    label: str
    dataset: dict
    ch_indices: list of str
    SAVE_FIGS: bool
    """

    bands = dataset.keys()
    feat_labels = ["CFS", "AMPS", "BWS"]

    for band in bands:

        curr_data = dataset[band]
        run_array_across_blocks(label + '_' + band + '_', curr_data, ch_indices, feat_labels=feat_labels, SAVE_FIGS=SAVE_FIGS)


def run_array_across_blocks(label, dataset, ch_indices, feat_labels, SAVE_FIGS):
    """Run analysis of FOOOF features across blocks.

    label:
    dataset:
    ch_indices
    feat_labels:
    SAVE_FIGS:
    """

    for feat_in, feat in enumerate(feat_labels):

        dataset = demean(dataset)

        demeaned_curr_masked_data = np.take(dataset, indices=ch_indices,  axis=2)
        demeaned_curr_mean_data = np.nanmean(demeaned_curr_masked_data, axis=2)
        demeaned_curr_data_matrix = demeaned_curr_mean_data[:,:,feat_in]

        time_corr_dict[label + '_' + feat ] = pearsonr(range(0, demeaned_curr_data_matrix.shape[1]), np.nanmedian(demeaned_curr_data_matrix, 0))

        means = np.nanmean(demeaned_curr_data_matrix, axis=0)
        stds = np.std(demeaned_curr_data_matrix, axis=0)

        plot_across_blocks(means, stds, label + "_" + feat + "_across_blocks_plot")