import pytest
import platform

if not platform.system() == "Darwin":
    pytest.skip("skipping MacOS-only tests", allow_module_level=True)

from src.pysikuli import _osx as osx


class TestOSX:
    def test_1(self):
        pass
