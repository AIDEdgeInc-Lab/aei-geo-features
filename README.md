# aei-geo-features

[![PyPI version](https://img.shields.io/pypi/v/aei-geo-features.svg)](https://pypi.org/project/aei-geo-features/)
[![Python versions](https://img.shields.io/pypi/pyversions/aei-geo-features.svg)](https://pypi.org/project/aei-geo-features/)
[![License](https://img.shields.io/pypi/l/aei-geo-features.svg)](LICENSE)
[![CI](https://github.com/AIDEdgeInc-Lab/aei-geo-features/actions/workflows/ci.yml/badge.svg)](https://github.com/AIDEdgeInc-Lab/aei-geo-features/actions/workflows/ci.yml)

Small, dependency-light geospatial feature primitives for tabular data:
great-circle distance, distance-to-landmark, location-jitter (movement
between successive points), coordinate normalization, and coordinate
validation. Built on pandas/numpy only - no geopandas, no shapely, no
Dask, no network calls.

**Status: published on PyPI.** This repository is public on GitHub under
Apache License 2.0. See [the production PyPI project page](https://pypi.org/project/aei-geo-features/).

## Why this exists

`aei-geo-features` is a small, general-purpose geospatial feature utility
- distance, jitter, coordinate validation and normalization over tabular
data. It exists as a small, independently reviewable example of AID Edge
Inc.'s engineering quality: typed errors, deterministic functions, no
hidden I/O, and a test suite that exercises real behavior rather than
mocks.

This project is separate from, and does not include, any part of AID Edge
Inc.'s proprietary Velorona telecom and decision-intelligence capabilities.
It contains only generic geospatial math and ships with no data beyond
three widely-known public landmarks used as illustrative examples - no
telecom, network, or detection-specific logic of any kind.

## Who this is for

`aei-geo-features` is intended for developers, data scientists, analysts,
and researchers working with tabular data that includes latitude and
longitude.

It is useful for:

- Building lightweight geospatial features for machine-learning pipelines
- Calculating point-to-point or point-to-landmark distance
- Validating and normalizing coordinate columns in pandas DataFrames
- Measuring movement between sequential observations
- Preparing GPS, IoT, logistics, infrastructure, mobility, or asset-location data
- Adding basic geospatial context without introducing a full GIS stack

This library is especially suitable when simple, deterministic geospatial
utilities are needed, but routing, geocoding, polygon operations, CRS
transformation, or spatial databases are out of scope.

## Example use cases

Typical use cases include:

- Distance from a customer, device, or asset to a reference location
- Movement or jitter between sequential GPS observations
- Coordinate validation before analytics or model training
- Feature engineering for logistics, IoT, mobility, infrastructure, and location-based datasets
- Lightweight preprocessing where GeoPandas or other GIS-heavy dependencies are unnecessary

## Install

```bash
pip install aei-geo-features
```

## Quick start

```python
import pandas as pd
from aei_geo_features import haversine_distance, add_distance_to_landmark

# Single-pair distance
toronto = (43.6426, -79.3871)
paris = (48.8584, 2.2945)
print(haversine_distance(*toronto, *paris))  # 5997.878983178893 (km)

# DataFrame feature helper
df = pd.DataFrame({"latitude": [43.64], "longitude": [-79.38]})
df = add_distance_to_landmark(df, landmark="CN_TOWER")
print(df)
#    latitude  longitude  dist_to_cn_tower_km
# 0     43.64     -79.38             0.640313
```

See `examples/basic_usage.py` for a complete, runnable example.

## Public API

| Function / value | Purpose |
|---|---|
| `haversine_distance(lat1, lon1, lat2, lon2, unit="km")` | Great-circle distance between two points. |
| `validate_coordinate(lat, lon)` | Raises `InvalidCoordinateError` for an out-of-range or non-numeric pair; returns `True` otherwise. |
| `add_distance_to_landmark(df, landmark=..., ...)` | Adds a distance-to-landmark column to a DataFrame. |
| `add_location_jitter(df, ...)` | Adds a distance-from-previous-row column (optionally time-sorted first). |
| `normalize_coordinates(df, ...)` | Clips latitude to `[-90, 90]`, wraps longitude into `[-180, 180]`. |
| `validate_dataframe(df, ...)` | Validates a DataFrame's coordinate columns exist, are numeric, and are in range. |
| `REFERENCE_LANDMARKS` | Three illustrative public landmarks (CN Tower, Eiffel Tower, Statue of Liberty) - not a claim about any real deployment or dataset. |
| `GeoFeatureError` and subclasses (`InvalidCoordinateError`, `MissingColumnError`, `UnsupportedUnitError`, `LandmarkNotFoundError`) | Typed, catchable errors - never a bare `ValueError`/`Exception` for a domain failure. |

This is deliberately a narrow API. It does not include polygon region
assignment, CRS transformation, spatial indexing, or GeoJSON export - those
are heavier, geopandas/shapely/pyproj-dependent capabilities that were
evaluated and intentionally excluded from this package (see
`CHANGELOG.md` and the project's internal audit notes) as out of scope for
a small, narrowly-useful public library. They may be reconsidered for a
future major version if there is real external demand.

## What this is not

- Not a GIS platform. No polygon operations, no coordinate-reference-system
  transforms, no spatial database integration.
- Not a routing, geocoding, or reverse-geocoding library.
- Not affiliated with the Apache Software Foundation. "Apache License 2.0"
  refers only to the license text under which this project is distributed
  - see `LICENSE`.
- Not a certified or compliance-audited product. No FIPS, SOC 2, GDPR, ISO
  27001, or similar claim is made anywhere in this project.

## Dependencies

Runtime: `pandas`, `numpy`. Nothing else. See `CHANGELOG.md` for the full
dependency and license audit.

## Security

See `SECURITY.md` for supported versions and how to report a vulnerability
privately. See `docs/PUBLISHING.md` for the release process. PyPI releases
use Trusted Publishing with OIDC and no stored API token.

## Contributing

See `CONTRIBUTING.md`.

## License

Apache License 2.0 - see `LICENSE`.

Copyright 2026 AID Edge Inc.
