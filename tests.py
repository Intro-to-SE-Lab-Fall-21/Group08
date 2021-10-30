import pathlib, os
import pytest

os.chdir(pathlib.Path.cwd() / "tests")

pytest.main()