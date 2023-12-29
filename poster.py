import math
import svgwrite
import csv
import os
import colour
from datetime import datetime


# page setup
PAGE_WIDTH = 42
PAGE_HEIGHT = 29.7
GRAPH_SCALE = .8
GRAPH_WIDTH = PAGE_WIDTH * GRAPH_SCALE
GRAPH_HEIGHT = PAGE_HEIGHT * GRAPH_SCALE

# color setup
L = .75
C = .125
H_MIN = 0
H_MAX = 320
B_COLOR = None

# line setup
DURATION_BASE = 5
DURATION_MAX = 10
LINE_EXPANSION = 1.3
CORNER_RADIUS = .3


def entry_to_date(entry):
    return datetime.strptime(entry[1].split(",")[0], "%d %b %Y")


def entry_to_time(entry):
    return datetime.strptime(entry[1].split(",")[1], " %H:%M")


def entry_to_color(entry, start_date, end_date, artists):
    if entry[2] not in artists:
        date_progress = (entry_to_date(entry) - start_date) / (end_date - start_date)
        h = H_MIN + (H_MAX - H_MIN) * date_progress
        a = C * math.cos(math.pi/180 * h)
        b = C * math.sin(math.pi/180 * h)
        artists[entry[2]] = colour.XYZ_to_sRGB(colour.Oklab_to_XYZ([L, a, b]))
    return artists[entry[2]]


def add_entry(dwg, previous, current, next, start_date, end_date, artists):
    color = entry_to_color(current, start_date, end_date, artists)


def generate_poster(src):
    dwg = svgwrite.Drawing(src.split('.')[0] + '.svg')
    artists = dict()

    with open(src, "r", encoding="utf8") as file:
        entries = [None] + list(csv.reader(file))[1:] + [None]
        start_date = entry_to_date(entries[-2])
        end_date = entry_to_date(entries[1])
        for i in range(len(entries) - 2, 1, -1):
            add_entry(dwg, entries[i-1], entries[i], entries[i+1], start_date, end_date, artists)
    dwg.save()


if __name__ == '__main__':
    files = [x for x in os.listdir() if x.endswith('.csv')]
    for file in files:
        generate_poster(file)
