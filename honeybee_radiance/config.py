"""Honeybee_radiance configurations.

Import this into every module where access configurations are needed.

Usage:

.. code-block:: python

    from honeybee_radiance.config import folders
    print(folders.radiance_path)
    folders.radiance_path = "C:/Radiance/bin"
"""
import honeybee.config as hb_config

import os
import platform
import json


class Folders(object):
    """Honeybee_radiance folders.

    Args:
        config_file: The path to the config.json file from which folders are loaded.
            If None, the config.json module included in this package will be used.
            Default: None.
        mute: If False, the paths to the various folders will be printed as they
            are found. If True, no printing will occur upon initialization of this
            class. Default: True.

    Properties:
        * radiance_path
        * radbin_path
        * radlib_path
        * standards_data_folder
        * modifier_lib
        * modifierset_lib
        * config_file
        * mute
    """

    def __init__(self, config_file=None, mute=True):
        # set the mute value
        self.mute = bool(mute)

        # load paths from the config JSON file 
        self.config_file  = config_file

    @property
    def radiance_path(self):
        """Get or set the path to Radiance installation folder.
        
        This is the top level folder that contains both the "bin" and the "lib"
        directories.
        """
        return self._radiance_path
    
    @radiance_path.setter
    def radiance_path(self, r_path):
        exe_name = 'rad.exe' if os.name == 'nt' else 'rad'
        if not r_path:  # check the PATH and then the default installation locations
            r_path, rad_exe_file = self._which(exe_name)
            if r_path is None:  # search within the default installation locations
                r_path, rad_exe_file = self._find_radiance_folder()
        else:
            r_path = os.path.join(r_path, 'bin')
            rad_exe_file = os.path.join(r_path, exe_name)

        if r_path:  # check that the Radiance executable exists in the installation
            assert os.path.isfile(rad_exe_file), \
                '{} is not a valid path to a Radiance installation.'.format(r_path)

        # set the radiance_path
        self._radbin_path = r_path
        if r_path:
            self._radiance_path = os.path.split(r_path)[0]
            self._radlib_path = os.path.join(self._radiance_path, 'lib')
            if not self.mute:
                print("Path to Radiance is set to: %s" % self._radiance_path)
        else:
            self._radiance_path = None
            self._radlib_path = None

    @property
    def radbin_path(self):
        """Get the path to Radiance bin folder.
        
        This is the "bin" directory for Radiance installation (the one that
        contains the executable files).
        """
        return self._radbin_path

    @property
    def radlib_path(self):
        """Get the path to Radiance lib folder."""
        return self._radlib_path

    @property
    def standards_data_folder(self):
        """Get or set the path to the folder standards loaded to honeybee_radiance.lib.
        
        This folder must have the following sub-folders in order to be valid:
            * modifiers - folder with RAD files for modifiers.
            * modifiersets - folder with JSON files of abridged ModifierSets.
        """
        return self._standards_data_folder
    
    @standards_data_folder.setter
    def standards_data_folder(self, path):
        if not path:  # check the default locations of the template library
            path = self._find_standards_data_folder()
        
        # gather all of the sub folders underneath the master folder
        self._modifier_lib = os.path.join(path, 'modifiers') if path else None
        self._modifierset_lib = os.path.join(path, 'modifiersets') if path else None

        # check that the library's sub-folders exist
        if path:
            assert os.path.isdir(self._modifier_lib), \
                '{} lacks a "modifiers" folder.'.format(path)
            assert os.path.isdir(self._modifierset_lib), \
                '{} lacks a "modifiersets" folder.'.format(path)

        # set the standards_data_folder
        self._standards_data_folder = path
        if path and not self.mute:
            print('Path to the standards_data_folder is set to: '
                    '{}'.format(self._standards_data_folder))

    @property
    def modifier_lib(self):
        """Get the path to the modifier library in the standards_data_folder."""
        return self._modifier_lib
    
    @property
    def modifierset_lib(self):
        """Get the path to the modifierset library in the standards_data_folder."""
        return self._modifierset_lib

    @property 
    def config_file(self):
        """Get or set the path to the config.json file from which folders are loaded.
        
        Setting this to None will result in using the config.json module included
        in this package.
        """
        return self._config_file

    @config_file.setter
    def config_file(self, cfg):
        if cfg is None:
            cfg = os.path.join(os.path.dirname(__file__), 'config.json')
        self._load_from_file(cfg)
        self._config_file = cfg

    def _load_from_file(self, file_path):
        """Set all of the the properties of this object from a config JSON file.
        
        Args:
            file_path: Path to a JSON file containing the file paths. A sample of this
                JSON is the config.json file within this package.
        """
        # check the default file path
        assert os.path.isfile(str(file_path)), \
            ValueError('No file found at {}'.format(file_path))

        # set the default paths to be all blank
        default_path = {
            "radiance_path": r'',
            "standards_data_folder": r''
        }

        with open(file_path, 'r') as cfg:
            try:
                paths = json.load(cfg)
            except Exception as e:
                print('Failed to load paths from {}.\n{}'.format(file_path, e))
            else:
                for key, p in paths.items():
                    if not key.startswith('__') and p.strip():
                        default_path[key] = p.strip()

        # set path for radiance installations
        self.radiance_path = default_path["radiance_path"]

        # set path for the standards_data_folder
        self.standards_data_folder = default_path["standards_data_folder"]

    def _find_radiance_folder(self):
        """Find the Radiance installation in its default location.
        
        This method will first attempt to return the path of a standalone Radiance
        installation and, if none are found, it will search for one that is
        installed with OpenStudio.

        Returns:
            File directory and full path to executable in case of success.
            None, None in case of failure.
        """
        # first check for the default location where standalone Radiance is installed
        rad_path = None
        if os.name == 'nt':  # search the C:/ drive on Windows
            for f in os.listdir('C:\\'):
                if f.lower() == 'radiance' and os.path.isdir('C:\\{}'.format(f)):
                    rad_path = 'C:\\{}'.format(f)
                    break
        elif platform.system() == 'Darwin':  # search the Applications folder on Mac
            for f in os.listdir('/Applications/'):
                if f.lower() == 'radiance' and os.path.isdir('/Applications/{}'.format(f)):
                    rad_path = '/Applications/{}'.format(f)
                    break
        elif platform.system() == 'Linux':  # search the usr/local folder
            for f in os.listdir('/usr/local/'):
                if f.lower() == 'radiance' and os.path.isdir('/usr/local/{}'.format(f)):
                    rad_path = '/usr/local/{}'.format(f)
                    break

        if not rad_path:  # then check the Radiance that comes with OpenStudio
            os_path = self._find_openstudio_folder()
            if os_path and os.path.isdir(os.path.join(os_path, 'Radiance')):
                rad_path = os.path.join(os_path, 'Radiance')

        if not rad_path:  # No Radiance installations were found
            return None, None

        # return the path to the executable
        rad_path = os.path.join(rad_path, 'bin')
        exec_file = os.path.join(rad_path, 'rad.exe') if os.name == 'nt' \
            else os.path.join(rad_path, 'rad')
        return rad_path, exec_file

    @staticmethod
    def _find_openstudio_folder():
        """Find the most recent OpenStudio installation in its default location.

        Returns:
            File directory and full path to executable in case of success.
            None, None in case of failure.
        """
        def getversion(openstudio_path):
            """Get digits for the version of OpenStudio."""
            ver = ''.join(s for s in openstudio_path if (s.isdigit() or s == '.'))
            return sum(int(d) * (10 ** i) for i, d in enumerate(reversed(ver.split('.'))))

        if os.name == 'nt':  # search the C:/ drive on Windows
            os_folders = ['C:\\{}'.format(f) for f in os.listdir('C:\\')
                          if (f.lower().startswith('openstudio') and
                              os.path.isdir('C:\\{}'.format(f)))]
        elif platform.system() == 'Darwin':  # search the Applications folder on Mac
            os_folders = ['/Applications/{}'.format(f) for f in os.listdir('/Applications/')
                          if (f.lower().startswith('openstudio') and
                              os.path.isdir('/Applications/{}'.format(f)))]
        elif platform.system() == 'Linux':  # search the usr/local folder
            os_folders = ['/usr/local/{}'.format(f) for f in os.listdir('/usr/local/')
                          if (f.lower().startswith('openstudio') and
                              os.path.isdir('/usr/local/{}'.format(f)))]
        else:  # unknown operating system
            os_folders = None
        
        if not os_folders:  # No Openstudio installations were found
            return None
        
        # get the most recent version of OpenStudio that was found
        return sorted(os_folders, key=getversion, reverse=True)[0]

    @staticmethod
    def _find_standards_data_folder():
        """Find the the user template library in its default location.
        
        The HOME/honeybee/honeybee_standards/data folder will be checked first,
        which can conatain libraries that are not overwritten with the update of the
        honeybee_energy package. If no such folder is found, this method defaults to
        the lib/library/ folder within this package.
        """
        # first check the default sim folder folder, where permanent libraries live
        home_folder = os.getenv('HOME') or os.path.expanduser('~')
        lib_folder = os.path.join(home_folder, 'honeybee', 'honeybee_standards', 'data')
        if os.path.isdir(lib_folder):
            return lib_folder
        else:  # default to the library folder that installs with this Python package
            return os.path.join(os.path.dirname(__file__), 'lib', 'data')

    @staticmethod
    def _which(program):
        """Find an executable program in the PATH by name.

        Args:
            program: Full file name for the program (e.g. energyplus.exe)

        Returns:
            File directory and full path to program in case of success.
            None, None in case of failure.
        """
        def is_exe(fpath):
            # Return true if the file exists and is executable
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        # check for the file in all path in environment
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path.strip('"'), program)  # strip "" in Windows
            if is_exe(exe_file):
                return path, exe_file

        # couldn't find it in the PATH! return None :|
        return None, None


"""Object possesing all key folders within the configuration."""
folders = Folders(mute=True)
