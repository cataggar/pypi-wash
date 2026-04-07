#!/usr/bin/env python3
"""Download wash release assets and repackage them as Python wheels."""

# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# ///

import hashlib
import sys
import zipfile
from base64 import urlsafe_b64encode
from pathlib import Path

import requests  # type: ignore[import-untyped]

IMPORT_NAME = "wash_cli"
DIST_NAME = "wash_bin"
WASH_REPO = "wasmCloud/wasmCloud"

# Maps release asset target triple to one or more wheel platform tags.
# wash releases are bare binaries (not archives).
PLATFORMS: dict[str, list[dict[str, str]]] = {
    "x86_64-unknown-linux-musl": [
        {"tag": "manylinux_2_17_x86_64.manylinux2014_x86_64", "binary": "wash"},
        {"tag": "musllinux_1_1_x86_64", "binary": "wash"},
    ],
    "aarch64-unknown-linux-musl": [
        {"tag": "manylinux_2_17_aarch64.manylinux2014_aarch64", "binary": "wash"},
        {"tag": "musllinux_1_1_aarch64", "binary": "wash"},
    ],
    "x86_64-apple-darwin": [
        {"tag": "macosx_10_9_x86_64", "binary": "wash"},
    ],
    "aarch64-apple-darwin": [
        {"tag": "macosx_11_0_arm64", "binary": "wash"},
    ],
    "x86_64-pc-windows-msvc": [
        {"tag": "win_amd64", "binary": "wash.exe"},
    ],
}


def sha256_digest(data: bytes) -> str:
    """Return url-safe base64 sha256 digest (no padding)."""
    return urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()


def download_asset(version: str, target: str) -> bytes:
    """Download a wash release binary."""
    asset_name = f"wash-{target}"
    url = f"https://github.com/{WASH_REPO}/releases/download/v{version}/{asset_name}"
    print(f"  Downloading {asset_name} ...")
    resp = requests.get(url, allow_redirects=True, timeout=300)
    resp.raise_for_status()
    return resp.content


_EXEC_ATTR = 0o100755 << 16
_FILE_ATTR = 0o100644 << 16


def build_wheel(
    version: str,
    binary_data: bytes,
    binary_name: str,
    platform_tag: str,
    dist_dir: Path,
) -> Path:
    """Build a single platform wheel."""
    # Collect wheel entries: (arcname, data_bytes, is_executable)
    entries: list[tuple[str, bytes, bool]] = []

    # Add __init__.py
    init_py = Path(__file__).resolve().parent.parent / "python" / IMPORT_NAME / "__init__.py"
    entries.append(
        (f"{IMPORT_NAME}/__init__.py", init_py.read_bytes(), False)
    )

    # Add the binary
    entries.append((f"{IMPORT_NAME}/{binary_name}", binary_data, True))

    # dist-info directory
    dist_info_dir = f"{DIST_NAME}-{version}.dist-info"

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    metadata = (
        f"Metadata-Version: 2.4\n"
        f"Name: wash-bin\n"
        f"Version: {version}\n"
        f"Summary: wash CLI repackaged as Python wheels\n"
        f"Home-page: https://github.com/wasmCloud/wasmCloud\n"
        f"License: Apache-2.0\n"
        f"Requires-Python: >=3.9\n"
        f"Description-Content-Type: text/markdown\n"
        f"\n"
        f"{readme_text}"
    )
    entries.append((f"{dist_info_dir}/METADATA", metadata.encode(), False))

    wheel_meta = (
        f"Wheel-Version: 1.0\n"
        f"Generator: build_wheels.py\n"
        f"Root-Is-Purelib: false\n"
        f"Tag: py3-none-{platform_tag}\n"
    )
    entries.append((f"{dist_info_dir}/WHEEL", wheel_meta.encode(), False))

    entry_points = f"[console_scripts]\nwash = {IMPORT_NAME}:main\n"
    entries.append(
        (f"{dist_info_dir}/entry_points.txt", entry_points.encode(), False)
    )

    # Build RECORD
    records: list[str] = []
    for arcname, file_data, _ in entries:
        digest = sha256_digest(file_data)
        records.append(f"{arcname},sha256={digest},{len(file_data)}")
    records.append(f"{dist_info_dir}/RECORD,,")
    record_data = ("\n".join(records) + "\n").encode()
    entries.append((f"{dist_info_dir}/RECORD", record_data, False))

    # Write wheel zip
    wheel_name = f"{DIST_NAME}-{version}-py3-none-{platform_tag}.whl"
    wheel_path = dist_dir / wheel_name
    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as whl:
        for arcname, file_data, executable in entries:
            zi = zipfile.ZipInfo(arcname)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = _EXEC_ATTR if executable else _FILE_ATTR
            whl.writestr(zi, file_data)

    print(f"  Built {wheel_name} ({wheel_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return wheel_path


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>")
        print(f"Example: {sys.argv[0]} 2.0.2")
        sys.exit(1)

    version = sys.argv[1]
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)

    print(f"Building wheels for wash v{version}\n")

    wheels: list[Path] = []
    for target, wheel_configs in PLATFORMS.items():
        print(f"[{target}]")
        binary_data = download_asset(version, target)

        for config in wheel_configs:
            wheel = build_wheel(
                version, binary_data, config["binary"], config["tag"], dist_dir
            )
            wheels.append(wheel)
        print()

    print(f"Done! {len(wheels)} wheels in {dist_dir}/")
    for w in wheels:
        print(f"  {w.name}")


if __name__ == "__main__":
    main()
