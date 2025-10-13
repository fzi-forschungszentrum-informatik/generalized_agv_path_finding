import os
import pathlib

import pytest

from generalized_path_finding.formats.mfn_excel.connection import Connection
from generalized_path_finding.formats.mfn_excel.fleet import Fleet
from generalized_path_finding.formats.mfn_excel.mfn import MFN
from generalized_path_finding.formats.mfn_excel.node import Node
from generalized_path_finding.formats.mfn_excel.path import Path

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


def test_parsing():
    mfn = MFN(current_path / "MFN_example.xlsx")

    assert mfn.nodes == [
        Node(name='1-E0', x_meter=1.5, y_meter=1.6, z_meter=0),
        Node(name='2-E0', x_meter=2.3, y_meter=2.4, z_meter=0),
        Node(name='3-E0', x_meter=3, y_meter=2.4, z_meter=0),
        Node(name='1-E1', x_meter=1.5, y_meter=1.6, z_meter=0)]

    assert mfn.paths == [
        Path(name='Path_1A', origin_node_name='1-E0', destination_node_name='2-E0', fleets='Roboter'),
        Path(name='Path_1B', origin_node_name='2-E0', destination_node_name='1-E0', fleets='Roboter'),
        Path(name='Path_2A', origin_node_name='2-E0', destination_node_name='3-E0', fleets='Roboter'),
        Path(name='Path_2B', origin_node_name='3-E0', destination_node_name='2-E0', fleets='Roboter')]

    assert mfn.connections == [
        Connection(name='Connection1', origin_node_name='1-E0', destination_node_name='1-E1',
                   cal_trans_duration_seconds=90, fleets='Roboter | Besucher'),
        Connection(name='Connection1', origin_node_name='1-E1', destination_node_name='1-E0',
                   cal_trans_duration_seconds=90, fleets='Roboter | Besucher')]

    assert mfn.fleets == [Fleet(name='Roboter', avg_speed_mps=0.5), Fleet(name='Besucher', avg_speed_mps=0.4)]


def test_missing_sheet():
    with pytest.raises(ValueError) as e:
        mfn = MFN(current_path / "MFN_missing_sheet.xlsx")
    assert "sheet" in str(e.value)


def test_parsing_with_different_order_and_additional_columns():
    mfn = MFN(current_path / "MFN_changed_order.xlsx")

    assert mfn.nodes == [
        Node(name='NodeA', x_meter=20.0, y_meter=30.0, z_meter=0),
        Node(name='NodeB', x_meter=50.0, y_meter=30.0, z_meter=0),
        Node(name='NodeC', x_meter=80.0, y_meter=30.0, z_meter=0)]