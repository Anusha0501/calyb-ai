from io import BytesIO
from urllib.error import HTTPError
from src.loader import PepDownloader

class Response(BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

def test_downloader_downloads_missing_and_skips_existing(tmp_path, monkeypatch):
    calls = []
    def fake_urlopen(url, timeout):
        calls.append(url)
        return Response(b"PEP: 484\nTitle: Type Hints\n")
    monkeypatch.setattr("src.loader.urlopen", fake_urlopen)
    downloader = PepDownloader(raw_dir=tmp_path, pep_numbers=(484,), retries=1)
    first = downloader.download_all()
    second = downloader.download_all()
    assert first.downloaded == [484]
    assert second.skipped == [484]
    assert (tmp_path / "pep-0484.rst").exists()
    assert len(calls) == 1

def test_downloader_logs_failures_without_crashing(tmp_path, monkeypatch):
    def fake_urlopen(url, timeout):
        raise HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr("src.loader.urlopen", fake_urlopen)
    result = PepDownloader(raw_dir=tmp_path, pep_numbers=(9999,), retries=1).download_all()
    assert 9999 in result.failed
    assert not (tmp_path / "pep-9999.rst").exists()
