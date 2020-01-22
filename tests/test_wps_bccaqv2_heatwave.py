from collections import deque
import tempfile
from unittest import mock

import pytest
from pathlib import Path
import xarray as xr

from finch.processes import BCCAQV2HeatWave
from finch.processes.wps_xclim_indices import make_nc_input
from finch.processes import utils
from tests.utils import wps_literal_input, execute_process


@mock.patch("finch.processes.bccaqv2.get_bccaqv2_opendap_datasets")
@mock.patch("finch.processes.wps_bccaqv2_heatwave.fix_broken_time_indices")
@mock.patch("finch.processes.wps_bccaqv2_heatwave.finch_subset_gridpoint")
@mock.patch("finch.processes.wps_bccaqv2_heatwave.compute_indices")
def test_bccaqv2_heatwave(
    mock_compute_indices, mock_bccaq_subset, mock_fix, mock_datasets, client
):
    identifier = "BCCAQv2_heat_wave_frequency_gridpoint"
    inputs = [
        wps_literal_input("output_format", "netcdf"),
        wps_literal_input("lat", "2"),
        wps_literal_input("lon", "3"),
        wps_literal_input("thresh_tasmin", "22.0 degC"),
        wps_literal_input("thresh_tasmax", "30 degC"),
        wps_literal_input("window", "3"),
        wps_literal_input("freq", "YS"),
    ]

    tmp = Path(__file__).parent / "tmp"
    tmp.mkdir(exist_ok=True)

    temp_file1 = tmp / "tasmin_some_file.nc"
    temp_file1.write_text("dummy data")
    temp_file2 = tmp / "tasmax_some_file.nc"
    temp_file2.write_text("dummy data")

    mock_datasets.return_value = ["dataset1", "dataset2"]
    mock_bccaq_subset.return_value = [temp_file1, temp_file2]
    mock_fix.side_effect = lambda *args: args

    def write_dummy_data(filename):
        Path(filename).write_text("dummy data")

    mock_computed = mock.MagicMock()
    mock_compute_indices.return_value = mock_computed
    mock_computed.to_netcdf.side_effect = write_dummy_data

    outputs = execute_process(client, identifier, inputs, output_names=["output"])

    output_file = outputs[0]
    assert len(outputs) == 1
    assert output_file.endswith("zip")
    assert Path(output_file).exists()

    assert len(mock_bccaq_subset.call_args[0][1]["resource"]) == 2


def test_bccaqv2_heat_wave_frequency_sample_data():
    here = Path(__file__).parent
    folder = here / "data" / "bccaqv2_single_cell"
    tasmin = list(sorted(folder.glob("tasmin*.nc")))[0]
    tasmax = list(sorted(folder.glob("tasmax*.nc")))[0]

    tasmin_input = make_nc_input("tasmin")
    tasmin_input.file = tasmin
    tasmax_input = make_nc_input("tasmax")
    tasmax_input.file = tasmax

    inputs = {
        "tasmin": deque([tasmin_input]),
        "tasmax": deque([tasmax_input]),
    }
    process = BCCAQV2HeatWave()
    process.workdir = tempfile.mkdtemp()
    out = utils.compute_indices(process, process.indices_process.xci, inputs)

    input_attrs = xr.open_dataset(tasmin).attrs
    del input_attrs["creation_date"]
    output_attrs = out.attrs
    del output_attrs["creation_date"]

    assert output_attrs == input_attrs


@pytest.mark.skip("Skipping: subset using real data is too long.")
def test_bccaqv2_heatwave_online(client):
    identifier = "BCCAQv2_heat_wave_frequency_gridpoint"
    up_right = 45.507485, -73.541295

    inputs = [
        wps_literal_input("output_format", "netcdf"),
        wps_literal_input("lat", str(up_right[0])),
        wps_literal_input("lon", str(up_right[1])),
        wps_literal_input("thresh_tasmin", "22.0 degC"),
        wps_literal_input("thresh_tasmax", "30 degC"),
        wps_literal_input("window", "3"),
        wps_literal_input("freq", "YS"),
    ]

    outputs = execute_process(client, identifier, inputs, output_names=["output"])

    print(outputs)
