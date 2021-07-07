"""Test sky subcommands."""

import uuid
from click.testing import CliRunner
from honeybee_radiance.cli.sunpath import sunpath_from_location, \
    sunpath_from_epw, parse_hours_from_suns
from honeybee_radiance.cli.util import get_hoys
import os


def test_get_hoys():
    output = [489, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590]
    hoys = get_hoys('JAN-01', '08:10', 'JAN-01', '09:50', 6, False)
    moy = [int(h * 60) for h in hoys]
    assert moy == output


def test_sunpath_climate_based():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_epw,
        [
            './tests/assets/epw/denver.epw', '--folder', folder,
            '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name', 'sunpath_cli_cb'
        ]
    )
    assert result.exit_code == 0


def test_sunpath():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_location,
        ['--lat', '39.76', '--lon', '-104.86', '--tz', '-7', '--folder', folder,
         '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name', 'sunpath_cli']
    )
    assert result.exit_code == 0


def test_sunpath_climate_based_reversed():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_epw,
        [
            './tests/assets/epw/denver.epw', '--folder', folder,
            '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name',
            'sunpath_cli_cb_r', '--reverse-vectors'
        ]
    )
    assert result.exit_code == 0


def test_sunpath_reversed():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_location,
        ['--lat', '39.76', '--lon', '-104.86', '--tz', '-7', '--folder', folder,
         '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name', 'sunpath_cli_r',
         '--reverse-vectors']
    )
    assert result.exit_code == 0


def test_sunpath_hours():
    name = str(uuid.uuid4()) + '.txt'
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        parse_hours_from_suns,
        ['./tests/assets/sun/suns.mod', '--folder', folder, '--name', name]
    )

    assert result.exit_code == 0
    # check the file is created
    assert os.path.isfile(os.path.join(folder, name))

    expected_results = [
        7, 8, 9, 10, 11, 12, 13, 14, 15, 31, 32, 33, 34, 35, 36, 37, 38, 39, 55, 56, 57,
        58, 59, 60, 61, 62, 63, 79, 80, 81, 82, 83, 84, 85, 86, 87, 103, 104, 105, 106,
        107, 108, 109, 110, 111, 112, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136,
        151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 175, 176, 177, 178, 179, 180,
        181, 182, 183, 184, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 223, 224,
        225, 226, 227, 228, 229, 230, 231, 232, 247, 248, 249, 250, 251, 252, 253, 254,
        255, 256, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 295, 296, 297, 298,
        299, 300, 301, 302, 303, 304, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328,
        343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 367, 368, 369, 370, 371, 372,
        373, 374, 375, 376, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 415, 416,
        417, 418, 419, 420, 421, 422, 423, 424, 439, 440, 441, 442, 443, 444, 445, 446,
        447, 448, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 487, 488, 489, 490,
        491, 492, 493, 494, 495, 496, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520,
        535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 559, 560, 561, 562, 563, 564,
        565, 566, 567, 568, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 607, 608,
        609, 610, 611, 612, 613, 614, 615, 616, 631, 632, 633, 634, 635, 636, 637, 638,
        639, 640, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 679, 680, 681, 682,
        683, 684, 685, 686, 687, 688, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712,
        727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 751, 752, 753, 754, 755, 756,
        757, 758, 759, 760, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 799, 800,
        801, 802, 803, 804, 805, 806, 807, 808, 823, 824, 825, 826, 827, 828, 829, 830,
        831, 832, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 871, 872, 873, 874,
        875, 876, 877, 878, 879, 880, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904,
        919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 943, 944, 945, 946, 947, 948,
        949, 950, 951, 952, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 991, 992,
        993, 994, 995, 996, 997, 998, 999, 1000
    ]

    with open(os.path.join(folder, name)) as inf:
        values = [int(float(i)) for i in inf]

    assert values == expected_results
