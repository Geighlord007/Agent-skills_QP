#!/usr/bin/env python3
"""
Image QA for translated documents.

Extracts embedded images from DOCX/PPTX and checks if they may contain
source-language text that needs localization.

Usage:
    python qa_images.py input.docx output_dir/
    python qa_images.py input.pptx output_dir/

Outputs:
- Extracted images to output_dir/
- QA report listing images that may need text localization
"""
import sys
import os
from pathlib import Path
from zipfile import ZipFile


def extract_images_docx(docx_path, out_dir):
    """Extract images from DOCX (which is a ZIP file)."""
    images = []
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with ZipFile(docx_path, 'r') as zf:
        for name in zf.namelist():
            if name.startswith('word/media/'):
                data = zf.read(name)
                filename = Path(name).name
                target = out_path / filename
                target.write_bytes(data)
                images.append({
                    'source': 'docx',
                    'archive_path': name,
                    'saved_to': str(target),
                    'size': len(data)
                })

    return images


def extract_images_pptx(pptx_path, out_dir):
    """Extract images from PPTX (which is a ZIP file)."""
    images = []
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with ZipFile(pptx_path, 'r') as zf:
        for name in zf.namelist():
            if name.startswith('ppt/media/'):
                data = zf.read(name)
                filename = Path(name).name
                target = out_path / filename
                target.write_bytes(data)
                images.append({
                    'source': 'pptx',
                    'archive_path': name,
                    'saved_to': str(target),
                    'size': len(data)
                })

    return images


def identify_text_heavy_images(images):
    """Identify images likely to contain text (screenshots, diagrams, charts)."""
    # Simple heuristic: check file extension and size
    text_heavy_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    candidates = []

    for img in images:
        ext = Path(img['saved_to']).suffix.lower()
        if ext in text_heavy_exts and img['size'] > 1024:
            candidates.append(img)

    return candidates


def main():
    if len(sys.argv) < 3:
        print("Usage: python qa_images.py <input.docx|pptx> <output_dir/>")
        sys.exit(1)

    input_path = sys.argv[1]
    out_dir = sys.argv[2]
    ext = Path(input_path).suffix.lower()

    if ext == '.docx':
        images = extract_images_docx(input_path, out_dir)
    elif ext == '.pptx':
        images = extract_images_pptx(input_path, out_dir)
    else:
        print(f"Unsupported format: {ext}")
        sys.exit(1)

    candidates = identify_text_heavy_images(images)

    print("=" * 60)
    print("IMAGE QA REPORT")
    print("=" * 60)
    print(f"Document: {input_path}")
    print(f"Total images: {len(images)}")
    print(f"Text-heavy candidates: {len(candidates)}")
    print(f"Output dir: {out_dir}")
    print()

    if images:
        print("Extracted images:")
        for img in images:
            print(f"  {Path(img['saved_to']).name} ({img['size']} bytes)")
        print()

    if candidates:
        print("⚠️  Images that MAY contain source-language text:")
        print("   (Check these manually or with OCR)")
        for img in candidates:
            print(f"  - {Path(img['saved_to']).name}")
        print()
        print("Reminder: Do not automatically localize images unless the user asks.")
    else:
        print("✅ No images found, or none appear text-heavy.")

    print("=" * 60)


if __name__ == "__main__":
    main()
