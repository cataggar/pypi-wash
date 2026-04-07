# wash-bin

[wash](https://github.com/wasmCloud/wasmCloud) CLI repackaged as Python wheels for easy installation via tools like `uv`.

wash is the command-line tool for wasmCloud development.

## Install

```sh
uv tool install wash-bin
wash --version
```

## Supported Platforms

| Platform | Wheel tag |
|----------|-----------|
| Linux x64 | `manylinux_2_17_x86_64` |
| Linux ARM64 | `manylinux_2_17_aarch64` |
| Linux x64 (musl) | `musllinux_1_1_x86_64` |
| Linux ARM64 (musl) | `musllinux_1_1_aarch64` |
| macOS x64 | `macosx_10_9_x86_64` |
| macOS ARM64 | `macosx_11_0_arm64` |
| Windows x64 | `win_amd64` |

## How It Works

This package downloads the official wash release binaries from
[wasmCloud/wasmCloud](https://github.com/wasmCloud/wasmCloud/releases)
and repackages each as a platform-specific Python wheel.

A thin Python entry point (`console_scripts`) delegates to the native binary,
so `wash` is available on `PATH` after install.

## Development

python, uv, & just are needed. Here is a quick setup example on Linux:

```bash
tdnf install -y python3 python3-pip
python3 -m pip install uv
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
uv tool install rust-just
```

## License

This package redistributes wash under its
[Apache-2.0](https://github.com/wasmCloud/wasmCloud/blob/main/LICENSE) license.
