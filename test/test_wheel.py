import subprocess
import sys
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def test_wheel_is_platform_specific(tmp_path: Path) -> None:
    """Check wheel compatibility tags and the bundled library's location.

    Args:
        tmp_path: Directory for the built wheel.

    """
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(tmp_path),
            str(root),
        ],
        check=True,
        timeout=180,
    )
    [wheel] = tmp_path.glob("libfaketime-*.whl")
    _, python_tag, abi_tag, platform_tag = wheel.stem.rsplit("-", 3)
    assert python_tag == "py3"
    assert abi_tag == "none"
    assert platform_tag != "any"

    library_name = (
        "libfaketime.1.dylib" if sys.platform == "darwin" else "libfaketime.so.1"
    )
    with ZipFile(wheel) as archive:
        [metadata_path] = (
            name for name in archive.namelist() if name.endswith(".dist-info/WHEEL")
        )
        metadata = BytesParser().parsebytes(archive.read(metadata_path))
        assert metadata["Root-Is-Purelib"] == "false"
        library = archive.getinfo(f"libfaketime/vendor/libfaketime/src/{library_name}")
        assert library.file_size > 0
