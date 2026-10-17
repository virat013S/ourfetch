# ourfetch

[![tests](https://github.com/virat013S/ourfetch/actions/workflows/tests.yml/badge.svg)](https://github.com/virat013S/ourfetch/actions/workflows/tests.yml)

**The fetch for every terminal.** System info next to your OS logo (or an
image you choose), typed out fast like someone showing off — with an intro
bar that sweeps and a caret that dashes ahead of the text. Linux, macOS,
Windows; kitty, alacritty, gnome-terminal, konsole, iterm2, windows
terminal, plain cmd… no terminal-specific features required.

```
$ ourfetch
     ▄▄▀▀▄                    user · mitsuki@arch-x8664
   ▄█▀▀  ▀▀█▄                  os   · CachyOS
  (your distro's fastfetch    kernel · 7.2.9 x86_64
   logo here — 23 of them)    shell · fish
                              wm · niri
                              cpu · Ryzen 9 9950X
                              mem · 9.4 / 87.7 GiB
                              uptime · 2d 5h 12m
```

## Installing

```sh
pipx install git+https://github.com/virat013S/ourfetch.git
# or classic:
python -m pip install --user git+https://github.com/virat013S/ourfetch.git
```

Then just run `ourfetch` in whatever terminal you already have open.

## Using it

| you type                     | what happens                              |
|------------------------------|-------------------------------------------|
| `ourfetch`                   | the fetch, animated (instant on pipes)     |
| `ourfetch --no-anim`         | instantly, for scripts                     |
| `ourfetch --cols 44`         | wider logo                                 |
| `ourfetch --logo kali`       | force any of the 23 logos, whatever the OS |
| `ourfetch logos`             | list every logo id                         |
| `ourfetch logo arch`         | preview one logo                           |
| `ourfetch set-image X.png`   | remember an image as the logo              |
| `ourfetch clear-image`       | back to the automatic OS logo              |
| `ourfetch --bg 24,24,28`     | blend color for images — your terminal bg  |
| `ourfetch --no-intro`        | skip the intro sweep                       |
| `ourfetch --no-caret`        | skip the flying caret                      |

The typing animation only runs on a real tty, so scripts and CI get plain
instant output automatically. `NO_COLOR` is respected everywhere.

## What it shows

user, OS (real PRETTY_NAME on linux, macOS version, Windows 10/11 after
build-number sniffing), kernel + arch, shell, wm/de, terminal, cpu, RAM,
disk, uptime and package count — each row only when it can be found on
that OS, no fake filler:

- **Linux** — /proc files, os-release, pacman · dpkg · rpm · apk counts
- **macOS** — sysctl (boottime, ram, cpu brand), vm_stat for used RAM
- **Windows** — ctypes for RAM + uptime, wmic for the cpu name, winget
  and Appx package count, msys/git-bash render fine too

## Logos

23 fastfetch-real logos ship included (tokens keep the original brand
colors): arch, cachyos, debian, ubuntu, fedora, manjaro, linuxmint,
endeavouros, pop, nixos, gentoo, opensuse, garuda, artix, kali, alpine,
void, elementary, linux, macos, windows, freebsd, plus a generic shard for
whatever else (compound ids fall back to their head:
opensuse-tumbleweed → opensuse). Set an image any time — `set-image` blends it against
your terminal's own background so it never looks pasted-on.

## Config

Knobs live in `~/.config/ourfetch/fetch.json`
(`%APPDATA%\ourfetch` on Windows) — `image`, `cols`, `anim`, `speed`,
`line_delay`, `intro`, `caret`, `bg`. Migrating from vitro? Your existing
vitro fetch setup is adopted on first run.

## License

MIT.
