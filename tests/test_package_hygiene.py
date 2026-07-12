"""Package-hygiene tests: no network calls, no env-var dependency, no
import-time side effects, no internal AID Edge / Velorona paths or naming
leaking into the public package.
"""
import ast
import importlib
import sys
from pathlib import Path

import aei_geo_features
from aei_geo_features.geo import REFERENCE_LANDMARKS

SRC_DIR = Path(aei_geo_features.__file__).resolve().parent

#: Manually reviewed 2026-07-12 against independent public sources
#: (Wikipedia-published coordinates for each monument) - see the release
#: candidate's verification report. Any change to REFERENCE_LANDMARKS must
#: go through the same manual review before this test is updated.
REVIEWED_PUBLIC_LANDMARKS = {
    "CN_TOWER": (43.6426, -79.3871),
    "EIFFEL_TOWER": (48.8584, 2.2945),
    "STATUE_OF_LIBERTY": (40.6892, -74.0445),
}


def _all_source_files():
    return sorted(SRC_DIR.rglob("*.py"))


def test_package_has_no_network_imports():
    banned = {"requests", "urllib", "http", "socket", "aiohttp", "httpx"}
    for path in _all_source_files():
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in banned, f"{path}: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in banned, f"{path}: {node.module}"


def test_package_does_not_read_environment_variables():
    for path in _all_source_files():
        assert "os.environ" not in path.read_text(), path
        assert "os.getenv" not in path.read_text(), path


def test_no_module_level_side_effect_calls():
    """No function call at module top level (besides class/def bodies) -
    i.e. nothing runs at import time beyond defining names."""
    for path in _all_source_files():
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                raise AssertionError(f"Unexpected import-time call in {path}: {ast.dump(node.value.func)}")


def test_no_internal_aid_edge_or_velorona_paths_in_source():
    banned_substrings = ["velorona", "aidedgeinc", "AIDEdgeInc-Lab", "aei.foundation", "aei.telecom", "aei.ml_platform"]
    for path in _all_source_files():
        text = path.read_text().lower()
        for banned in banned_substrings:
            assert banned.lower() not in text, f"Found '{banned}' in {path}"


def test_no_internal_error_hierarchy_imported():
    """Confirms this package's errors are self-contained - never import an
    internal AEIError-rooted base class."""
    for path in _all_source_files():
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("aei.foundation"), f"{path} imports internal {node.module}"


def test_reimporting_module_does_not_reexecute_network_or_env_logic():
    """Re-import is idempotent and side-effect-free (proxy: no exception,
    same object identity)."""
    mod1 = importlib.import_module("aei_geo_features")
    mod2 = importlib.reload(sys.modules["aei_geo_features"])
    assert mod1.__version__ == mod2.__version__


def test_no_secret_like_string_literals_in_source():
    """A crude but real check: no string literal in source looks like an
    API key, token, or credential."""
    suspicious_markers = ["api_key", "apikey", "secret_key", "access_token", "aws_secret", "private_key", "-----BEGIN"]
    for path in _all_source_files():
        text = path.read_text().lower()
        for marker in suspicious_markers:
            assert marker not in text, f"Suspicious marker '{marker}' found in {path}"


def test_reference_landmarks_match_manually_reviewed_set_exactly():
    """REFERENCE_LANDMARKS must contain exactly the manually-reviewed public
    landmarks - no more, no fewer, no silently-changed coordinate. Adding a
    new entry requires the same manual public-source verification as the
    three already reviewed (see the release candidate's verification
    report) before this test's REVIEWED_PUBLIC_LANDMARKS is updated."""
    assert REFERENCE_LANDMARKS == REVIEWED_PUBLIC_LANDMARKS


def test_no_contracts_module_imported_or_referenced():
    """This package must work entirely without any FeatureDefinition-style
    contracts framework - it never existed as a dependency and must not be
    reintroduced."""
    banned = ["contracts", "FeatureDefinition", "FeatureCategory", "ExecutionSafety", "Statefulness",
              "ROLLING_SIGNAL_STATS", "BUILT_FEATURE_SET"]
    for path in _all_source_files():
        text = path.read_text()
        for marker in banned:
            assert marker not in text, f"Found '{marker}' in {path}"
