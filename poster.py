import math
import svgwrite
import csv
import os
import colour
from datetime import datetime

# page setup
PAGE_WIDTH = 42
PAGE_HEIGHT = 29.7
GRAPH_SCALE = .9
GRAPH_WIDTH = PAGE_WIDTH * GRAPH_SCALE
GRAPH_HEIGHT = PAGE_HEIGHT * GRAPH_SCALE
OFFSET_X = (PAGE_WIDTH - GRAPH_WIDTH) / 2
OFFSET_Y = (PAGE_HEIGHT - GRAPH_HEIGHT) / 2

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


def entry_to_minutes(entry):
    time = datetime.strptime(entry[1].split(",")[1], " %H:%M")
    absolute = time.hour * 60 + time.minute
    return absolute


def entry_to_color(entry, start_date, end_date, artists):
    if entry[2] not in artists:
        date_progress = (entry_to_date(entry) - start_date) / (end_date - start_date)
        h = H_MIN + (H_MAX - H_MIN) * date_progress
        a = C * math.cos(math.pi / 180 * h)
        b = C * math.sin(math.pi / 180 * h)
        artists[entry[2]] = colour.XYZ_to_sRGB(colour.Oklab_to_XYZ([L, a, b]))
    return artists[entry[2]]


def add_entry(dwg, previous, current, successor, start_date, end_date, artists):
    current_date = entry_to_date(current)
    current_start = entry_to_minutes(current)
    current_end = min([entry_to_minutes(current) + DURATION_BASE, 1440])
    if previous and entry_to_date(previous) == current_date and current_start - entry_to_minutes(
            previous) <= DURATION_MAX:
        pass  # TODO: no start cap
    if successor and entry_to_date(current) == current_date and entry_to_minutes(
            successor) - current_start <= DURATION_MAX:
        current_end = entry_to_minutes(successor)
        # TODO: no end cap
    color = entry_to_color(current, start_date, end_date, artists)
    x = f"{OFFSET_X + GRAPH_WIDTH * (current_date - start_date).days / ((end_date - start_date).days + 1)}cm"
    y = f"{OFFSET_Y + GRAPH_HEIGHT * current_start / 1440}cm"
    width = f"{GRAPH_WIDTH / ((end_date - start_date).days + 1)}cm"
    height = f"{GRAPH_HEIGHT * (current_end - current_start) / 1440}cm"
    # print(f"{x=} {y=} {width=} {height=}")
    dwg.add(dwg.rect(insert=(x, y), size=(width, height),
                     fill=f"rgb({int(color[0] * 255)},{int(color[1] * 255)},{int(color[2] * 255)})"))


def generate_poster(src):
    dwg = svgwrite.Drawing(src.split('.')[0] + '.svg', width=f"{PAGE_WIDTH}cm", height=f"{PAGE_HEIGHT}cm")
    artists = dict()

    with open(src, "r", encoding="utf8") as file:
        entries = [None] + list(csv.reader(file))[1:] + [None]
        start_date = entry_to_date(entries[-2])
        end_date = entry_to_date(entries[1])
        for i in range(len(entries) - 2, 1, -1):
            add_entry(dwg, entries[i + 1], entries[i], entries[i - 1], start_date, end_date, artists)
    dwg.save()


if __name__ == '__main__':
    files = [x for x in os.listdir() if x.endswith('.csv')]
    for file in files:
        generate_poster(file)
