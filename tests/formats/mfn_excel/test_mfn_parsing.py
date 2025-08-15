import os
import pathlib

import pytest

from generalized_path_finding.formats.mfn_excel.connection import Connection
from generalized_path_finding.formats.mfn_excel.mfn import MFN
from generalized_path_finding.formats.mfn_excel.node import Node
from generalized_path_finding.formats.mfn_excel.path import Path

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


def test_parsing():
    mfn = MFN(current_path / "MFN_example.xlsx")

    assert mfn.nodes == [
        Node(name='1-E0', x_meter=1.5, y_meter=1.6, z_meter=0, X=150, Y=160, network='E0'),
        Node(name='2-E0', x_meter=2.3, y_meter=2.4, z_meter=0, X=230, Y=240, network='E0'),
        Node(name='3-E0', x_meter=3, y_meter=2.4, z_meter=0, X=300, Y=240, network='E0'),
        Node(name='1-E1', x_meter=1.5, y_meter=1.6, z_meter=0, X=150, Y=160, network='E1')]

    assert mfn.paths == [
        Path(name='Path_1A', origin_node_name='1-E0', destination_node_name='2-E0', network='E0', origin_id=1,
             dest_id=2, prio=1, speed_limit_mps=None, description=None, color='blue', controls=None, pedestrians=None,
             fleets='Roboter'),
        Path(name='Path_1B', origin_node_name='2-E0', destination_node_name='1-E0', network='E0', origin_id=2,
             dest_id=1, prio=1, speed_limit_mps=None, description=None, color='blue', controls=None, pedestrians=None,
             fleets='Roboter'),
        Path(name='Path_2A', origin_node_name='2-E0', destination_node_name='3-E0', network='E0', origin_id=2,
             dest_id=3, prio=2, speed_limit_mps=None, description=None, color='blue', controls=None, pedestrians=None,
             fleets='Roboter'),
        Path(name='Path_2B', origin_node_name='3-E0', destination_node_name='2-E0', network='E0', origin_id=3,
             dest_id=2, prio=None, speed_limit_mps=0.5, description=None, color='blue', controls=None,
             pedestrians=None, fleets='Roboter')]

    assert mfn.connections == [
        Connection(name='Connection1', origin_node_name='1-E0', destination_node_name='1-E1',
                   cal_trans_duration_seconds=90, origin_controls='Aufzugsname', origin_network='E0',
                   destination_network='E1', description=None, pedestrians='Besucher', fleets='Roboter | Besucher',
                   orientation='N', comment=None),
        Connection(name='Connection1', origin_node_name='1-E1', destination_node_name='1-E0',
                   cal_trans_duration_seconds=90, origin_controls='Aufzugsname', origin_network='E0',
                   destination_network='E1', description=None, pedestrians='Besucher', fleets='Roboter | Besucher',
                   orientation='N', comment=None)]


def test_missing_sheet():
    with pytest.raises(ValueError) as e:
        mfn = MFN(current_path / "MFN_missing_sheet.xlsx")
    assert "sheet" in str(e.value)
