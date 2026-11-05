#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2026 Outlast-Headbob-Remover
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Outlast Head Bob Remover
==========================

Entry point for the Outlast-Headbob-Remover project.

Runs the graphical patcher (tkinter) or the command-line interface
available in patcher/Outlast-HeadBob-Remover.py.

Usage:
    python main.py                 # opens the patcher GUI
    python main.py --cli ...       # forwards arguments to the patcher

License: MIT (see LICENSE in the project root).
"""

import os
import subprocess
import sys

PATCHER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patcher")
PATCHER_SCRIPT = os.path.join(PATCHER_DIR, "Outlast-HeadBob-Remover.py")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # If the user passed CLI arguments, forward them directly to the patcher.
    if argv:
        cmd = [sys.executable, PATCHER_SCRIPT] + argv
    else:
        cmd = [sys.executable, PATCHER_SCRIPT]
    try:
        return subprocess.call(cmd, cwd=PATCHER_DIR)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
