import os
import fcntl
from pathlib import Path
import pty
import re
import subprocess
import struct
import tempfile
import termios
import unittest


WRAPPER = Path(__file__).resolve().parents[1] / "shell" / "repo-ls.py"


class RepoListingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo with spaces"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "-c", "user.name=Test", "-c",
             "user.email=test@example.com", "commit", "--allow-empty", "-qm", "init"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "add", "-qb", "linked",
             str(self.root / "linked")], check=True,
        )
        (self.root / "ordinary").mkdir()
        (self.repo / "inside").mkdir()
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("NO_COLOR", "EZA_COLORS", "EXA_COLORS", "LS_COLORS")}
        self.env["TERM"] = "xterm-256color"

    def listing(self, *args):
        return subprocess.run(
            ["python3", str(WRAPPER), *args], cwd=self.root, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def test_only_repo_roots_are_green_including_worktrees(self):
        result = self.listing("-1", "--color=always")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"\x1b[1;32m'repo with spaces'\x1b[0m", result.stdout)
        self.assertIn(b"\x1b[1;32mlinked\x1b[0m", result.stdout)
        self.assertNotIn(b"\x1b[1;32mordinary", result.stdout)
        nested = self.listing("-1", "--color=always", str(self.repo))
        self.assertNotIn(b"\x1b[1;32minside", nested.stdout)

    def test_color_never_and_pipes_remain_plain(self):
        for args in [("-1",), ("-1", "--color=never")]:
            result = self.listing(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(b"\x1b", result.stdout)

    def test_arguments_and_exit_status_match_eza(self):
        for args in [("-la", "--color=never", "ordinary"), ("missing",)]:
            expected = subprocess.run(
                ["eza", "--icons", *args], cwd=self.root, env=self.env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            result = self.listing(*args)
            self.assertEqual(result.returncode, expected.returncode)
            self.assertEqual(result.stdout, expected.stdout)
            self.assertEqual(result.stderr, expected.stderr)

    def terminal_listing(self, command):
        master, slave = pty.openpty()
        try:
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
            result = subprocess.run(command, cwd=self.root, env=self.env, stdout=slave)
            # Fixtures are deliberately small enough to fit in the terminal buffer.
            output = os.read(master, 8192)
            self.assertEqual(result.returncode, 0)
            return output
        finally:
            os.close(slave)
            os.close(master)

    def test_terminal_layout_matches_eza(self):
        ansi = re.compile(rb"\x1b\[[0-9;]*m")
        for args in [[], ["-lh"], ["--tree", "--level=2"], ["-1"],
                     ["-1", "--color=auto", "--icons=auto"],
                     ["-1", "--colour", "auto", "--icons", "auto"]]:
            expected = self.terminal_listing(["eza", "--icons", *args])
            actual = self.terminal_listing(["python3", str(WRAPPER), *args])
            self.assertEqual(ansi.sub(b"", actual), ansi.sub(b"", expected))
            self.assertIn(b"\x1b[1;32m", actual)

    def test_no_color_in_terminal_and_hyperlink_opt_in(self):
        self.env["NO_COLOR"] = "1"
        output = self.terminal_listing(["python3", str(WRAPPER), "-1"])
        self.assertNotIn(b"\x1b", output)
        del self.env["NO_COLOR"]
        result = self.listing("-1", "--color=always", "--hyperlink")
        self.assertIn(b"\x1b]8;;file://", result.stdout)
        self.assertIn(b"\x1b[1;32mlinked", result.stdout)

    def test_sourced_alias_works_after_changing_directory(self):
        result = subprocess.run(
            ["bash", "--noprofile", "--norc", "-c",
             'shopt -s expand_aliases; source "$1"; cd "$2"; '
             'eval "ls -1 --color=always"', "bash",
             str(WRAPPER.with_name("aliases.bash")), str(self.root)],
            cwd="/", env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"\x1b[1;32mlinked", result.stdout)


if __name__ == "__main__":
    unittest.main()
