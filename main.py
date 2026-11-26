#!/usr/bin/env python3
"""Copy the front-page poster for Thursday, 26 November 2026 to
the output path.

The poster itself (frontpage.png, drawn in advance and checked by
eye) is part of this repository. This program only copies it, so it
needs nothing but the standard library: no drawing, no fonts, no
network. It writes /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png) and prints its size and sha256.
"""

import hashlib
import os
import shutil
import sys

IMAGE_NAME = "frontpage.png"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1024 * 1024


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, IMAGE_NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, OUTPUT_NAME)
    shutil.copyfile(src, dst)
    data = open(dst, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG file", file=sys.stderr)
        sys.exit(1)
    if len(data) > MAX_BYTES:
        print("entry.png exceeds 1 MiB: %d bytes" % len(data),
              file=sys.stderr)
        sys.exit(1)
    print("wrote %s (%d bytes, sha256 %s)"
          % (dst, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
