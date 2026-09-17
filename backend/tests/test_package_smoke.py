from pathlib import Path

import rebot


def test_package_resolves_from_src_layout() -> None:
    expected_package_init = Path(__file__).resolve().parents[1] / "src" / "rebot" / "__init__.py"

    assert Path(rebot.__file__).resolve() == expected_package_init
