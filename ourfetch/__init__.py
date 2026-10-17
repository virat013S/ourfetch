"""ourfetch — the fetch for every terminal. Linux, macOS, Windows."""
from .core import (ACCENT, BG, BLOCKS, DEFAULTS, DIM, FG, LOGOS, TOKEN_COLORS,
                   brand_color, colors_line, compose, config_dir, config_path,
                   gather, image_to_ansi, info_lines, intro_bar, load_config,
                   logo_for, main, os_id, save_config, set_image, stream,
                   sys_name)

__version__ = "1.0.0"
