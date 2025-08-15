import math
import pathlib

from openpyxl import load_workbook

from .connection import Connection
from .node import Node
from .path import Path


class MFN:
    def __init__(self, path: str | pathlib.Path):
        """
        Internal representation of a Multi Floor Network Excel Schema file.

        :param path: the path to the Excel file in MFN format
        """

        self.path = path

        self.nodes = []
        self.paths = []
        self.connections = []

        wb = load_workbook(path, read_only=True)

        for sheet in ["NetworkNodes", "NetworkPaths", "NetworkConnections"]:
            if sheet not in wb.sheetnames:
                raise ValueError(f"MFN file needs a sheet called '{sheet}'")

        for row in wb["NetworkNodes"].iter_rows(min_row=4, values_only=True):
            # reading excel sometimes moves integers a little (for some reason), correct this
            self.nodes.append(Node(*[round(x) if isinstance(x, float) and math.isclose(round(x), x, rel_tol=1e-9) else x
                                     for x in row[:7]]))

        for row in wb["NetworkPaths"].iter_rows(min_row=4, values_only=True):
            self.paths.append(Path(*row))

        for row in wb["NetworkConnections"].iter_rows(min_row=4, values_only=True):
            self.connections.append(Connection(*row))
