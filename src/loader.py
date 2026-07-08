"""Download curated typing PEPs from the official Python PEP repository."""
from __future__ import annotations
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from src.config import PEP_NUMBERS, PEP_RAW_URL, RAW_DIR

@dataclass(frozen=True)
class DownloadResult:
    """Summary of a dataset download run."""

    downloaded: list[int]
    skipped: list[int]
    failed: dict[int, str]
    paths: list[Path]

    @property
    def ok(self) -> bool:
        return not self.failed

class PepDownloader:
    """Reproducibly download the selected official PEP RST files.

    The downloader never fabricates PEP content. If the official repository is
    unavailable, failed PEP numbers are reported and any already-downloaded
    files remain available for parsing.
    """

    def __init__(
        self,
        raw_dir: Path = RAW_DIR,
        pep_numbers: tuple[int, ...] = PEP_NUMBERS,
        retries: int = 3,
        backoff_seconds: float = 1.0,
    ) -> None:
        self.raw_dir = raw_dir
        self.pep_numbers = pep_numbers
        self.retries = retries
        self.backoff_seconds = backoff_seconds

    def download_all(self, force: bool = False) -> DownloadResult:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        downloaded: list[int] = []
        skipped: list[int] = []
        failed: dict[int, str] = {}
        paths: list[Path] = []

        total = len(self.pep_numbers)
        for index, pep in enumerate(self.pep_numbers, start=1):
            path = self.raw_dir / f"pep-{pep:04d}.rst"
            paths.append(path)
            if path.exists() and not force:
                skipped.append(pep)
                print(f"[{index}/{total}] PEP {pep}: already present, skipping")
                continue

            url = PEP_RAW_URL.format(pep=pep)
            print(f"[{index}/{total}] PEP {pep}: downloading {url}")
            error = self._download_with_retries(url, path)
            if error is None:
                downloaded.append(pep)
                print(f"[{index}/{total}] PEP {pep}: saved to {path}")
            else:
                failed[pep] = error
                print(f"[{index}/{total}] PEP {pep}: failed after {self.retries} attempts: {error}")

        if failed:
            failed_list = ", ".join(str(pep) for pep in sorted(failed))
            print(f"Download completed with failures for PEPs: {failed_list}")
        else:
            print("Download completed successfully")
        return DownloadResult(downloaded=downloaded, skipped=skipped, failed=failed, paths=paths)

    def existing_paths(self) -> list[Path]:
        return sorted(path for path in self.raw_dir.glob("pep-*.rst") if path.is_file())

    def _download_with_retries(self, url: str, path: Path) -> str | None:
        last_error: str | None = None
        for attempt in range(1, self.retries + 1):
            try:
                with urlopen(url, timeout=30) as response:
                    path.write_bytes(response.read())
                return None
            except HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.reason}"
            except URLError as exc:
                last_error = f"URL error: {exc.reason}"
            except OSError as exc:
                last_error = str(exc)

            if attempt < self.retries:
                time.sleep(self.backoff_seconds * attempt)
        return last_error or "unknown download error"
