"""Where the document set lives, and the numbers that define its standard.

Nothing else in this toolkit hard-codes a path or a size. Set these, then every other
tool works on your set. Override the root with the DOCSET_ROOT environment variable so
one copy of the toolkit can serve several document sets.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------------------- paths
DOCSET_ROOT = os.environ.get("DOCSET_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# Administrative output, kept out of the delivered tree's way but inside the set so it
# travels with it. Verification must skip this directory by name.
ADMIN_DIR = os.path.join(DOCSET_ROOT, "_admin")

# Scratch, backups and evidence. MUST be skipped by every verification walk -- backups
# in the live tree are what made a count check report 98 documents instead of 73.
WORK_DIR = os.path.join(DOCSET_ROOT, "_tools", "work")

# Torn-down material. Never delete: archive with a reason code.
ARCHIVE_DIR = os.path.join(DOCSET_ROOT, "99_Archive")

# Directories a verification walk must not descend into.
SKIP_TOP = {".git", "_tools", "_admin", "_reorg_work"}

# --------------------------------------------------------------------------- units
# Anchors, so every number in the standard is checkable arithmetic.
PT_PER_INCH = 72.0
MM_PER_PT = 25.4 / 72.0            # 0.35278 mm

A4_WIDTH_PT = 595.276              # 210 mm
A4_HEIGHT_PT = 841.890             # 297 mm

# --------------------------------------------------------------------------- layout
PAGE_MARGIN_CM = 2.2
TEXT_COLUMN_PT = 470.551           # 16.6 cm -- the widest a figure may sit at
FIGURE_CAP_PT = 456.693            # 16.11 cm -- the design standard's figure cap
EMU_PER_PT = 12700                 # for wp:extent / a:ext edits

# --------------------------------------------------------------------------- type
# The floor is the smallest legible printed size; the target leaves margin for the
# instrument's own error. A figure landing between them is undecidable, not passing.
MIN_ONPAGE_PT = 6.0
TARGET_ONPAGE_PT = 6.5
INSTRUMENT_TOLERANCE_PT = 0.06

# --------------------------------------------------------------------------- render
# Page-render resolution. MUST NOT exceed the embedded raster's resolution, or the
# render up-samples and the classifier flips glyph class -- a 38 % error.
# Sweep these and confirm stability before trusting any reading.
DPI_SWEEP = (150, 200, 300, 400, 600, 900)
DEFAULT_PAGE_DPI = 200

# Glyph-metric fallbacks, used ONLY when a figure's own lines cannot resolve the class.
X_HEIGHT_RATIO = 0.52
CAP_HEIGHT_RATIO = 0.72


# ------------------------------------------------------------------- identity
# Who the cover says this is. MUST be set per document set -- these were once
# hard-coded inside the cover builder, which would stamp one client's name onto
# another client's documents.
BRAND_NAME = os.environ.get("DOCSET_BRAND") or "Your Company"
DOCSET_TITLE = os.environ.get("DOCSET_TITLE") or "Desk Research"  # SET THIS
