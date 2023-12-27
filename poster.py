import svgwrite
import os


def entry_to_color(artist, date, start_date, end_date):
    pass


def generate_poster(src):
    dwg = svgwrite.Drawing(src.split('.')[0] + '.svg')
    dwg.save()


if __name__ == '__main__':
    files = [x for x in os.listdir() if x.endswith('.csv')]
    for file in files:
        generate_poster(file)
