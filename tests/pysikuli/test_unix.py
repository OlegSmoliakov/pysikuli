import pytest
import platform

from subprocess import PIPE, run

import src.pysikuli as sik

if not platform.system() == "Linux":
    pytest.skip("skipping Linux-only tests", allow_module_level=True)

from src.pysikuli import _unix as unix

TEST_REFRESH_RATE = 60
TEST_PKGS = ["rolldice"]


def uninstalTestPkg():
    command = ["sudo", "apt-get", "-y", "remove"]
    for package in TEST_PKGS:
        command.append(package)

    run(command, encoding="utf-8")


@pytest.fixture()
def aptTesting():
    yield
    uninstalTestPkg()


class TestUnix:
    def test_apt_check_return_none(self):
        assert unix._apt_check(["flex"]) is None

    @pytest.mark.parametrize(
        "test_pkgs, expected",
        [
            (["test"], "Installing packages: test\n"),
            (["test", "test_pkg_test"], "Installing packages: test, test_pkg_test\n"),
            (["flex"], "The requirements have already been installed\n"),
        ],
    )
    def test_apt_check_return_print(self, mocker, capsys, test_pkgs, expected):
        mocker.patch("src.pysikuli._unix._apt_install", return_value=None)
        unix._apt_check(test_pkgs)

        captured = capsys.readouterr().out
        # out, err = capsys.readouterr()

        assert captured == expected

    def test_getRefreshRate(self):
        assert isinstance(unix._getRefreshRate(), int)
        assert unix._getRefreshRate() == TEST_REFRESH_RATE
