"""
File Optimizer for PaddleOCR Document Parsing

Compresses and optimizes large image files to meet size requirements,
preserving EXIF orientation and safely converting color modes.

Usage:
    python optimize_file.py input.png output.jpg --quality 85
    python optimize_file.py input.tif output.jpg --target-size 10
"""

import argparse
import math
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib import configure_stdio_utf8

configure_stdio_utf8()

DEFAULT_QUALITY = 85
DEFAULT_TARGET_SIZE_MB = 20.0
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")
SUPPORTED_FORMATS_DISPLAY = ", ".join(
    e.lstrip(".").upper() for e in SUPPORTED_EXTENSIONS
)


def _arg_quality(value: str) -> int:
    q = int(value)
    if q < 1 or q > 100:
        raise argparse.ArgumentTypeError("quality must be between 1 and 100 inclusive")
    return q


def _arg_positive_mb(value: str) -> float:
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise argparse.ArgumentTypeError(
            "target size must be a finite number greater than 0"
        )
    return v


def _normalize_to_8bit_l(img):
    """Safely normalize 16-bit / integer / float grayscale images to 8-bit 'L'."""
    extrema = img.getextrema()
    if isinstance(extrema, tuple) and len(extrema) == 2:
        lo, hi = extrema
        if hi > lo:
            scale = 255.0 / (hi - lo)
            return img.point(lambda px: int((px - lo) * scale)).convert("L")
    return img.convert("L")


def _prepare_image_mode(img, output_suffix: str):
    """Convert any PIL image mode into a mode safe for the target output format."""
    from PIL import Image

    suffix = output_suffix.lower()
    no_alpha_format = suffix in (".jpg", ".jpeg", ".bmp")

    if img.mode.startswith("I") or img.mode == "F":
        img = _normalize_to_8bit_l(img)

    if no_alpha_format:
        if img.mode in ("RGBA", "LA", "PA") or (
            img.mode == "P" and "transparency" in img.info
        ):
            rgba = img.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[-1])
            return background
        if img.mode not in ("RGB", "L"):
            return img.convert("RGB")
        return img

    # Formats supporting alpha (PNG, WebP, TIFF)
    if img.mode == "PA":
        return img.convert("RGBA")
    if img.mode not in ("RGB", "RGBA", "L", "LA", "P", "1"):
        return img.convert("RGB")
    return img


def _atomic_save(image, output_path: Path, save_kwargs: dict) -> float:
    """Save image atomically via a sibling temp file to prevent in-place corruption."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{output_path.stem}_",
        suffix=output_path.suffix or ".tmp",
        dir=str(output_path.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        image.save(tmp_path, **save_kwargs)
        size_mb = tmp_path.stat().st_size / (1024 * 1024)
        os.replace(tmp_path, output_path)
        return size_mb
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def optimize_image(
    input_path: Path,
    output_path: Path,
    quality: int = DEFAULT_QUALITY,
    max_size_mb: float = DEFAULT_TARGET_SIZE_MB,
) -> None:
    """Optimize image file by applying EXIF orientation, converting mode, and resizing."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("ERROR: Pillow not installed. Install with: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    if input_path.stat().st_size == 0:
        raise ValueError("Input file is empty (0 bytes); nothing to optimize")

    original_size = input_path.stat().st_size / (1024 * 1024)
    print(f"Optimizing image: {input_path}")
    print(f"Original size: {original_size:.2f}MB")

    # Open, transpose EXIF orientation, and copy into memory so the file handle closes
    # cleanly before writing (critical for Windows in-place overwrite).
    with Image.open(input_path) as raw_img:
        transposed = ImageOps.exif_transpose(raw_img)
        img = transposed.copy()

    print(f"Dimensions (EXIF-normalized): {img.size[0]}x{img.size[1]} (mode={img.mode})")

    img = _prepare_image_mode(img, output_path.suffix)

    suffix = output_path.suffix.lower()
    save_kwargs: dict = {"optimize": True}
    if suffix in (".jpg", ".jpeg", ".webp"):
        save_kwargs["quality"] = quality

    new_size = _atomic_save(img, output_path, save_kwargs)

    scale_factor = 0.9
    while new_size > max_size_mb and scale_factor >= 0.4:
        new_width = int(img.size[0] * scale_factor)
        new_height = int(img.size[1] * scale_factor)
        if new_width < 1 or new_height < 1:
            print(
                f"Cannot shrink to valid dimensions at scale {scale_factor:.2f} "
                f"(would be {new_width}x{new_height}); stopping resize loop."
            )
            break

        print(f"Resizing to {new_width}x{new_height} (scale: {scale_factor:.2f})")
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        new_size = _atomic_save(resized, output_path, save_kwargs)
        scale_factor -= 0.1

    print(f"Optimized size: {new_size:.2f}MB")
    pct = (original_size - new_size) / original_size * 100
    print(f"Reduction: {pct:.1f}%")

    if new_size > max_size_mb:
        print(f"\nWARNING: File still larger than {max_size_mb}MB", file=sys.stderr)
        print("Consider: --quality 70, smaller resolution, or --file-url", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Optimize image files for PaddleOCR document parsing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python optimize_file.py input.png output.jpg --quality 85
  python optimize_file.py scan.tif output.jpg --target-size 10

Supported formats:
  Images: {SUPPORTED_FORMATS_DISPLAY}
        """,
    )

    parser.add_argument("input", help="Input image file path")
    parser.add_argument("output", help="Output image file path")
    parser.add_argument(
        "--quality",
        type=_arg_quality,
        default=DEFAULT_QUALITY,
        help="JPEG/WebP quality (1-100, default: %(default)s)",
    )
    parser.add_argument(
        "--target-size",
        type=_arg_positive_mb,
        default=DEFAULT_TARGET_SIZE_MB,
        help="Target maximum size in MB (default: %(default)s)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(
            f"ERROR: Unsupported file format: {ext} (supported: {SUPPORTED_FORMATS_DISPLAY})",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        optimize_image(input_path, output_path, args.quality, args.target_size)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nOptimized file saved to: {output_path}")


if __name__ == "__main__":
    main()
