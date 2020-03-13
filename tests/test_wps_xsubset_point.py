import pytest
from pywps import Service
from pywps.tests import assert_response_success, client_for
import xarray as xr

from finch.processes import SubsetGridPointProcess

from .common import CFG_FILE, get_metalinks, get_output


def test_wps_xsubsetpoint(netcdf_datasets):
    client = client_for(
        Service(processes=[SubsetGridPointProcess()], cfgfiles=CFG_FILE)
    )

    datainputs = (
        f"resource=files@xlink:href=file://{netcdf_datasets['tas']};"
        "lat=2.0;"
        "lon=3.0;"
        "start=2000;"
    )

    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=subset_gridpoint&datainputs={datainputs}"
    )

    assert_response_success(resp)
    out = get_output(resp.xml)
    ds = xr.open_dataset(out["output"][6:])
    assert ds.lat == 2
    assert ds.lon == 3


@pytest.mark.online
def test_thredds():
    import lxml.etree

    client = client_for(
        Service(processes=[SubsetGridPointProcess()], cfgfiles=CFG_FILE)
    )
    fn1 = (
        "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/dodsC/birdhouse/cmip5/MRI/rcp85/fx/atmos/r0i0p0/sftlf/"
        "sftlf_fx_MRI-CGCM3_rcp85_r0i0p0.nc"
    )
    fn2 = (
        "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/dodsC/birdhouse/cmip5/MRI/rcp85/fx/atmos/r0i0p0/orog/"
        "orog_fx_MRI-CGCM3_rcp85_r0i0p0.nc"
    )

    datainputs = (
        f"resource=files@xlink:href={fn1};"
        f"resource=files@xlink:href={fn2};"
        "lat=45.0;"
        "lon=150.0;"
    )

    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=subset_gridpoint&datainputs={datainputs}"
    )

    assert_response_success(resp)
    out = get_output(resp.xml)
    links = get_metalinks(lxml.etree.fromstring(out["ref"].encode()))
    assert len(links) == 2
