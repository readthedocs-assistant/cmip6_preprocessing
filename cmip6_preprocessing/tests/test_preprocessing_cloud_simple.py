# This module tests data directly from the pangeo google cloud storage.
# Tests are meant to be more high level and also serve to document known problems (see skip statements).
import pytest
import xarray as xr
import numpy as np
from cmip6_preprocessing.tests.cloud_test_utils import (
    full_specs,
    xfail_wrapper,
    all_models,
    data,
    diagnose_doubles,
)
from cmip6_preprocessing.preprocessing import combined_preprocessing
from cmip6_preprocessing.grids import combine_staggered_grid

pytest.importorskip("gcsfs")

print(f"\n\n\n\n$$$$$$$ All available models: {all_models()}$$$$$$$\n\n\n\n")


# manually combine all pytest parameters, so that I have very fine grained control over
# which combination of parameters is expected to fail.


########################### Most basic test #########################
expected_failures = [
    ("AWI-ESM-1-1-LR", "thetao", "historical", "gn"),
    ("AWI-ESM-1-1-LR", "thetao", "ssp585", "gn"),
    ("AWI-CM-1-1-MR", "thetao", "historical", "gn"),
    ("AWI-CM-1-1-MR", "thetao", "ssp585", "gn"),
    # TODO: would be nice to have a "*" matching...
    ("CESM2-FV2", "thetao", "historical", "gn"),
    ("CESM2-FV2", "thetao", "ssp585", "gn"),
]


@pytest.mark.parametrize(
    "source_id,variable_id,experiment_id,grid_label",
    xfail_wrapper(full_specs(), expected_failures),
)
def test_check_dim_coord_values_wo_intake(
    source_id, variable_id, experiment_id, grid_label
):
    # there must be a better way to build this at the class level and then tear it down again
    # I can probably get this done with fixtures, but I dont know how atm
    ds, cat = data(source_id, variable_id, experiment_id, grid_label, False)

    if ds is None:
        pytest.skip(
            f"No data found for {source_id}|{variable_id}|{experiment_id}|{grid_label}"
        )

    ##### Check for dim duplicates
    # check all dims for duplicates
    # for di in ds.dims:
    # for now only test a subset of the dims. TODO: Add the bounds once they
    # are cleaned up.
    for di in ["x", "y", "lev", "time"]:
        if di in ds.dims:
            diagnose_doubles(ds[di].load().data)
            assert len(ds[di]) == len(np.unique(ds[di]))
            if di != "time":  # these tests do not make sense for decoded time
                assert ~np.all(np.isnan(ds[di]))
                assert np.all(ds[di].diff(di) >= 0)

    assert ds.lon.min().load() >= 0
    assert ds.lon.max().load() <= 360
    if "lon_bounds" in ds.variables:
        assert ds.lon_bounds.min().load() >= 0
        assert ds.lon_bounds.max().load() <= 360
    assert ds.lat.min().load() >= -90
    assert ds.lat.max().load() <= 90
    # make sure lon and lat are 2d
    assert len(ds.lon.shape) == 2
    assert len(ds.lat.shape) == 2


expected_failures = [
    ("AWI-ESM-1-1-LR", "thetao", "historical", "gn"),
    ("AWI-ESM-1-1-LR", "thetao", "ssp585", "gn"),
    ("AWI-CM-1-1-MR", "thetao", "historical", "gn"),
    ("AWI-CM-1-1-MR", "thetao", "ssp585", "gn"),
    # TODO: would be nice to have a "*" matching...
    ("CESM2-FV2", "thetao", "historical", "gn"),
    ("CESM2-FV2", "thetao", "ssp585", "gn"),
    (
        "IPSL-CM6A-LR",
        "thetao",
        "historical",
        "gn",
    ),  # IPSL has an issue with `lev` dims concatting
    ("IPSL-CM6A-LR", "o2", "historical", "gn"),
    ("NorESM2-MM", "thetao", "historical", "gn"),
]


@pytest.mark.parametrize(
    "source_id,variable_id,experiment_id,grid_label",
    xfail_wrapper(full_specs(), expected_failures),
)
def test_check_dim_coord_values(source_id, variable_id, experiment_id, grid_label):
    # there must be a better way to build this at the class level and then tear it down again
    # I can probably get this done with fixtures, but I dont know how atm
    ds, cat = data(source_id, variable_id, experiment_id, grid_label, True)

    if ds is None:
        pytest.skip(
            f"No data found for {source_id}|{variable_id}|{experiment_id}|{grid_label}"
        )

    ##### Check for dim duplicates
    # check all dims for duplicates
    # for di in ds.dims:
    # for now only test a subset of the dims. TODO: Add the bounds once they
    # are cleaned up.
    for di in ["x", "y", "lev", "time"]:
        if di in ds.dims:
            diagnose_doubles(ds[di].load().data)
            assert len(ds[di]) == len(np.unique(ds[di]))
            if di != "time":  # these tests do not make sense for decoded time
                assert ~np.all(np.isnan(ds[di]))
                assert np.all(ds[di].diff(di) >= 0)

    assert ds.lon.min().load() >= 0
    assert ds.lon.max().load() <= 360
    if "lon_bounds" in ds.variables:
        assert ds.lon_bounds.min().load() >= 0
        assert ds.lon_bounds.max().load() <= 360
    assert ds.lat.min().load() >= -90
    assert ds.lat.max().load() <= 90
    # make sure lon and lat are 2d
    assert len(ds.lon.shape) == 2
    assert len(ds.lat.shape) == 2
