"""Config sanity - cheap guards against foot-guns like overlap >= chunk size."""
import pytest

from rag import config


def test_chunk_config_is_sane():
    assert config.CHUNK_SIZE > config.CHUNK_OVERLAP > 0


def test_top_k_is_sane():
    assert config.TOP_K >= 1


def test_fetch_k_at_least_top_k():
    if not hasattr(config, "FETCH_K"):
        pytest.skip("rerank settings not installed")
    assert config.FETCH_K >= config.TOP_K


def test_expected_paths():
    assert config.DATA_DIR.name == "sample_docs"
    assert config.COLLECTION
