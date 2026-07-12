"""aei_geo_features - small, dependency-light geospatial feature primitives.

Public API:
    haversine_distance, validate_coordinate, add_distance_to_landmark,
    add_location_jitter, normalize_coordinates, validate_dataframe,
    REFERENCE_LANDMARKS, GeoFeatureError and its typed subclasses.

See README.md for scope, and CHANGELOG.md for version history.
"""
from aei_geo_features.errors import (
    GeoFeatureError,
    InvalidCoordinateError,
    LandmarkNotFoundError,
    MissingColumnError,
    UnsupportedUnitError,
)
from aei_geo_features.geo import (
    EARTH_RADIUS_KM,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
    REFERENCE_LANDMARKS,
    add_distance_to_landmark,
    add_location_jitter,
    haversine_distance,
    normalize_coordinates,
    validate_coordinate,
    validate_dataframe,
)

__version__ = "0.1.3"

__all__ = [
    "__version__",
    "GeoFeatureError",
    "InvalidCoordinateError",
    "MissingColumnError",
    "UnsupportedUnitError",
    "LandmarkNotFoundError",
    "EARTH_RADIUS_KM",
    "MAX_LATITUDE",
    "MIN_LATITUDE",
    "MAX_LONGITUDE",
    "MIN_LONGITUDE",
    "REFERENCE_LANDMARKS",
    "haversine_distance",
    "validate_coordinate",
    "add_distance_to_landmark",
    "add_location_jitter",
    "normalize_coordinates",
    "validate_dataframe",
]
