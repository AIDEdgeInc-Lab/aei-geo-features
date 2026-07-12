# Changelog

All notable changes to this project are recorded here. This project is
published on PyPI: https://pypi.org/project/aei-geo-features/

## [0.1.0] - 2026-07-12

### Added

- `haversine_distance(lat1, lon1, lat2, lon2, unit="km")` - great-circle
  distance between two points.
- `validate_coordinate(lat, lon)` - single-point coordinate validation.
- `add_distance_to_landmark(df, landmark=..., ...)` - DataFrame feature
  helper.
- `add_location_jitter(df, ...)` - distance-from-previous-row DataFrame
  feature helper.
- `normalize_coordinates(df, ...)` - clips/wraps latitude/longitude into
  valid ranges.
- `validate_dataframe(df, ...)` - validates a DataFrame's coordinate
  columns.
- `REFERENCE_LANDMARKS` - three illustrative public landmarks.
- Typed error hierarchy: `GeoFeatureError`, `InvalidCoordinateError`,
  `MissingColumnError`, `UnsupportedUnitError`, `LandmarkNotFoundError`.

### Provenance

Generalized from an internal, already-audited, non-proprietary geospatial
feature module. All telecom/microwave/operator-specific logic, internal
naming, and internal exception-hierarchy dependencies were removed or
reimplemented standalone during that generalization - none of this
project's code imports or depends on any private/internal package.

### Deliberately excluded from this release candidate

- Polygon region assignment, coordinate-reference-system (CRS)
  transformation, spatial indexing, and GeoJSON export. These exist in the
  internal source as a separate, heavier engine (optional
  geopandas/shapely/pyproj/geopy/Dask dependencies) and were evaluated but
  excluded here to keep this release candidate's dependency footprint and
  API surface minimal. May be reconsidered as a future major version (e.g.
  an `aei-geo-features[batch]` extra) if there is real external demand -
  not built speculatively.
- A `FeatureDefinition`-style declarative contract framework. The internal
  source has one, but it exists to describe execution-safety/statefulness
  distinctions relevant to a larger internal architecture; it did not seem
  to add value for a five-function public library and was left out to keep
  the API narrow. Docstrings and type hints serve the same documentation
  purpose here.
- Bearing/direction calculation. Considered per the general "what a geo
  library commonly offers" checklist, but no such function exists in the
  audited source material, so none was added - this project does not
  manufacture capabilities without an audited implementation behind them.

## Dependency and license audit

| Package | Version range | Purpose | License | Mandatory? | Redistribution/patent concern | Lighter alternative? |
|---|---|---|---|---|---|---|
| `pandas` | `>=1.5,<3` | DataFrame input/output for all `add_*`/`validate_dataframe`/`normalize_coordinates` functions | BSD-3-Clause | Yes | None - permissive, widely redistributed | Could drop to a stdlib-only single-point API (no DataFrame helpers); rejected because DataFrame-oriented feature helpers are this library's main value proposition |
| `numpy` | `>=1.23,<3` | `np.clip`, `np.nan`, vectorized array ops used by `normalize_coordinates`/`add_distance_to_landmark` | BSD-3-Clause | Yes (transitive via pandas in practice, declared explicitly for clarity) | None | None needed; already minimal |
| `pytest` | `>=7.4,<9` | Test runner | MIT | Dev-only | None | None needed; de facto standard |
| `build` | `>=1.0,<2` | PEP 517 build frontend, used in CI to build wheel/sdist | MIT | Dev-only | None | None needed |
| `twine` | `>=5.0,<7` | Package-metadata/README validation (`twine check`) in CI, run as part of the `build` job in `.github/workflows/publish.yml` before either publish job runs | Apache-2.0 | Dev-only | None | None needed |

No dependency copies third-party source code into this project. No
dependency was flagged with unclear or incompatible licensing. `pandas`
and `numpy` are both BSD-3-Clause, fully compatible with Apache 2.0
redistribution. All four non-runtime tools are dev-only and never ship
inside the built wheel/sdist (verified - see the package-content
inspection results in the audit report).

Standard-library alternatives were considered for the runtime path
(`math` alone covers `haversine_distance` and `validate_coordinate`, which
is why those two functions have no DataFrame/pandas dependency internally
beyond what's needed to accept a DataFrame in the `add_*` helpers) - full
stdlib-only was not chosen as the project-wide default because the
DataFrame-oriented helpers are the more useful half of the public API for
the intended feature-engineering use case.
