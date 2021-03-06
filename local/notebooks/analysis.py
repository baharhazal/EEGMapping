"""Analysis functions for EEGMapping project."""

import numpy as np
from scipy.stats import pearsonr, spearmanr, ttest_ind, sem

from plots import *
from utilities import *

###################################################################################################
###################################################################################################

def run_state_dict(datasets, label, mask, save_fig):
    """
    datasets: list of dict of 4d array
    """

    bands = datasets[0].keys()
    feats = ["CFS", "AMPS", "BWS"]

    corr_dicts = []

    for band in bands:

        curr_data = [dataset[band] for dataset in datasets]
        corr_dicts.append(run_state_array(curr_data, label + '_' + band, mask, feats, save_fig))

    return comb_dicts(corr_dicts)


def run_state_array(datasets, label, mask, feats, save_fig=True):
    """
    datasets: list of 4d array
    """

    state_ttest_dict = dict()

    for feat_in, feat in enumerate(feats):

        outputs = []
        for dataset in datasets:

            # Masking, if requested
            if np.any(mask):
                dataset = np.take(dataset, indices=mask, axis=2)

            # Data still 4D (not precombined across groups), then grab first block per subject
            if len(dataset.shape) == 4:
                dataset = dataset[:, 0, :, :]

            # Extract desired feature
            out_data = dataset[:, :, feat_in]
            outputs.append(out_data)

        name = label + "_" + feat
        state_ttest_dict[name] = ttest_ind(outputs[0], outputs[1])

        plot_comp(name, feat, outputs[0], outputs[1], save_fig=save_fig,
                  save_name=name + "_across_state")

    return state_ttest_dict


def make_topos_dict(datasets, label, eeg_dat_info, pos, save_fig=True):
    """
    datasets: list of dict of 4d arrays
    """

    bands = datasets[0].keys()
    feats = ["CFS", "AMPS", "BWS"]

    corr_dicts = []

    for band in bands:

        cur_data = [dataset[band] for dataset in datasets]
        corr_dicts.append(make_topos_array(cur_data, label + '_' + band,
                          eeg_dat_info, pos, feats, save_fig))

    space_corr_dict = comb_dicts(corr_dicts)

    return space_corr_dict


def make_topos_array(datasets, label, eeg_dat_info, pos, feats, save_fig=True):
    """
    datasets: list of 4d array
    """

    space_corr_dict = dict()

    for feat_in, feat in enumerate(feats):

        print('CURRENT FEATURE:', feat)

        topo_dat = np.zeros(shape=[2, 64])

        for ind, dataset in enumerate(datasets):
            topo_dat[ind, :] =  avg_for_topo(dataset, feat_in)

        # Calculate the average data across groups
        avg_dat = np.mean(topo_dat, 0)

        ## Plot topographies - within and across datasets
        plot_topo(topo_dat[0, :], title='D1' + label + feat, eeg_dat_info=eeg_dat_info, save_fig=save_fig)
        plot_topo(topo_dat[0, :], title='D2'+ label + feat, eeg_dat_info=eeg_dat_info, save_fig=save_fig)
        plot_topo(avg_dat, title='Both_' + label + feat, eeg_dat_info=eeg_dat_info, save_fig=save_fig)

        ## Plot scatter plots - across datasets for Ant-Pos & Med-Lat
        plot_space_scatter(avg_dat, abs(pos[:, 0]), 'Both_' + label + feat + "_medial_to_lateral_plot",
                           xlabel='Medial -> Lateral' , ylabel=feat, save_fig=save_fig)
        plot_space_scatter(avg_dat, pos[:, 1], 'Both_' + label + feat + "_posterior_to_anterior_plot",
                           xlabel='Posterior -> Anterior' , ylabel=feat, save_fig=save_fig)

        space_corr_dict['Both_' + label + '_' +  feat +'_' + "M_L"] = \
            pearsonr(abs(pos[:, 0]), np.nanmedian(topo_dat,0))
        space_corr_dict['Both_' + label + '_' +  feat + '_' + "P_A"] = \
            pearsonr(pos[:, 1], np.nanmedian(topo_dat,0))

    return space_corr_dict


def run_dict_across_blocks(label, dataset, ch_indices, save_figs):
    """
    label: str
    dataset: dict
    ch_indices: list of str
    save_figs: bool
    """

    bands = dataset.keys()
    feat_labels = ["CFS", "AMPS", "BWS"]

    time_corrs = []

    for band in bands:

        curr_data = dataset[band]
        time_corrs.append(run_array_across_blocks(label + '_' + band + '_', curr_data,
                                                  ch_indices, feat_labels=feat_labels, save_figs=save_figs))

    return comb_dicts(time_corrs)


def run_array_across_blocks(label, dataset, ch_indices, feat_labels, save_figs):
    """Run analysis of FOOOF features across blocks.

    label:
    dataset:
    ch_indices
    feat_labels:
    save_figs:
    """

    time_corr_dict = dict()

    for feat_in, feat in enumerate(feat_labels):

        dataset = demean(dataset)

        demeaned_curr_masked_data = np.take(dataset, indices=ch_indices,  axis=2)
        demeaned_curr_mean_data = np.nanmean(demeaned_curr_masked_data, axis=2)
        demeaned_curr_data_matrix = demeaned_curr_mean_data[:,:,feat_in]

        time_corr_dict[label + '_' + feat ] = pearsonr(range(0, demeaned_curr_data_matrix.shape[1]), np.nanmedian(demeaned_curr_data_matrix, 0))

        #avgs = np.nanmedian(demeaned_curr_data_matrix, axis=0)
        avgs = np.nanmean(demeaned_curr_data_matrix, axis=0)

        #yerrs = np.std(demeaned_curr_data_matrix, axis=0)
        yerrs = sem(demeaned_curr_data_matrix, axis=0)

        plot_across_blocks(avgs, yerrs, feat, label + "_" + feat + "_across_blocks_plot", save_figs)

    return time_corr_dict
