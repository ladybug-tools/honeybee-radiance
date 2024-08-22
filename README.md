# honeybee-radiance

![Honeybee](https://www.ladybug.tools/assets/img/honeybee.png)

[![Build Status](https://github.com/ladybug-tools/honeybee-radiance/workflows/CI/badge.svg)](https://github.com/ladybug-tools/honeybee-radiance/actions)
[![Coverage Status](https://coveralls.io/repos/github/ladybug-tools/honeybee-radiance/badge.svg?branch=master)](https://coveralls.io/github/ladybug-tools/honeybee-radiance)

[![Python 3.10](https://img.shields.io/badge/python-3.10-orange.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/)
[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

Radiance extension for honeybee.

Honeybee-radiance adds Radiance simulation functionalities to honeybee for daylight/radiation simulation.

## Installation

`pip install -U honeybee-radiance`

To check if the command line interface is installed correctly use `honeybee-radiance --help`.

## Documentation

[API documentation](https://www.ladybug.tools/honeybee-radiance/docs/)

## Local Development

1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/honeybee-radiance

# or

git clone https://github.com/ladybug-tools/honeybee-radiance
```
2. Install dependencies:
```console
cd honeybee-radiance
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./honeybee_radiance
sphinx-build -b html ./docs ./docs/_build/docs
```

