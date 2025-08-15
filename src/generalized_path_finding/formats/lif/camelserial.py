import re
from abc import ABC
from enum import Enum
from types import UnionType
from typing import Type
from typing import TypeVar, get_type_hints
from typing import Union, get_args, get_origin

from auto_all import public

CAMEL_CASE_WORD_SPLIT = re.compile(
    r"""
        # end of word
        (?<=[a-z])      # preceded by lowercase
        (?=[A-Z])       # followed by uppercase
        |               #   OR
        # end of acronym
        (?<=[A-Z])       # preceded by uppercase
        (?=[A-Z][a-z])  # followed by uppercase, then lowercase
    """,
    re.X,
)


def _camel_to_snake(camel_string: str) -> str:
    return re.sub(CAMEL_CASE_WORD_SPLIT, '_', camel_string).lower()


def _snake_to_camel(snake_str: str) -> str:
    if snake_str.startswith('_'): raise ValueError('snake_str must not start with "_"')
    uppercase_camel_string = "".join(x.capitalize() for x in snake_str.lower().split("_"))
    return snake_str[0].lower() + uppercase_camel_string[1:]


T = TypeVar('T', bound="CamelSerial")

# Union and UnionType (result of "A | B") are virtually the same and will be merged into Union soon:
# https://github.com/python/cpython/pull/105511
# For now, both cases have to be handled
union_types = [Union, UnionType]

def is_optional_type(tp):
    return get_origin(tp) in union_types and any(t is type(None) for t in get_args(tp))

def non_optional_type(tp):
    if get_origin(tp) in union_types:
        non_none = tuple(t for t in get_args(tp) if t is not type(None))
        if len(non_none) == 1:
            return non_none[0]
        else:
            return Union[non_none]
    return tp


@public
class CamelSerial(ABC):
    """
    Inherit from this class to support deserialization from and serialization to dicts with camel case keys,
    while keeping attributs snake case.

    Deserialization and serialization works recursively and converts the entire tree.
    It also supports lists and enums.
    """

    @staticmethod
    def _pre_deserialization_check(_camel_dict: dict) -> bool:
        """
        This method is called before deserializing the object.
        It can be overridden to check for certain properties of the input dictionary before conversion.

        :param _camel_dict: Dictionary that is about to be deserialized using camel case keys.
        :return: True if `camel_dict` is ready for deserialization
        """
        return True

    @classmethod
    def from_camel_dict(cls: Type[T], camel_dict: dict) -> T:
        """
        Create and return an instance of the class this method is called on using the values provided in camel_dict.
        Each snake case attribute of the class is populated with the value of the same key in camel case in camel_dict.

        These attribute types are treated extra:
        - subtype of `Deserializer`: is also populated using its conversion `from_camel_dict`
        - list: each item is converted
        - enum: populated with enum variants from the values in teh camel_dict

        :param camel_dict: Dictionary that holds at least all necessary attributes of the class using camel case keys.
        :return: An instance of the class this method is called on with attributes populated from camel_dict.
        """
        if not cls._pre_deserialization_check(camel_dict):
            raise ValueError("Pre deserialization check failed")
        snake_dict = {_camel_to_snake(k): v for k, v in camel_dict.items()}
        for prop, typ in get_type_hints(cls).items():
            if is_optional_type(typ):
                if prop in snake_dict:
                    typ = non_optional_type(typ)
                else:
                    continue  # no value for optional value given -> let the constructor handle it
            elif not is_optional_type(typ) and prop not in snake_dict:
                raise ValueError(f"mandatory field {prop} missing in {cls.__name__}")

            if get_origin(typ) is list and issubclass(list_typ := get_args(typ)[0], CamelSerial):
                snake_dict[prop] = [list_typ.from_camel_dict(item) for item in snake_dict[prop]]
            elif isinstance(typ, type) and issubclass(typ, Enum):
                snake_dict[prop] = typ[snake_dict[prop]]
            elif isinstance(typ, type) and issubclass(typ, CamelSerial):
                snake_dict[prop] = typ.from_camel_dict(snake_dict[prop])
            elif typ is float:  # accept int as float
                snake_dict[prop] = float(snake_dict[prop])
            elif get_origin(typ) is list and get_args(typ)[0] is float:
                snake_dict[prop] = list(map(float, snake_dict[prop]))

        # noinspection PyArgumentList
        return cls(**snake_dict)

    def to_camel_dict(self):
        """
        Create and return a dictionary with camel case keys using the values of the attributes of the class this method
        is called on.
        Each snake case attribute of the class is converted into a camel case key-value pair in the returned dictionary.

        These attribute types are treated extra:
        - subtype of `Deserializer`: is also converted using its method `to_camel_dict`
        - list: each item is converted
        - enum: converted to their associated values

        :return: Dictionary that holds all non-null attributes of the class using camel case keys.
        """

        def serialize_child(obj):
            if isinstance(obj, CamelSerial):
                return obj.to_camel_dict()
            elif isinstance(obj, list):
                return list(map(serialize_child, obj))
            elif isinstance(obj, Enum):
                return obj.value
            else:
                return obj

        return {_snake_to_camel(k): serialize_child(self.__dict__[k]) for k in self.__annotations__}
