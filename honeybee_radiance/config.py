"""Honeybee_radiance configurations.

Import this into every module where access configurations are needed.

Usage:

.. code-block:: python

    from honeybee_radiance.config import folders
    print(folders.radiance_path)
    folders.radiance_path = "C:/Radiance/bin"
"""
import ladybug.config as lb_config
import honeybee_standards

import os
import platform
import subprocess
import json
import re


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
        * radiance_version
        * radiance_version_str
        * radiance_version_date
        * standards_data_folder
        * modifier_lib
        * modifierset_lib
        * defaults_file
        * config_file
        * mute
    """

    def __init__(self, config_file=None, mute=True):
        self.mute = bool(mute)  # set the mute value
        self.config_file = config_file  # load paths from the config JSON file

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
        if not r_path:  # check the default installation location
            r_path = self._find_radiance_folder()
        else:
            r_path = os.path.join(r_path, 'bin')
        rad_exe_file = os.path.join(r_path, exe_name) if r_path is not None else None

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
        self._radiance_version = None
        self._radiance_version_str = None
        self._radiance_version_date = None

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
    def radiance_version(self):
        """Get a tuple for the version of radiance (eg. (5, 3, '012cb17835')).

        This will be None if the version could not be sensed or if no Radiance
        installation was found.
        """
        if self._radbin_path and self._radiance_version_str is None:
            self._radiance_version_from_cli()
        return self._radiance_version

    @property
    def radiance_version_str(self):
        """Get text for the full version of radiance (eg."RADIANCE 5.3 official release").

        This will be None if the version could not be sensed or if no Radiance
        installation was found.
        """
        if self._radbin_path and self._radiance_version_str is None:
            self._radiance_version_from_cli()
        return self._radiance_version_str

    @property
    def radiance_version_date(self):
        """Get a tuple for the date of the radiance version (eg. (2020, 9, 3)).

        This will be None if the version could not be sensed or if no Radiance
        installation was found.
        """
        if self._radbin_path and self._radiance_version_str is None:
            self._radiance_version_from_cli()
        return self._radiance_version_date

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
        self._modifier_lib, self._modifierset_lib, self._defaults_file = \
            self._check_standards_folder(path)

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
    def defaults_file(self):
        """Get the path to the JSON file where honeybee's defaults are loaded from."""
        return self._defaults_file

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

    @property
    def env(self):
        "Return Radiance environment as a dictionary."
        env = {}
        if self.radbin_path:
            env['PATH'] = self.radbin_path.replace('\\', '/')
        if self.radlib_path:
            env['RAYPATH'] = self.radlib_path.replace('\\', '/')
        return env

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

    def _radiance_version_from_cli(self):
        """Get the Radiance version properties by making a call to a Radiance command."""
        rad_exe = os.path.join(self.radbin_path, 'mkpmap.exe') if os.name == 'nt' \
            else os.path.join(self.radbin_path, 'mkpmap')
        cmds = [rad_exe, '-version']
        use_shell = True if os.name == 'nt' else False
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
        stdout = process.communicate()
        base_str = str(stdout[0]).replace("b'", '').replace(r"\r\n'", '')
        self._radiance_version_str = base_str  # set the version string
        try:  # try to parse the version into a list of integers
            ver_nums = base_str.split('(')[-1].split(')')[0].split('.')
            ver_array = []
            for i in ver_nums:
                val = int(i) if i.isnumeric() else i
                ver_array.append(val)
            self._radiance_version = tuple(ver_array)
        except Exception:
            pass  # failed to parse the version into values; possibly a custom build
        try:  # try to parse the date into a list of integers
            date_pattern = re.compile(r'(\d*\-\d*\-\d*)')
            ver_date = re.search(date_pattern, base_str)
            self._radiance_version_date = \
                tuple(int(v) for v in ver_date.group(0).split('-'))
        except Exception:
            pass  # failed to parse the date into values; possibly a custom build

    @staticmethod
    def _find_radiance_folder():
        """Find the Radiance installation in its default location.

        This method will first attempt to return the path of a standalone Radiance
        installation and, if none are found, it will search for one that is
        installed with OpenStudio.

        Returns:
            File directory and full path to executable in case of success.
            None, None in case of failure.
        """
        # first check if there's a version installed in the ladybug_tools folder
        lb_install = lb_config.folders.ladybug_tools_folder
        rad_path = None
        if os.path.isdir(lb_install):
            test_path = os.path.join(lb_install, 'radiance')
            rad_path = test_path if os.path.isdir(test_path) else None

        # then check for the default location where standalone Radiance is installed
        if rad_path is not None:
            pass  # we found a version of radiance in the ladybug_tools folder
        elif os.name == 'nt':  # search the C:/ drive on Windows
            test_path = 'C:\\Radiance'
            rad_path = test_path if os.path.isdir(test_path) else None
        elif platform.system() == 'Darwin':  # search usr/local and Applications on Mac
            test_path = '/usr/local/radiance'
            rad_path = test_path if os.path.isdir(test_path) else None
            if rad_path is None:
                test_path = '/Applications/radiance'
                rad_path = test_path if os.path.isdir(test_path) else None
        elif platform.system() == 'Linux':  # search the usr/local folder
            test_path = '/usr/local/radiance'
            rad_path = test_path if os.path.isdir(test_path) else None

        if not rad_path:  # No Radiance installations were found
            return None

        # return the path to the executable
        rad_path = os.path.join(rad_path, 'bin')
        return rad_path

    @staticmethod
    def _find_standards_data_folder():
        """Find the the user template library in its default location.

        The ladybug_tools/resources/standards/honeybee_standards folder will be
        checked first, which can contain libraries that are not overwritten with
        the update of the honeybee_radiance package. If no such folder is found,
        this method defaults to the lib/library/ folder within this package.
        """
        # first check the ladybug_tools installation folder were permanent lib is
        lb_install = lb_config.folders.ladybug_tools_folder
        if os.path.isdir(lb_install):
            lib_folder = os.path.join(
                lb_install, 'resources', 'standards', 'honeybee_standards')
            if os.path.isdir(lib_folder):
                return lib_folder

        # default to the library folder that installs with this Python package
        return os.path.join(os.path.dirname(honeybee_standards.__file__))

    @staticmethod
    def _check_standards_folder(path):
        """Check that a standards data sub-folders exist."""
        if not path:  # first check that a path exists
            return [None] * 3

        # gather all of the sub folders underneath the master folder
        _modifier_lib = os.path.join(path, 'modifiers') if path else None
        _modifierset_lib = os.path.join(path, 'modifiersets') if path else None
        _radiance_default = os.path.join(path, 'radiance_default.json')

        assert os.path.isdir(_modifier_lib), \
            '{} lacks a "modifiers" folder.'.format(path)
        assert os.path.isdir(_modifierset_lib), \
            '{} lacks a "modifiersets" folder.'.format(path)
        assert os.path.isfile(_radiance_default), \
            '{} lacks a "radiance_default.json."'.format(path)

        return _modifier_lib, _modifierset_lib, _radiance_default


"""Object possesing all key folders within the configuration."""
folders = Folders(mute=True)
