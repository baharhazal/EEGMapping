"""Database related organization and utilities for slope fitting project."""

import os

####################################################################################################
####################################################################################################

class EEGDB(object):
    """Class to hold database information for slope fitting project.

    Attributes
    ----------
    project_path : str
        Base path for the project.
    data_path : str
        Path to all data.
    subjs_path : str
        Path to EEG subjects data.
    syns_path : str
    	Path to synthetic-fitting data.
    """

    def __init__(self, gen_paths=True):
        """Initialize SLFDB object."""

        # Set base path for project
        self.project_path = ("/Users/tom/Documents/Research/1-Projects/EEGMapping/")

        # Initialize paths
        self.data_path = str()
        self.subjs_path = str()
        self.psd_path = str()
        self.fooof_path = str()

        # Generate project paths
        if gen_paths:
            self.gen_paths()


    def gen_paths(self):
        """Generate paths."""

        self.data_path = os.path.join(self.project_path, '2-Data/childmind')
        self.subjs_path = os.path.join(self.data_path, 'EEG', 'Subjs')
        self.syns_path = os.path.join(self.data_path, 'syns')
        self.psd_path = os.path.join(self.data_path, 'psds')
        self.fooof_path = os.path.join(self.data_path, 'fooof')


    def check_subjs(self):
        """Check which subjects are avaiable in database."""

        subjs = _clean_files(os.listdir(self.subjs_path))

        return subjs


    def check_psd(self):
        """Get the available PSD files."""

        psd_files = _clean_files(os.listdir(self.psd_path))

        return psd_files


    def check_fooof(self):
        """Check which synthetic-fitting files are available in the database."""

        fooof_files = _clean_files(os.listdir(self.fooof_path))

        return fooof_files


    def get_subj_files(self, subj_number):
        """Get the preprocessed, EEG data file names (csv format) a specified subject."""

        dat_dir = os.path.join(self.subjs_path, subj_number,
                               'EEG', 'preprocessed', 'csv_format')
        files = os.listdir(dat_dir)

        eeg = [fi for fi in files if 'events' not in fi and 'channels' not in fi]
        evs = [fi for fi in files if 'events' in fi]
        chs = [fi for fi in files if 'channels' in fi]

        # Quick hack to ignore subjs with problematic files
        if not len(eeg) == len(evs) == len(chs):
            print('Oh Shit. Something seems to have gone wrong.')
            return None, None, None

        return eeg, evs, chs


    def get_psd_subjs(self):
        """Get a list of subject number for whom PSDs are calculated."""

        psd_files = self.check_psd()

        return [fi.split('_')[0] for fi in psd_files]


    def get_fooof_subjs(self):
        """Get a list of subject number for whom FOOOF results are calculated."""

        fooof_files = self.check_fooof()

        return [fi.split('_')[0] for fi in fooof_files]


    def gen_dat_path(self, subj_number, dat_file):
        """Generate full file path to a data file."""

        return os.path.join(self.subjs_path, subj_number,
                            'EEG', 'preprocessed', 'csv_format',
                            dat_file)

####################################################################################################
####################################################################################################

def _clean_files(files):
    """Clean a list of files, removing any hidden files."""

    return list(filter(lambda x: x[0] != '.', files))
