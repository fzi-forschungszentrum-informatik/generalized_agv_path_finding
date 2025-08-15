from dataclasses import dataclass
from enum import Enum

from auto_all import public

from .camelserial import (CamelSerial)


@public
class BlockingType(str, Enum):
    """
    Specifies what else might be executed simultaneously to an action.
    """

    NONE = 'NONE'
    """
    Allows moving and other actions.
    """

    SOFT = 'SOFT'
    """
    Allows other actions, but not moving.
    """

    HARD = 'HARD'
    """
    Is the only allowed action at this time.
    """

@public
class RequirementType(str, Enum):
    """
    Whether and when the (third-party) master control system must communicate an action to the vehicle.
    """

    REQUIRED = 'REQUIRED'
    """
    The (third-party) master control system must always communicate this action to the vehicle on this node or edge.
    
    The LIF does not specify a rigid definition of behaviour for anything other than at most one required action. If more than one action is marked as
    required on a node or edge, it is the responsibility
    of the vehicle integrator to define the implications of this to the (third-party) master control
    system, either be it that all of the required
    actions are always required, or that one of the
    actions is always required, or some other combination thereof.
    """

    CONDITIONAL = 'CONDITIONAL'
    """
    The action may or may not be required contingent upon various factors. 
    Discussion between the vehicle integrator and the (third-party) master control system is required.
    """

    OPTIONAL = 'OPTIONAL'
    """
    The action may or may not be communicated to the vehicle at the (third-party) master control system‘s discretion 
    and responsibility. The vehicle must be able to execute without issue if OPTIONAL actions are never, sometimes, 
    or always sent to it.
    """

@public
@dataclass
class ActionParameter(CamelSerial):
    """
    Key/value based generic action parameter listing.
    """

    key: str
    """
    Key which must be unique among the collection of action parameters.
    """

    value: str
    """
    Value corresponding to the key.
    """


@public
@dataclass
class Action(CamelSerial):
    """
    Refers to VDA 5050 action definition.
    All properties that have the same name are meant to be semantically identical.
    """

    action_type: str
    """
    Name of the action same as described in the VDA 5050 specification document 
    (section 6.8.2 in VDA 5050 2.0 specification document).

    Manufacturer-specific actions can be specified.
    Such actions must be agreed with the (third-party) master control system.
    """

    blocking_type: BlockingType
    """
    Specifies what else might be executed simultaneously to this action.
    """

    action_description: str | None = None
    """
    Brief description of the action.
    """

    requirement_type: RequirementType | None = None
    """
    Whether and when the (third-party) master control system must communicate this action to the vehicle. 
    """

    action_parameters: list[ActionParameter] | None = None
    """
    Exact list of parameters and their statically defined values which must be sent along with this action.

    There may be other actionParameters with dynamic values that are required by an action that are not contained in 
    this list. The (third-party) master control system must still determine and send these actionParameters.
    Refer to the AGV Fact Sheet.
    """

    def get_action_parameter_dict(self) -> dict[str, str]:
        """
        Get the action parameters as a dictionary derived from the list of key-value pairs.
        """

        if self.action_parameters is None:
            return {}
        else:
            return {param.key: param.value for param in self.action_parameters}
