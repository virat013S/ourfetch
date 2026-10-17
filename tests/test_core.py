"""ourfetch tests — portable core, every OS. No network, no runtime deps."""
from __future__ import annotations

import io
import os
import struct
import zlib

import pytest

from ourfetch import __version__
from ourfetch import core


def test_meta():
    assert __version__ == "1.0.0"


def test_logo_count():
    assert len(core.LOGOS) == 23
    assert set(core.TOKEN_COLORS) == set(core.LOGOS) - {"generic"}


# ------------------------------------------------------------- the flying bar

def test_flying_bar(monkeypatch):
    monkeypatch.setattr(core, "_term_cols", lambda: 120)
    fake = io.StringIO()
    fake.isatty = lambda: True
    monkeypatch.setattr(core.sys, "stdout", fake)
    core.intro_bar(True)
    core.stream("typed line\n", 0.2, True, 0, line_ms=1, caret=True)
    sweep = fake.getvalue()
    assert "\x1b[2K" in sweep and "█" in sweep      # the intro comet
    assert "▊" in sweep and "\x1b[s" in sweep      # the caret flew ahead
    assert "╱" in sweep                            # slash trail
    fake2 = io.StringIO()
    fake2.isatty = lambda: True
    monkeypatch.setattr(core.sys, "stdout", fake2)
    core.stream("quiet line\n", 0.2, True, 0, line_ms=1, caret=False)
    assert "▊" not in fake2.getvalue()             # caret knob is honored


# ------------------------------------------------------------------- images

def _tiny_png(w: int, h: int) -> bytes:
    rows = bytearray()
    for y in range(h):
        rows.append(0)
        for _ in range(w):
            rows.extend((48, 40 + y * 8, 200))
    raw = bytes(rows)

    def chunk(tag: bytes, body: bytes) -> bytes:
        return (struct.pack(">I", len(body)) + tag + body +
                struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)   # RGB, 8-bit
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def test_png_decode_and_ansi(tmp_path):
    w, h, px = core._png_decode(_tiny_png(4, 4))
    assert (w, h) == (4, 4) and len(px) == 16
    assert px[0][3] == 255 and 0 <= px[0][0] <= 255
    p = tmp_path / "t.png"
    p.write_bytes(_tiny_png(6, 6))
    art = core.image_to_ansi(str(p), 8)
    assert len(art) >= 3 and all("38;2" in line for line in art)


# --------------------------------------------------------------- logo render

def test_logo_and_compose():
    for os_id, want in (("arch", 19), ("cachyos", 22), ("ubuntu", 20),
                        ("nixos", 20), ("macos", 17), ("windows", 16),
                        ("linuxmint", 19), ("void", 18),
                        ("definitely-not-an-os", 7)):
        art = core.logo_for(os_id)
        assert len(art) == want and all("\x1b[" in line for line in art)
    for key in core.LOGOS:                 # every logo renders colored
        assert all("\x1b[" in ln and ln.strip() for ln in core.logo_for(key)), key
    assert core.brand_color("cachyos") == (76, 195, 189)
    assert core.brand_color("opensuse-tumbleweed") == (0, 205, 0)
    assert core.brand_color("macos") == (229, 229, 229)
    info = core.info_lines([("os", "Test OS"), ("kernel", "6.9")], True,
                           (76, 195, 189))
    assert len(info) == 2 and "Test OS" in info[0]
    line = core.compose(art, info, core.colors_line(True), True)
    assert line.count("\x1b[0m") >= 2 and line.endswith("\x1b[0m\n")


def test_os_id_fallback(monkeypatch):
    monkeypatch.setattr(core, "_os_release", lambda: {})
    monkeypatch.setattr(core.platform, "system", lambda: "Darwin")
    assert core.os_id() == "macos"
    monkeypatch.setattr(core.platform, "system", lambda: "Windows")
    assert core.os_id() == "windows"
    assert core.logo_for("windows")        # both have real art


# ------------------------------------------------------------------ portable

def test_gather_shape():
    rows = core.gather()
    assert rows and all(isinstance(r, tuple) and len(r) == 2 for r in rows)
    labels = [r[0] for r in rows]
    assert "os" in labels and "term" in labels


def test_info_getters_survive_any_os():
    """The per-OS getters must return strings (maybe empty), never raise."""
    for fn in (core.mem_str, core.disk_str, core.uptime_str, core.cpu,
               core.packages, core.sys_name, core.user_host, core.shell_name,
               core.desktop, core.terminal_name, core.kernel, core.machine):
        got = fn()
        assert got is None or isinstance(got, str), fn
    assert core.sys_name()
    assert core._logo_key(core.os_id()) in core.LOGOS


# --------------------------------------------------------------- config + CLI

def test_config_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    cfg = core.load_config()
    assert cfg == dict(core.DEFAULTS)
    assert "bg" in core.DEFAULTS
    cfg["cols"] = 44
    assert core.save_config(cfg)
    assert core.load_config()["cols"] == 44
    assert core.image_path() is None


def test_adopts_vitro_config(monkeypatch, tmp_path):
    """One-time migration: vitro's fetch setup lives on with us."""
    import json
    (tmp_path / "vitro").mkdir()
    cfg = {"cols": 44, "intro": False}
    (tmp_path / "vitro" / "fetch.json").write_text(json.dumps(cfg))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    got = core.load_config()
    assert got["cols"] == 44 and got["intro"] is False
    assert (tmp_path / "ourfetch" / "fetch.json").exists()


def test_set_image_command(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    src = tmp_path / "logo.png"
    src.write_bytes(_tiny_png(6, 6))
    assert core.main(["set-image", str(src)]) == 0
    assert core.load_config()["image"].endswith("image.png")
    assert core.image_path() is not None and core.image_path().exists()
    art = core.image_to_ansi(str(core.image_path()), 10)
    assert len(art) >= 3
    assert core.main(["set-image", str(tmp_path / "nope.png")]) == 1
    assert core.main(["clear-image"]) == 0
    assert core.image_path() is None


def test_stream_off_tty_is_instant(capsys):
    rc = core.main(["--no-anim"])
    out = capsys.readouterr().out
    assert rc == 0 and "os" in out and "\x1b[38;2;" in out


def test_logo_force_and_lists(capsys):
    assert core.main(["--logo", "kali", "--no-anim"]) == 0
    out = capsys.readouterr().out
    assert "term" in out                       # forced logo + info composed
    assert core.main(["logos"]) == 0
    assert "cachyos" in capsys.readouterr().out
    assert core.main(["logo", "arch"]) == 0
    assert "oooooo" in capsys.readouterr().out
