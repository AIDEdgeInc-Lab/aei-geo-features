"""Small, dependency-light geospatial feature primitives.

Generalized from an internal, non-proprietary geo-math module (great-circle
distance, distance-to-landmark, location-jitter, coordinate normalization
and validation) with all telecom/microwave/operator-specific code, internal
naming, and internal error-hierarchy dependencies removed. Nothing in this
module reads real device, tower, site, or customer data - the only
coordinates shipped with the package are three widely-known public
landmarks used purely as illustrative reference points.

Deterministic and stateless: no I/O, no network calls, no environment-
variable reads, no hidden global state.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from math import asin, cos, radians, sin, sqrt
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd

from aei_geo_features.errors import (
    GeoFeatureError,
    InvalidCoordinateError,
    LandmarkNotFoundError,
    MissingColumnError,
    UnsupportedUnitError,
)

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371
MAX_LATITUDE = 90.0
MIN_LATITUDE = -90.0
MAX_LONGITUDE = 180.0
MIN_LONGITUDE = -180.0

#: Illustrative reference points only - not a claim about any real
#: deployment or dataset. Callers are free to pass their own (lat, lon)
#: tuple instead of one of these names.
REFERENCE_LANDMARKS = {
    "CN_TOWER": (43.6426, -79.3871),
    "EIFFEL_TOWER": (48.8584, 2.2945),
    "STATUE_OF_LIBERTY": (40.6892, -74.0445),
}


def _validate_single_point(lat: float, lon: float, name: str = "Coordinate") -> None:
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise InvalidCoordinateError(
            f"{name} must be numeric. Got lat={type(lat).__name__}, lon={type(lon).__name__}."
        )
    if not (MIN_LATITUDE <= lat <= MAX_LATITUDE):
        raise InvalidCoordinateError(
            f"{name} latitude {lat} is out of valid range [{MIN_LATITUDE}, {MAX_LATITUDE}]",
            coord_value=lat, min_val=MIN_LATITUDE, max_val=MAX_LATITUDE,
        )
    if not (MIN_LONGITUDE <= lon <= MAX_LONGITUDE):
        raise InvalidCoordinateError(
            f"{name} longitude {lon} is out of valid range [{MIN_LONGITUDE}, {MAX_LONGITUDE}]",
            coord_value=lon, min_val=MIN_LONGITUDE, max_val=MAX_LONGITUDE,
        )


def validate_coordinate(lat: float, lon: float) -> bool:
    """Validates a single (lat, lon) pair. Returns True, or raises
    InvalidCoordinateError - never returns False."""
    _validate_single_point(lat, lon)
    return True


def validate_coordinates(func):
    """Decorator for two-point functions taking (lat1, lon1, lat2, lon2)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) >= 4:
            coords = [(args[0], args[1]), (args[2], args[3])]
        elif all(k in kwargs for k in ("lat1", "lon1", "lat2", "lon2")):
            coords = [(kwargs["lat1"], kwargs["lon1"]), (kwargs["lat2"], kwargs["lon2"])]
        else:
            raise GeoFeatureError(
                f"@validate_coordinates requires lat1, lon1, lat2, lon2. "
                f"Function '{func.__name__}' called with unexpected arguments."
            )
        for i, (lat, lon) in enumerate(coords):
            _validate_single_point(lat, lon, name=f"Point {i + 1} coordinate")
        return func(*args, **kwargs)
    return wrapper


@validate_coordinates
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "km") -> float:
    """Great-circle distance between two points. Deterministic, stateless,
    no I/O."""
    try:
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        distance = EARTH_RADIUS_KM * 2 * asin(sqrt(a))

        if unit == "mi":
            return distance * 0.621371
        elif unit == "km":
            return distance
        raise UnsupportedUnitError(
            f"Unsupported unit: '{unit}'. Use 'km' or 'mi'.", unit_provided=unit, supported_units=["km", "mi"],
        )
    except (InvalidCoordinateError, UnsupportedUnitError):
        raise
    except Exception as exc:
        logger.exception("Unexpected error calculating haversine distance")
        raise GeoFeatureError(f"Failed to calculate haversine distance: {exc}") from exc


def add_distance_to_landmark(
    df: pd.DataFrame,
    landmark: Union[str, Tuple[float, float]] = "CN_TOWER",
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    output_col: Optional[str] = None,
    unit: str = "km",
    parallel: bool = False,
) -> pd.DataFrame:
    """Adds a distance-to-landmark column. `landmark` is either a name from
    REFERENCE_LANDMARKS (example points only) or an explicit (lat, lon)."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    try:
        if isinstance(landmark, str):
            if landmark not in REFERENCE_LANDMARKS:
                raise LandmarkNotFoundError(
                    f"Landmark '{landmark}' not found. Available: {list(REFERENCE_LANDMARKS.keys())}",
                    landmark_name=landmark, available_landmarks=list(REFERENCE_LANDMARKS.keys()),
                )
            landmark_coords = REFERENCE_LANDMARKS[landmark]
        elif isinstance(landmark, (tuple, list)) and len(landmark) == 2:
            landmark_coords = landmark
            _validate_single_point(landmark_coords[0], landmark_coords[1], name="Custom landmark")
        else:
            raise ValueError("Landmark must be either a predefined name (str) or a (lat, lon) tuple/list.")

        if output_col is None:
            landmark_name = landmark if isinstance(landmark, str) else "custom_landmark"
            output_col = f"dist_to_{landmark_name.lower()}_{unit}"

        missing = [col for col in (lat_col, lon_col) if col not in df.columns]
        if missing:
            raise MissingColumnError(f"DataFrame must contain required columns: {missing}", missing_cols=missing)

        if unit not in ("km", "mi"):
            raise UnsupportedUnitError(
                f"Unsupported unit: '{unit}'. Use 'km' or 'mi'.", unit_provided=unit, supported_units=["km", "mi"],
            )

        if not pd.api.types.is_numeric_dtype(df[lat_col]) or not pd.api.types.is_numeric_dtype(df[lon_col]):
            raise InvalidCoordinateError(f"'{lat_col}' and '{lon_col}' columns must contain numeric values.")

        df = df.copy()
        if parallel:
            def calculate_dist(lat, lon):
                try:
                    return haversine_distance(lat, lon, landmark_coords[0], landmark_coords[1], unit=unit)
                except (InvalidCoordinateError, UnsupportedUnitError) as exc:
                    logger.warning(f"Skipping distance calculation for ({lat}, {lon}) due to: {exc}")
                    return np.nan

            with ThreadPoolExecutor() as executor:
                df[output_col] = list(executor.map(calculate_dist, df[lat_col], df[lon_col]))
        else:
            df[output_col] = df.apply(
                lambda row: haversine_distance(row[lat_col], row[lon_col], landmark_coords[0], landmark_coords[1], unit=unit),
                axis=1,
            )
        return df

    except (MissingColumnError, LandmarkNotFoundError, InvalidCoordinateError, UnsupportedUnitError, TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception(f"Failed to add distance to landmark '{landmark}'")
        raise GeoFeatureError(f"Failed to add distance to landmark: {exc}") from exc


def add_location_jitter(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    time_col: Optional[str] = None,
    threshold: Optional[float] = None,
) -> pd.DataFrame:
    """Distance between each row and the previous one (0.0 for the first
    row). Sorted by `time_col` first if given."""
    if not all(col in df.columns for col in (lat_col, lon_col)):
        raise MissingColumnError(
            "Required 'latitude' or 'longitude' columns missing for jitter calculation.",
            missing_cols=[c for c in (lat_col, lon_col) if c not in df.columns],
        )

    temp_df = df.copy()
    if time_col:
        if time_col not in temp_df.columns:
            raise MissingColumnError(f"Time column '{time_col}' not found for time-aware jitter calculation.", missing_cols=[time_col])
        if not pd.api.types.is_datetime64_any_dtype(temp_df[time_col]):
            temp_df[time_col] = pd.to_datetime(temp_df[time_col])
        temp_df = temp_df.sort_values(by=[time_col]).reset_index(drop=True)

    if not pd.api.types.is_numeric_dtype(temp_df[lat_col]) or not pd.api.types.is_numeric_dtype(temp_df[lon_col]):
        raise InvalidCoordinateError(f"'{lat_col}' and '{lon_col}' columns must contain numeric values for jitter calculation.")

    distances = [0.0]
    for i in range(1, len(temp_df)):
        try:
            distances.append(haversine_distance(
                temp_df[lat_col].iloc[i - 1], temp_df[lon_col].iloc[i - 1],
                temp_df[lat_col].iloc[i], temp_df[lon_col].iloc[i],
            ))
        except InvalidCoordinateError as exc:
            logger.warning(f"Skipping jitter calculation for row {i} due to invalid coordinates: {exc}")
            distances.append(np.nan)

    temp_df["location_jitter"] = distances
    if threshold is not None:
        if not isinstance(threshold, (int, float)) or threshold < 0:
            raise ValueError("Jitter threshold must be a non-negative number.")
        temp_df["location_jitter_flag"] = (temp_df["location_jitter"] > threshold).astype(int)
    return temp_df


def normalize_coordinates(df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude") -> pd.DataFrame:
    """Clips latitude to [-90, 90] and wraps longitude into [-180, 180]."""
    if not all(col in df.columns for col in (lat_col, lon_col)):
        raise MissingColumnError(
            "Required 'latitude' or 'longitude' columns missing for normalization.",
            missing_cols=[c for c in (lat_col, lon_col) if c not in df.columns],
        )
    normalized_df = df.copy()
    if not pd.api.types.is_numeric_dtype(normalized_df[lat_col]) or not pd.api.types.is_numeric_dtype(normalized_df[lon_col]):
        raise InvalidCoordinateError(f"'{lat_col}' and '{lon_col}' columns must contain numeric values for normalization.")

    normalized_df[lat_col] = np.clip(normalized_df[lat_col], MIN_LATITUDE, MAX_LATITUDE)
    normalized_df[lon_col] = (normalized_df[lon_col] + 180) % 360 - 180
    return normalized_df


def validate_dataframe(df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude") -> bool:
    """Raises if required columns are missing, non-numeric, or out of range; returns True otherwise."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    missing_cols = [col for col in (lat_col, lon_col) if col not in df.columns]
    if missing_cols:
        raise MissingColumnError("Required columns for validation are missing.", missing_cols=missing_cols)

    if not pd.api.types.is_numeric_dtype(df[lat_col]) or not pd.api.types.is_numeric_dtype(df[lon_col]):
        raise InvalidCoordinateError("Latitude and longitude columns must be numeric.")

    if not df[lat_col].between(MIN_LATITUDE, MAX_LATITUDE, inclusive="both").all():
        invalid = df[~df[lat_col].between(MIN_LATITUDE, MAX_LATITUDE, inclusive="both")][lat_col].tolist()
        raise InvalidCoordinateError(
            f"Invalid latitude values found: {invalid[:5]} (first 5 out of {len(invalid)}). "
            f"Must be between {MIN_LATITUDE} and {MAX_LATITUDE}."
        )
    if not df[lon_col].between(MIN_LONGITUDE, MAX_LONGITUDE, inclusive="both").all():
        invalid = df[~df[lon_col].between(MIN_LONGITUDE, MAX_LONGITUDE, inclusive="both")][lon_col].tolist()
        raise InvalidCoordinateError(
            f"Invalid longitude values found: {invalid[:5]} (first 5 out of {len(invalid)}). "
            f"Must be between {MIN_LONGITUDE} and {MAX_LONGITUDE}."
        )
    return True
