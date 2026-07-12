"""Minimal, self-contained usage example for aei_geo_features.

Run with: python examples/basic_usage.py
"""
import pandas as pd

from aei_geo_features import (
    add_distance_to_landmark,
    add_location_jitter,
    haversine_distance,
    normalize_coordinates,
    validate_coordinate,
)


def main() -> None:
    # Single-pair distance.
    toronto = (43.6426, -79.3871)
    paris = (48.8584, 2.2945)
    distance_km = haversine_distance(*toronto, *paris)
    print(f"Toronto -> Paris: {distance_km:.1f} km")

    # Single-point validation.
    validate_coordinate(*toronto)
    print("Toronto coordinate is valid.")

    # DataFrame-level feature helpers.
    df = pd.DataFrame({
        "latitude": [43.6430, 43.6532, 43.6700],
        "longitude": [-79.3875, -79.3832, -79.3800],
        "timestamp": pd.to_datetime([
            "2023-01-01 00:00:00", "2023-01-01 00:01:00", "2023-01-01 00:02:00",
        ]),
    })

    df = add_distance_to_landmark(df, landmark="CN_TOWER")
    df = add_location_jitter(df, time_col="timestamp", threshold=0.05)
    df = normalize_coordinates(df)

    print(df)


if __name__ == "__main__":
    main()
