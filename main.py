#!/usr/bin/env python3
"""Entry point for the news-image-20261117 submission.

Draws the front page with render.py and writes entry.png into
$MAKEFUN_OUTPUT_DIR (default /output). No network, no inputs, deterministic.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import main

if __name__ == "__main__":
    main()
