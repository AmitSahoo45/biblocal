import pytest

from biblocal.ocr import OcrEngine


@pytest.fixture(scope="session")
def engine():
    return OcrEngine()
