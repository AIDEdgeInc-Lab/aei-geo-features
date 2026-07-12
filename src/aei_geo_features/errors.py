"""Typed exceptions for aei_geo_features.

This is a small, self-contained hierarchy rooted directly in the stdlib
``Exception`` - it does not inherit from, import, or depend on any other
package's exception base class. Each error carries the same plain-string
message plus a small set of typed context fields, and exposes
``to_dict()`` for callers who want a machine-readable representation
separate from ``str(exc)``.
"""
from typing import Any, Dict, List, Optional


class GeoFeatureError(Exception):
    """Base exception for all errors raised by this package."""

    def to_dict(self) -> Dict[str, Any]:
        return {"error": type(self).__name__, "message": str(self)}


class InvalidCoordinateError(GeoFeatureError):
    """Raised for an out-of-range or non-numeric latitude/longitude value."""

    def __init__(
        self,
        message: str = "Invalid latitude or longitude value.",
        coord_value: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ):
        super().__init__(message)
        self.coord_value = coord_value
        self.min_val = min_val
        self.max_val = max_val

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "coord_value": self.coord_value,
            "min_val": self.min_val,
            "max_val": self.max_val,
        }


class MissingColumnError(GeoFeatureError):
    """Raised when a required column is missing from a DataFrame."""

    def __init__(
        self,
        message: str = "Required column(s) not found in DataFrame.",
        missing_cols: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.missing_cols: List[str] = list(missing_cols) if missing_cols is not None else []

    def to_dict(self) -> Dict[str, Any]:
        return {**super().to_dict(), "missing_cols": self.missing_cols}


class UnsupportedUnitError(GeoFeatureError):
    """Raised when an unsupported distance unit is requested."""

    def __init__(
        self,
        message: str = "Unsupported unit provided.",
        unit_provided: Optional[str] = None,
        supported_units: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.unit_provided = unit_provided
        self.supported_units: List[str] = list(supported_units) if supported_units is not None else []

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "unit_provided": self.unit_provided,
            "supported_units": self.supported_units,
        }


class LandmarkNotFoundError(GeoFeatureError):
    """Raised when a named landmark is not found in the built-in reference set."""

    def __init__(
        self,
        message: str = "Landmark not found.",
        landmark_name: Optional[str] = None,
        available_landmarks: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.landmark_name = landmark_name
        self.available_landmarks: List[str] = list(available_landmarks) if available_landmarks is not None else []

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "landmark_name": self.landmark_name,
            "available_landmarks": self.available_landmarks,
        }
