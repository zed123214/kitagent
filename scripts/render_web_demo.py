"""Render the recorded workbench video as a README GIF using local FFmpeg."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, default=root / "docs/assets/equal-operator-demo.webm")
    parser.add_argument("--output", type=Path, default=root / "docs/assets/equal-operator-demo.gif")
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("FFmpeg is required; run this script in WSL with ffmpeg on PATH.")
    if not args.video.is_file():
        parser.error(f"Recorded video does not exist: {args.video}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kitagent-demo-palette-") as temporary:
        palette = str(Path(temporary) / "palette.png")
        filters = "fps=6,scale=1120:-1:flags=lanczos"
        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(args.video),
                "-vf",
                f"{filters},palettegen=max_colors=128:stats_mode=diff",
                palette,
            ],
            check=True,
        )
        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(args.video),
                "-i",
                palette,
                "-lavfi",
                f"{filters}[frame];[frame][1:v]paletteuse=dither=none:diff_mode=rectangle",
                "-loop",
                "0",
                str(args.output),
            ],
            check=True,
        )
    print(f"Rendered {args.output.name}: {args.output.stat().st_size / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    main()
