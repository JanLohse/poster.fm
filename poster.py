import math
import csv
import os
import colour
from datetime import datetime
from fpdf import FPDF

# page setup
PAGE_WIDTH = 420
PAGE_HEIGHT = 297
GRAPH_SCALE = .9
GRAPH_WIDTH = PAGE_WIDTH * GRAPH_SCALE
GRAPH_HEIGHT = PAGE_HEIGHT * GRAPH_SCALE
OFFSET_X = (PAGE_WIDTH - GRAPH_WIDTH) / 2
OFFSET_Y = (PAGE_HEIGHT - GRAPH_HEIGHT) / 2

# color setup
L = .66
C = .125
H_MIN = 0
H_MAX = 320
B_COLOR = None

# line setup
DURATION_BASE = 7
DURATION_MAX = 15
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
        rgb = colour.XYZ_to_sRGB(colour.Oklab_to_XYZ([L, a, b]))
        artists[entry[2]] = [min([255, max([0, int(i * 255)])]) for i in rgb]
    return artists[entry[2]]


def add_entry(pdf, previous, current, successor, start_date, end_date, artists):
    current_date = entry_to_date(current)
    current_start = entry_to_minutes(current)
    current_end = min([entry_to_minutes(current) + DURATION_BASE, 1440])
    if previous and entry_to_date(previous) == current_date and current_start - entry_to_minutes(
            previous) <= DURATION_MAX:
        pass  # TODO: no start cap
    if successor and entry_to_date(current) == current_date and 0 <= entry_to_minutes(
            successor) - current_start <= DURATION_MAX:
        current_end = entry_to_minutes(successor)
        # TODO: no end cap
    color = entry_to_color(current, start_date, end_date, artists)
    x = OFFSET_X + GRAPH_WIDTH * (current_date - start_date).days / ((end_date - start_date).days + 1)
    y = OFFSET_Y + GRAPH_HEIGHT * current_start / 1440
    w = GRAPH_WIDTH / ((end_date - start_date).days + 1)
    h = GRAPH_HEIGHT * (current_end - current_start) / 1440
    pdf.set_fill_color(color)
    if h < 0:
        print(x, y, w, h)
    pdf.rect(x=x, y=y, w=w, h=h, style='F')


def generate_poster(src):
    pdf = FPDF(unit='mm')
    pdf.set_margins(left=OFFSET_X, top=OFFSET_Y)
    if PAGE_WIDTH > PAGE_HEIGHT:
        pdf.add_page('L', (PAGE_HEIGHT, PAGE_WIDTH))
    else:
        pdf.add_page('P', (PAGE_HEIGHT, PAGE_WIDTH))

    artists = dict()

    with open(src, "r", encoding="utf8") as file:
        entries = [None] + list(csv.reader(file))[1:] + [None]
        start_date = entry_to_date(entries[-2])
        end_date = entry_to_date(entries[1])
        for i in range(len(entries) - 2, 1, -1):
            add_entry(pdf, entries[i + 1], entries[i], entries[i - 1], start_date, end_date, artists)
    pdf.output(src.split('.')[0] + '.pdf')

if __name__ == '__main__':
    files = [x for x in os.listdir() if x.endswith('.csv')]
    for file in files:
        generate_poster(file)
