# -*- coding: utf-8 -*-
# Copyright (C) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE for more info.
import json

import pytest

from wetterdienst.provider.dwd.observation import (
    DwdObservationDataset,
    DwdObservationPeriod,
    DwdObservationRequest,
    DwdObservationResolution,
)


def test_dwd_observation_metadata_discover_parameters():
    metadata = DwdObservationRequest.discover(resolution="minute_1", flatten=True)
    expected = {
        "minute_1": {
            "precipitation_height": {"origin": "mm", "si": "kg / m ** 2"},
            "precipitation_height_droplet": {
                "origin": "mm",
                "si": "kg / m ** 2",
            },
            "precipitation_height_rocker": {
                "origin": "mm",
                "si": "kg / m ** 2",
            },
            "precipitation_index": {"origin": "-", "si": "-"},
        }
    }
    assert json.dumps(expected) in json.dumps(metadata)


@pytest.mark.xfail
@pytest.mark.remote
def test_dwd_observation_metadata_describe_fields_kl_daily_english():
    metadata = DwdObservationRequest.describe_fields(
        dataset=DwdObservationDataset.CLIMATE_SUMMARY,
        resolution=DwdObservationResolution.DAILY,
        period=DwdObservationPeriod.RECENT,
    )
    assert list(metadata.keys()) == [
        "parameters",
        "quality_information",
    ]
    assert list(metadata["parameters"].keys()) == [
        "stations_id",
        "mess_datum",
        "qn_3",
        "fx",
        "fm",
        "qn_4",
        "rsk",
        "rskf",
        "sdk",
        "shk_tag",
        "nm",
        "vpm",
        "pm",
        "tmk",
        "upm",
        "txk",
        "tnk",
        "tgk",
    ]


@pytest.mark.xfail
@pytest.mark.remote
def test_dwd_observation_metadata_describe_fields_kl_daily_german():
    metadata = DwdObservationRequest.describe_fields(
        dataset=DwdObservationDataset.CLIMATE_SUMMARY,
        resolution=DwdObservationResolution.DAILY,
        period=DwdObservationPeriod.RECENT,
    )
    assert list(metadata.keys()) == [
        "parameters",
        "quality_information",
    ]
    assert list(
        DwdObservationRequest.describe_fields(
            dataset=DwdObservationDataset.CLIMATE_SUMMARY,
            resolution=DwdObservationResolution.DAILY,
            period=DwdObservationPeriod.RECENT,
            language="de",
        )["parameters"].keys()
    ) == [
        "stations_id",
        "mess_datum",
        "qn_3",
        "fx",
        "fm",
        "qn_4",
        "rsk",
        "rskf",
        "sdk",
        "shk_tag",
        "nm",
        "vpm",
        "pm",
        "tmk",
        "upm",
        "txk",
        "tnk",
        "tgk",
    ]


@pytest.mark.xfail
@pytest.mark.remote
def test_dwd_observation_metadata_describe_fields_solar_hourly():
    metadata = DwdObservationRequest.describe_fields(
        dataset=DwdObservationDataset.SOLAR,
        resolution=DwdObservationResolution.HOURLY,
        period=DwdObservationPeriod.RECENT,
        language="en",
    )

    assert list(metadata.keys()) == [
        "parameters",
        "quality_information",
    ]

    assert list(metadata["parameters"].keys()) == [
        "stations_id",
        "mess_datum",
        "qn_592",
        "atmo_strahl",
        "fd_strahl",
        "fg_strahl",
        "sd_strahl",
        "zenith",
    ]


@pytest.mark.xfail
@pytest.mark.remote
def test_dwd_observation_metadata_describe_fields_temperature_10minutes():
    metadata = DwdObservationRequest.describe_fields(
        dataset=DwdObservationDataset.TEMPERATURE_AIR,
        resolution=DwdObservationResolution.MINUTE_10,
        period=DwdObservationPeriod.RECENT,
    )

    assert list(metadata.keys()) == [
        "parameters",
        "quality_information",
    ]

    assert list(metadata["parameters"].keys()) == [
        "stations_id",
        "mess_datum",
        "qn",
        "pp_10",
        "tt_10",
        "tm5_10",
        "rf_10",
        "td_10",
    ]
