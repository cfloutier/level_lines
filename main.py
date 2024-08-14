import argparse
import subprocess
from typing import Optional
from xml.sax import parse
from xml.sax.handler import ContentHandler
import cartopy.crs as ccrs

from pathlib import Path

from tools.fs import make_parent_dir


class Line:

    def __init__(self) -> None:
        self.points = []
        self.altitude = 0

class osm_parser(ContentHandler):

    def __init__(self) -> None:
        super().__init__()

        self.points = {}
        self.lines = []

        self.currentLine = None

    def startDocument(self):
        pass

    def startElement(self, name, attrs):

        if name == "osm":
            return
        elif name == "node":
            att = dict(attrs)
            self.points[att.get("id")] = (float(att.get("lat")), float(att.get("lon")))
            return
        elif name == "way":
            self.currentLine = Line()
            # print(name)
            # att = dict(attrs)
            # print(att)
        elif name == "nd":
            if not self.currentLine:
                raise Exception("error no current line")

            ref = attrs.get("ref")
            if not ref in self.points:
                raise Exception(f"point {ref} not found")
            point = self.points[ref]
            self.currentLine.points.append(point)
        elif name == "tag":
            att = dict(attrs)
            if att["k"] == "ele":
                self.currentLine.altitude = float(att["v"])
            # print(att)

        else:
            print(name)
            return

    def characters(self, content):
        # print(f"characters {content}")
        pass

    def endElement(self, name):
        # print(f"endElement {name}")

        if name == "way":
            if not self.currentLine:
                raise Exception("error no current line")
            self.lines.append(self.currentLine)
            self.currentLine = None

    def endDocument(self):
        pass


def osm_file(name):
    file_path = Path(__file__).parent / "result" / f"{name}.osm"
    return file_path


def svg_file(name):
    file_path = Path(__file__).parent / "result" / f"{name}.svg"
    return file_path


def callsrt2osm(name, min_lat, min_lon, max_lat, max_lon, step):

    exe_path = Path(__file__).parent / "Srtm2Osm" / "Srtm2Osm.exe"

    if not exe_path.exists():
        print(f"{exe_path} not found")
        return False

    output = osm_file(name)
    make_parent_dir(output)

    command_line = [
        str(exe_path.resolve()),
        "-bounds1",
        min_lat,
        min_lon,
        max_lat,
        max_lon,
        "-o",
        str(output),
        "-step",
        str(step),
    ]

    # command_line = [str(exe_path.resolve()), "-h"]
    print(command_line)

    # subprocess.run(["ls", "-l"])
    subprocess.run(command_line, check=False)

    return output.exists()


def parse_osm(name):

    _osm_file = osm_file(name)
    if not _osm_file.exists():
        return False

    parser = osm_parser()
    parse(_osm_file, parser)
    return parser.lines


def center_lat_lon(min_lat, min_lon, max_lat, max_lon):

    src_crs = ccrs.PlateCarree()
    dst_crs = ccrs.Gnomonic(central_latitude=min_lat, central_longitude=min_lon)

    p1 = dst_crs.transform_point(min_lon, min_lat, src_crs=src_crs)
    p2 = dst_crs.transform_point(max_lon, max_lat, src_crs=src_crs)

    center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    lon_lat = src_crs.transform_point(center[0], center[1], src_crs=dst_crs)
    return (float(lon_lat[1]), float(lon_lat[0]))


def convert_to_meters(src_lines: list[Line], center):

    if not src_lines:
        return None

    src_crs = ccrs.PlateCarree()
    dst_crs = ccrs.Gnomonic(central_latitude=center[0], central_longitude=center[1])

    new_lines = []

    min_x = None
    min_y = None
    max_x = None
    max_y = None

    for line in src_lines:
        new_line = Line()
        new_line.altitude = line.altitude

        for p in line.points:
            x_y = dst_crs.transform_point(p[1], p[0], src_crs=src_crs)

            # test = dst_crs.transform_point(center[1], center[0], src_crs=src_crs)
            new_line.points.append(x_y)

            if not min_x:
                min_x = x_y[0]
                max_x = x_y[0]
                min_y = x_y[1]
                max_y = x_y[1]
            else:
                if x_y[0] < min_x:
                    min_x = x_y[0]
                if x_y[0] > max_x:
                    max_x = x_y[0]
                if x_y[1] < min_y:
                    min_y = x_y[1]
                if x_y[1] > max_y:
                    max_y = x_y[1]

        new_lines.append(new_line)

    new_width = 200
    total_width = max_x - min_x
    scale = new_width / total_width

    for line in new_lines:
        for index, point in enumerate(line.points):
            line.points[index] = (5 + (point[0] - min_x) * scale, 292 - (point[1] - min_y) * scale)

    return new_lines


class SvgFormater:

    def __init__(self) -> None:
        self.content = ""

    def start_svg(self, name, width_mm = 210, height_mm=297):
        self.content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{width_mm}mm" height="{297}mm" viewBox="0 0 {width_mm} {297}" version="1.1" id="{name}" xml:space="preserve" inkscape:version="1.3.2 (091e20e, 2023-11-25, custom)" sodipodi:docname="template.svg"
  xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
  xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
  xmlns="http://www.w3.org/2000/svg"
  xmlns:svg="http://www.w3.org/2000/svg">
"""

    def begin_group(self, group_name):
        self.content += f'    <g id="{group_name}">\n'

    def end_group(self):
        self.content += "    </g>\n"

    def add_line(self, line: Line, id, stroke_width=0.1):
        index_point = 0
        coords = ""

        prev_point: Optional[tuple] = None
        style = f"fill:none;stroke:#000000;stroke-width:{stroke_width};stroke-linecap:square;stroke-linejoin:bevel;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"

        for point in line.points:

            if not prev_point:
                coords += f"m {point[0]:.9f},{point[1]:.9f} "
                prev_point = point
            else:
                coords += f"{point[0]-prev_point[0]:.9f},{point[1]-prev_point[1]:.9f} "
                prev_point = point

            index_point += 1

        self.content += f'      <path id="{id}" d="{coords}" style="{style}"/>'

    def save(self, file_path):
        self.content += "</svg>"

        with open(file_path, encoding="utf8", mode="w") as f:
            f.write(self.content)



def save_to_svg(lines: list[Line], name, sort_by_h, big_lines_step):

    file_path = svg_file(name)

    print(f"saving to {file_path}")

    heights = {}

    svg = SvgFormater()
    svg.start_svg(name)



    # group per altitudes
    for line in lines:
        if line.altitude in heights:
            height_grp = heights[line.altitude]
            height_grp.append(line)
        else:
            height_grp = [line]
            heights[line.altitude] = height_grp

    svg.begin_group(name)

    # content += f'    <g id="{name}">\n'

    for altitude, lines in heights.items():
        # content += f'    <g id="alt_{altitude}">\n'
        index = 1
        if sort_by_h:
            svg.begin_group(f"alt_{altitude}")

        for line in lines:
            if not line.points:
                continue

            id = f"line_{altitude}_{index}"


            big_line = False

            if big_lines_step >= 0:
                big_line = altitude%big_lines_step == 0
                
            if big_line:
                svg.add_line(line, id, 0.3)
                svg.add_line(line, id, 0.3)
            else:
                svg.add_line(line, id, 0.1)
                
            index += 1

        if sort_by_h:
            svg.end_group()
      
    svg.end_group()

    svg.save(file_path)
   


def _setup_args():

    parser = argparse.ArgumentParser(
        prog="osm2svg",
        description="create a svg based on the osm file generated by Srtm2Osm",
    )

    parser.add_argument("name")

    parser.add_argument("min_lat")
    parser.add_argument("min_lon")
    parser.add_argument("max_lat")
    parser.add_argument("max_lon")


    parser.add_argument("-s", "--step", default=10)  # line every 10 meters

    parser.add_argument("--sort_by_height", action="store_true")
    parser.add_argument("--big_lines_step", default=-1)

    return parser.parse_args()


def main():
    args = _setup_args()

    min_lat = float(args.min_lat)
    min_lon = float(args.min_lon)
    max_lat = float(args.max_lat)
    max_lon = float(args.max_lon)

    if not callsrt2osm(args.name, args.min_lat, args.min_lon, args.max_lat, args.max_lon, args.step):
        print("error while creating file")
        return

    print("loading osm file")
    lines = parse_osm(args.name)
    if not lines:
        print("error parsing osm file")
        return

    # print(f"found {len(lines)} lines")
    center = center_lat_lon(min_lat, min_lon, max_lat, max_lon)
    print(f"center {center[0]}, {center[1]}")
    print("convert to page coords")
    lines = convert_to_meters(lines, center)

    save_to_svg(lines, args.name, bool(args.sort_by_height), int(args.big_lines_step))

    # print(center)


if __name__ == "__main__":
    main()
