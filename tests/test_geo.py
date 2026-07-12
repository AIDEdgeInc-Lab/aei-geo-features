import pandas as pd
import pytest

from aei_geo_features.errors import (
    InvalidCoordinateError,
    LandmarkNotFoundError,
    MissingColumnError,
    UnsupportedUnitError,
)
from aei_geo_features.geo import (
    add_distance_to_landmark,
    add_location_jitter,
    haversine_distance,
    normalize_coordinates,
    validate_coordinate,
    validate_dataframe,
)


def test_haversine_valid_distance():
    dist = haversine_distance(43.6426, -79.3871, 48.8584, 2.2945)
    assert abs(dist - 5997.88) < 1.0


def test_haversine_invalid_coordinates_raises_canonical_error():
    with pytest.raises(InvalidCoordinateError):
        haversine_distance(100.0, -79.3871, 48.8584, 2.2945)


def test_haversine_unsupported_unit():
    with pytest.raises(UnsupportedUnitError):
        haversine_distance(43.6426, -79.3871, 43.6532, -79.3832, unit="m")


def test_haversine_unit_conversion():
    km = haversine_distance(43.6426, -79.3871, 43.6532, -79.3832, unit="km")
    mi = haversine_distance(43.6426, -79.3871, 43.6532, -79.3832, unit="mi")
    assert abs(km * 0.621371 - mi) < 0.001


def test_haversine_same_point_is_zero():
    assert haversine_distance(43.6426, -79.3871, 43.6426, -79.3871) == 0.0


def test_haversine_non_numeric_raises():
    with pytest.raises(InvalidCoordinateError):
        haversine_distance("a", -79.3871, 48.8584, 2.2945)


def test_validate_coordinate_valid_returns_true():
    assert validate_coordinate(43.6426, -79.3871) is True


def test_validate_coordinate_invalid_latitude_raises():
    with pytest.raises(InvalidCoordinateError):
        validate_coordinate(91.0, 0.0)


def test_validate_coordinate_invalid_longitude_raises():
    with pytest.raises(InvalidCoordinateError):
        validate_coordinate(0.0, 181.0)


def test_validate_coordinate_boundary_values_are_valid():
    assert validate_coordinate(90.0, 180.0) is True
    assert validate_coordinate(-90.0, -180.0) is True


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "latitude": [43.6430, 43.6532, 43.6700],
        "longitude": [-79.3875, -79.3832, -79.3800],
        "timestamp": pd.to_datetime(["2023-01-01 00:00:00", "2023-01-01 00:01:00", "2023-01-01 00:02:00"]),
    })


def test_add_distance_to_landmark_default(sample_df):
    df = add_distance_to_landmark(sample_df.copy())
    assert "dist_to_cn_tower_km" in df.columns
    assert not df["dist_to_cn_tower_km"].isnull().any()


def test_add_distance_to_landmark_missing_columns(sample_df):
    with pytest.raises(MissingColumnError):
        add_distance_to_landmark(sample_df.drop(columns=["latitude"]))


def test_add_distance_to_landmark_unknown_landmark(sample_df):
    with pytest.raises(LandmarkNotFoundError):
        add_distance_to_landmark(sample_df.copy(), landmark="UNKNOWN")


def test_add_distance_to_landmark_parallel(sample_df):
    df = add_distance_to_landmark(sample_df.copy(), parallel=True)
    assert not df["dist_to_cn_tower_km"].isnull().any()


def test_add_distance_to_landmark_custom_point(sample_df):
    df = add_distance_to_landmark(sample_df.copy(), landmark=(51.5074, -0.1278), output_col="dist_to_london_km")
    assert "dist_to_london_km" in df.columns


def test_add_distance_to_landmark_not_a_dataframe_raises():
    with pytest.raises(TypeError):
        add_distance_to_landmark("not_a_dataframe")


def test_add_location_jitter_basic(sample_df):
    df = add_location_jitter(sample_df.copy())
    assert df["location_jitter"].iloc[0] == 0.0
    assert df["location_jitter"].iloc[1] > 0.0


def test_add_location_jitter_threshold_flag(sample_df):
    df = add_location_jitter(sample_df.copy(), threshold=0.001)
    assert "location_jitter_flag" in df.columns
    assert df["location_jitter_flag"].sum() > 0


def test_add_location_jitter_missing_columns_raises():
    with pytest.raises(MissingColumnError):
        add_location_jitter(pd.DataFrame({"lat": [1.0], "lon": [2.0]}))


def test_normalize_coordinates_wraps_values():
    df = pd.DataFrame({"latitude": [91.0, -91.0], "longitude": [181.0, -181.0]})
    normalized = normalize_coordinates(df)
    assert (normalized["latitude"].between(-90, 90)).all()
    assert normalized.loc[0, "longitude"] == -179.0
    assert normalized.loc[1, "longitude"] == 179.0


def test_validate_dataframe_passes_for_valid_data(sample_df):
    assert validate_dataframe(sample_df)


def test_validate_dataframe_raises_for_out_of_range():
    df = pd.DataFrame({"latitude": [91.0], "longitude": [-75.0]})
    with pytest.raises(InvalidCoordinateError):
        validate_dataframe(df)


def test_validate_dataframe_raises_for_missing_columns():
    df = pd.DataFrame({"lat": [1.0]})
    with pytest.raises(MissingColumnError):
        validate_dataframe(df)


def test_validate_dataframe_raises_for_non_dataframe():
    with pytest.raises(TypeError):
        validate_dataframe("not_a_dataframe")
