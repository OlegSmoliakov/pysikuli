import pytest
import platform

if not platform.system() == "Windows":
    pytest.skip("skipping Windows-only tests", allow_module_level=True)

from ...src.pysikuli import _win as win


class TestUtils:
    def test_1(self):
        pass
