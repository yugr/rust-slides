#!/usr/bin/python3

# Plots AA precision results.

import argparse
import atexit
import multiprocessing
import os
import os.path
import re
import shutil
import subprocess
import statistics
import sys
import tempfile
from typing import NoReturn

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

ME = os.path.basename(__file__)
DEFAULT_VALUE = -0.1

data = {
    "rustc": 81 - 83,
    "SpacetimeDB": 81 - 83,
    "bevy": 67 - 72,
    "meilisearch": 41 - 47,
    "nalgebra": 30 - 66,
    "oxipng": 99 - 99,
    "rav1e": 87 - 89,
#    "rebar": 82 - 88,
    "ruff": 76 - 80,
#    "rust_serialization_benchmark": 75 - 78,
#    "rustc-perf": 83 - 84,
    "tokio": 82 - 87,
    "uv": 87 - 87,
    "veloren": 55 - 57,
    "zed": 78 - 79,
}

font_size = 20
plt.rc("font", size=font_size)

fig, ax = plt.subplots(figsize=(3 * (len(data) + 1), 15), layout="constrained")

colors = {}
legend_handles = {}
# something like 12 benchmarks should take up 80% of space between groups
width = 0.8 / 12

for i, (name, value) in enumerate(data.items()):
    color = colors.setdefault(name, cm.tab20(len(colors) / 20))
    rect = ax.bar(
        width * i,
        value,
        width,
        label=name,
        color=color,
    )
    legend_handles.setdefault(name, rect)
    ax.bar_label(rect, padding=3, fmt="%.1f")

ax.set_ylabel("% change")
ax.set_ylim(-50, 5)
ax.legend(ncols=3, handles=legend_handles.values())
plt.show()
fig.savefig("plot.png")
