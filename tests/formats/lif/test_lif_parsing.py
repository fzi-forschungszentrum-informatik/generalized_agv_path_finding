import json
import os
from pathlib import Path
from typing import TypeVar, Optional, Union, Tuple

import pytest

from generalized_path_finding.formats.lif import *
from generalized_path_finding.formats.lif import Node, OrientationType
from generalized_path_finding.formats.lif.camelserial import CamelSerial, is_optional_type, non_optional_type

current_path = Path(os.path.dirname(os.path.realpath(__file__)))


def normalize_json(json_str):
    return json.dumps(json.loads(json_str))


def dict_le(left: dict, right: dict) -> bool:
    # inefficient, because it logs all differences, while the presence of one already determines the result
    # But it's only used in tests and only suboptimal for failing tests, so it can stay like this
    return dict_minus(left, right) == []


def dict_minus(left, right, parent_key="") -> list[Tuple[str, str]]:
    differences = []

    if type(left) != type(right) and {type(left), type(right)} != {float, int}:
        differences.append((parent_key, "not of same type"))

    if isinstance(left, dict):  # Handle dictionaries
        for key, value in left.items():
            full_key = f"{parent_key}.{key}" if parent_key else key

            # Check if key is missing in the right dictionary
            if key not in right:
                differences.append((full_key, "missing"))
            else:
                # Recurse into nested structures
                differences.extend(dict_minus(value, right[key], full_key))

    elif isinstance(left, list):  # Handle lists
        for index, value in enumerate(left):
            full_key = f"{parent_key}[{index}]" if parent_key else f"[{index}]"

            # Check if the index exists in the right list
            if index >= len(right):
                differences.append((full_key, "missing in list"))
            else:
                # Recurse into nested structures
                differences.extend(dict_minus(value, right[index], full_key))

    else:  # Compare values directly
        if left != right:
            differences.append((parent_key, f"{left} != {right}"))

    return differences


debug = True
T = TypeVar("T", bound=CamelSerial)


def check_dict(dict_in: dict, cls: type[T]) -> T:
    obj = cls.from_camel_dict(dict_in)

    if debug:
        print("object:")
        print(obj)

    dict_out = obj.to_camel_dict()

    if debug:
        json_out = json.dumps(dict_out)
        print("back to json:")
        print(json_out)

    ok = dict_le(dict_in, dict_out)
    if not ok:
        print("dict difference:")
        print("\n".join(f"{key} ({reason})" for key, reason in dict_minus(dict_in, dict_out)))

    # checks for subset (additional optional arguments may be present)
    assert ok, "JSON should still have the same values after deserializing and serializing."

    if ok and debug:
        print("extra attributes in dict_out:")
        print("\n".join(f"{key} ({reason})" for key, reason in dict_minus(dict_out, dict_in)))

    return obj


def test_type_helpers():
    assert is_optional_type(Union[int, None])
    assert is_optional_type(int | None)
    assert is_optional_type(Optional[int])

    assert not is_optional_type(int)

    assert non_optional_type(Optional[int]) == int
    assert non_optional_type(int | None) == int
    assert non_optional_type(Union[int, None]) == int
    assert non_optional_type(int) == int

    assert non_optional_type(Union[int, list[int], None]) in [Union[int, list[int]], int | list[int]]


def test_node_conversion():
    json_in = """
    {
        "nodeId": "N1",
        "nodeName": "",
        "mapId": "map1",
        "nodePosition": {
            "x": 0.0,
            "y": 0.0
        },
        "vehicleTypeNodeProperties": [
            {
                "vehicleTypeId": "robot",
                "theta": 0.0,
                "actions": []
            }
        ]
    }
    """

    dict_in = json.loads(json_in)
    check_dict(dict_in, Node)


def test_missing_mandatory_fields():
    json_in = """
    {
        "nodeId": "N1",
        "nodeName": "",
        "mapId": "map1",
        "vehicleTypeNodeProperties": [
            {
                "vehicleTypeId": "robot",
                "theta": 0.0,
                "actions": []
            }
        ]
    }
    """

    dict_in = json.loads(json_in)
    with pytest.raises(ValueError, match="mandatory field"):
        Node.from_camel_dict(dict_in)


def test_single_edge():
    with open(current_path / "LIF_single_edge.json") as file:
        dict_in = json.load(file)
    check_dict(dict_in, LIF)


def test_mapf():
    with open(current_path / "LIF_4_4_MAPF.json") as file:
        dict_in = json.load(file)
    check_dict(dict_in, LIF)


def test_trajectory():
    with open(current_path / "LIF_trajectory.json") as file:
        dict_in = json.load(file)
    l = check_dict(dict_in, LIF)


def test_enums():
    with open(current_path / "LIF_single_edge.json") as file:
        dict_in = json.load(file)
    l = check_dict(dict_in, LIF)
    assert (l.layouts[0].edges[0].vehicle_type_edge_properties[0].orientation_type == OrientationType.TANGENTIAL)


def test_checks_version():
    with open(current_path / "LIF_wrong_version.json") as file:
        dict_in = json.load(file)
    with pytest.warns(UserWarning):
        LIF.from_camel_dict(dict_in)


def test_pre_deserialization_check():
    class TestCS(CamelSerial):
        @staticmethod
        def _pre_deserialization_check(_camel_dict):
            return False

    with pytest.raises(ValueError) as e:
        TestCS.from_camel_dict({})

    assert "deserialization" in str(e)
