#!/usr/bin/env python3
"""Keep eza's output, highlighting Git repository roots in green."""

import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
from urllib.parse import unquote


LINK = re.compile(r"(\x1b\]8;;file://[^/]*)(.*?)(\x1b\\)(.*?)(\x1b\]8;;\x1b\\)")
SGR = re.compile(r"\x1b\[[0-9;]*m")


def highlight(match):
    opening, path, separator, label, closing = match.groups()
    marker = Path(unquote(path, errors="surrogateescape")) / ".git"
    if SGR.search(label) and (marker.is_dir() or marker.is_file()):
        label = "\x1b[1;32m" + SGR.sub("", label) + "\x1b[0m"
    return opening + path + separator + label + closing


def main():
    args = sys.argv[1:]
    option_end = args.index("--") if "--" in args else len(args)
    # Resolve automatic color against our stdout, not the pipe eza writes to.
    auto_color = "always" if sys.stdout.isatty() and "NO_COLOR" not in os.environ else "never"
    for index in range(option_end):
        if args[index] in ("--color=auto", "--colour=auto"):
            args[index] = args[index].replace("=auto", "=" + auto_color)
        elif (args[index] in ("--color", "--colour") and index + 1 < option_end
              and args[index + 1] == "auto"):
            args[index + 1] = auto_color
    defaults = ["--icons"]
    if sys.stdout.isatty():
        if "NO_COLOR" not in os.environ:
            defaults.append("--color=always")
        defaults.append(f"--width={shutil.get_terminal_size().columns}")
        options = args[:option_end]
        if not any(
            arg in ("--long", "--oneline", "--tree")
            or (arg.startswith("-") and not arg.startswith("--")
                and any(flag in arg for flag in "l1T"))
            for arg in options
        ):
            defaults.append("--grid")

    # Hyperlinks carry exact paths, including spaces, without parsing the layout.
    # Remove our links again unless the caller explicitly requested them.
    keep_links = "--hyperlink" in args
    with subprocess.Popen(
        ["eza", *defaults, "--hyperlink", *args], stdout=subprocess.PIPE,
        text=True, encoding="utf-8", errors="surrogateescape",
    ) as process:
        for line in process.stdout:
            line = LINK.sub(highlight, line)
            if not keep_links:
                line = re.sub(r"\x1b\]8;;.*?\x1b\\", "", line)
            sys.stdout.write(line)
        return process.wait()


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main())
