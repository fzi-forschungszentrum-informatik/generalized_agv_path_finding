from generalized_path_finding.formats.lif.action import (
    Action,
    ActionParameter,
    BlockingType,
    RequirementType,
)


def test_parameters():
    param1 = ActionParameter(key="speed", value="fast")
    param2 = ActionParameter(key="direction", value="north")
    action = Action(
        action_type="move",
        blocking_type=BlockingType.SOFT,
        action_description="Move the vehicle",
        requirement_type=RequirementType.REQUIRED,
        action_parameters=[param1, param2],
    )

    param_dict = action.get_action_parameter_dict()
    assert param_dict == {"speed": "fast", "direction": "north"}

    # Test Action without parameters
    action_no_params = Action(
        action_type="stop",
        blocking_type=BlockingType.HARD,
        action_description="Stop the vehicle",
        requirement_type=RequirementType.OPTIONAL,
        action_parameters=None,
    )

    param_dict_no_params = action_no_params.get_action_parameter_dict()
    assert param_dict_no_params == {}
