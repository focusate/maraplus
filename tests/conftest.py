import pathlib
import pytest


@pytest.fixture(scope="package")
def path_modules_one():
    yield str(_get_path("modules_one.yml"))


@pytest.fixture(scope="package")
def path_modules_two():
    yield str(_get_path("modules_two.yml"))


def _get_path(*args) -> pathlib.Path:
    p = pathlib.Path(__file__).parent / "data"
    return p.joinpath(*args)
