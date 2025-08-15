import re
import warnings
from enum import Enum, auto


class OSMWayDirectionCategory(Enum):
    """Enum representing the direction categories for OSM ways."""
    OPEN_IN_BOTH = auto()
    ONLY_OPEN_FORWARDS = auto()
    ONLY_OPEN_BACKWARDS = auto()
    CLOSED = auto()


def is_osm_way_used_by_cars(tags) -> bool:
    """
    Determines if an OSM way is used by cars based on its tags.

    :param tags: Dictionary of OSM tags for the way
    :return: True if the way is used by bicycles, False otherwise
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L174
    if tags["junction"] is not None:
        return True

    if "route" in tags and tags["route"] == "ferry":
        return True

    if "ferry" in tags and tags["ferry"] == "yes":
        return True

    if tags["highway"] is None:
        return False

    if tags["motorcar"] is not None and tags["motorcar"] == "no":
        return False

    if tags["motor_vehicle"] is not None and tags["motor_vehicle"] == "no":
        return False

    if tags["access"] is not None:
        if tags["access"] not in ["yes", "permissive", "delivery", "designated", "destination"]:
            return False

    if tags["highway"] in [
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "unclassified",
        "residential",
        "service",
        "motorway_link",
        "trunk_link",
        "primary_link",
        "secondary_link",
        "tertiary_link",
        "motorway_junction",
        "living_street",
        "residential",
        "track",
        "ferry"
    ]:
        return True

    if tags["highway"] == "bicycle_road":
        return tags["motorcar"] is not None and tags["motorcar"] == "yes"

    if tags["highway"] in [
        "construction",
        "path",
        "footway",
        "cycleway",
        "bridleway",
        "pedestrian",
        "bus_guideway",
        "raceway",
        "escape",
        "steps",
        "proposed",
        "conveying"
    ]:
        return False

    if tags["oneway"] is not None and tags["oneway"] in ["reversible", "alternating"]:
        return False

    if tags["maxspeed"] is not None:
        return True

    return False


def is_osm_way_used_by_bicycles(tags) -> bool:
    """
    Determines if an OSM way is used by bicycles based on its tags.

    :param tags: Dictionary of OSM tags for the way
    :return: True if the way is used by bicycles, False otherwise
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L470
    junction = tags.get('junction')
    if junction is not None:
        return True

    route = tags.get('route')
    if route is not None and route == 'ferry':
        return True

    ferry = tags.get('ferry')
    if ferry is not None and ferry == 'ferry':
        return True

    highway = tags.get('highway')
    if highway is None:
        return False

    if highway == 'proposed':
        return False

    access = tags.get('access')
    if access:
        if access not in [
            'yes', 'permissive', 'delivery', 'designated', 'destination',
            'agricultural', 'forestry', 'public'
        ]:
            return False

    bicycle = tags.get('bicycle')
    if bicycle and bicycle in ['no', 'use_sidepath']:
        return False

    # if a cycleway is specified we can be sure
    # that the highway will be used in a direction
    cycleway = tags.get('cycleway')
    if cycleway is not None:
        return True
    cycleway_left = tags.get('cycleway:left')
    if cycleway_left is not None:
        return True
    cycleway_right = tags.get('cycleway:right')
    if cycleway_right is not None:
        return True
    cycleway_both = tags.get('cycleway:both')
    if cycleway_both is not None:
        return True

    if highway in [
        'secondary', 'tertiary', 'unclassified', 'residential', 'service',
        'secondary_link', 'tertiary_link', 'living_street', 'track',
        'bicycle_road', 'primary', 'primary_link', 'path', 'footway',
        'cycleway', 'bridleway', 'pedestrian', 'crossing', 'escape',
        'steps', 'ferry'
    ]:
        return True

    if highway in [
        'motorway', 'motorway_link', 'motorway_junction', 'trunk',
        'trunk_link', 'construction', 'bus_guideway', 'raceway',
        'conveying'
    ]:
        return False

    return False


def is_osm_way_used_by_pedestrians(tags) -> bool:
    """
    Determines if an OSM way is used by pedestrians based on its tags.

    :param tags: Dictionary of OSM tags for the way
    :return: True if the way is used by pedestrians, False otherwise
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L67
    junction = tags.get('junction')
    if junction is not None:
        return True

    route = tags.get('route')
    if route and route == 'ferry':
        return True

    ferry = tags.get('ferry')
    if ferry and ferry == 'ferry':
        return True

    public_transport = tags.get('public_transport')
    if public_transport is not None and public_transport in [
        'stop_position', 'platform', 'stop_area', 'station'
    ]:
        return True

    railway = tags.get('railway')
    if railway is not None and railway in [
        'halt', 'platform', 'subway_entrance', 'station', 'tram_stop'
    ]:
        return True

    highway = tags.get('highway')
    if highway is None:
        return False

    access = tags.get('access')
    if access:
        if access not in [
            'yes', 'permissive', 'delivery', 'designated', 'destination',
            'agricultural', 'forestry', 'public'
        ]:
            return False

    crossing = tags.get('crossing')
    if crossing is not None and crossing == 'no':
        return False

    if highway in [
        'secondary', 'tertiary', 'unclassified', 'residential', 'service',
        'secondary_link', 'tertiary_link', 'living_street', 'track',
        'bicycle_road', 'path', 'footway', 'cycleway', 'bridleway',
        'pedestrian', 'escape', 'steps', 'crossing', 'escalator',
        'elevator', 'platform', 'ferry'
    ]:
        return True

    if highway in [
        'motorway', 'motorway_link', 'motorway_junction', 'trunk',
        'trunk_link', 'primary', 'primary_link', 'construction',
        'bus_guideway', 'raceway', 'proposed', 'conveying'
    ]:
        return False

    return False


def get_osm_way_speed(osm_way_id: int, tags: dict) -> float:
    """
    Get the speed limit for an OSM way based on its tags.

    :param osm_way_id: The OSM way ID
    :param tags: Dictionary of OSM tags for the way
    :return: Speed limit in km/h
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L364
    INF_WEIGHT = float('inf')

    maxspeed = tags.get("maxspeed")
    if maxspeed is not None and maxspeed != "unposted":
        maxspeed: str
        lower_case_maxspeed = maxspeed.lower()

        speed = INF_WEIGHT

        for maxspeed_val in lower_case_maxspeed.split(';'):
            speed = min(speed, parse_maxspeed_value(osm_way_id, maxspeed_val))

        if speed == 0:
            speed = 1
            warnings.warn(f"Warning: OSM way {osm_way_id} has speed 0 km/h, setting it to 1 km/h")

        if speed != INF_WEIGHT:
            return speed

    highway = tags.get("highway")
    if highway:
        highway_speeds = {
            "motorway": 90,
            "motorway_link": 45,
            "trunk": 85,
            "trunk_link": 40,
            "primary": 65,
            "primary_link": 30,
            "secondary": 55,
            "secondary_link": 25,
            "tertiary": 40,
            "tertiary_link": 20,
            "unclassified": 25,
            "residential": 25,
            "living_street": 10,
            "service": 8,
            "track": 8,
            "ferry": 5
        }

        if highway in highway_speeds:
            return highway_speeds[highway]

    junction = tags.get("junction")
    if junction:
        return 20

    # RoutingKit has an open TO-DO: a ferry may have a duration tag
    route = tags.get("route")
    if route == "ferry":
        return 5

    ferry = tags.get("ferry")
    if ferry:
        return 5

    warnings.warn(
        f'Warning: OSM way {osm_way_id} has '
        f'{"no" if not maxspeed else "an unrecognized"} "maxspeed" tag'
        f'{f" of \"{maxspeed}\"" if maxspeed else ""} and '
        f'{"no" if not highway else "an unrecognized"} "highway" tag'
        f'{f" of \"{highway}\"" if highway else ""} and no junction tag -> assuming 50km/h.')

    return 50


# Compile regex pattern once at module level
speed_pattern = re.compile(r'^(\d+)\s*(.*)$')


def parse_maxspeed_value(osm_way_id: int, maxspeed: str) -> float:
    """
    Parse a maxspeed value from OSM tags.

    :param osm_way_id: The OSM way ID (for logging)
    :param maxspeed: The maxspeed value to parse
    :return: Parsed speed value in km/h, or inf if unparseable
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L294
    INF_WEIGHT = float('inf')

    maxspeed = maxspeed.strip()
    if not maxspeed:
        return INF_WEIGHT

    if maxspeed in ["signals", "variable"]:
        return INF_WEIGHT

    if maxspeed in ["none", "unlimited"]:
        return 130

    if maxspeed in ["walk", "foot", "walking_pace", "schritt"] or maxspeed.endswith(":walk"):
        return 5

    if maxspeed == "urban" or maxspeed.endswith(":urban"):
        return 40

    if maxspeed == "living_street" or maxspeed.endswith(":living_street"):
        return 10

    if maxspeed in ["de:rural", "at:rural", "ro:rural", "rural"]:
        return 100
    if maxspeed in ["ru:rural", "ua:rural", "it:rural", "hu:rural"]:
        return 90
    if maxspeed in ["dk:rural", "ch:rural", "fr:rural"]:
        return 80

    if maxspeed == "ru:motorway":
        return 110
    if maxspeed == "ch:motorway":
        return 120
    if maxspeed in ["at:motorway", "ro:motorway", "de:motorway"]:
        return 130

    if maxspeed == "national":
        return 100

    if maxspeed == "ro:trunk":
        return 100

    if maxspeed in ["de:zone:30", "de:zone30", "at:zone30"]:
        return 30

    # Try to parse numeric value
    if maxspeed and maxspeed[0].isdigit():
        match = speed_pattern.match(maxspeed)
        if match:
            speed = int(match.group(1))
            unit = match.group(2)

            if not unit or unit in ["km/h", "kmh", "kph"]:
                return speed
            elif unit == "mph":
                return speed * 1609 / 1000  # Convert mph to km/h (integer division like C++)
            elif unit == "knots":
                return speed * 1852 / 1000  # Convert knots to km/h
            else:
                warnings.warn(
                    f'Warning: OSM way {osm_way_id} has an unknown unit "{unit}" for its "maxspeed" tag -> assuming "km/h".')
                return speed

    # If we can't parse it, log a warning
    warnings.warn(
        f'Warning: OSM way {osm_way_id} has an unrecognized value of "{maxspeed}" for its "maxspeed" tag.')

    return INF_WEIGHT


def get_osm_car_direction_category(osm_way_id, tags) -> OSMWayDirectionCategory:
    """
    Determines the direction category of an OSM way for car routing.

    :param osm_way_id: The OSM way ID
    :param tags: Dictionary of OSM tags for the way
    :return: Direction category enum value
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L266
    oneway = tags.get("oneway")
    junction = tags.get("junction")
    highway = tags.get("highway")

    if oneway is not None:
        if oneway in ["-1", "reverse", "backward"]:
            return OSMWayDirectionCategory.ONLY_OPEN_BACKWARDS
        elif oneway in ["yes", "true", "1"]:
            return OSMWayDirectionCategory.ONLY_OPEN_FORWARDS
        elif oneway in ["no", "false", "0"]:
            return OSMWayDirectionCategory.OPEN_IN_BOTH
        elif oneway in ["reversible", "alternating"]:
            return OSMWayDirectionCategory.CLOSED
        else:
            warnings.warn(
                f'Warning: OSM way {osm_way_id} has unknown oneway tag value "{oneway}" for "oneway". Way is closed.')
            return OSMWayDirectionCategory.CLOSED
    elif junction is not None and junction == "roundabout":
        return OSMWayDirectionCategory.ONLY_OPEN_FORWARDS
    elif highway is not None and highway in ["motorway", "motorway_link"]:
        return OSMWayDirectionCategory.ONLY_OPEN_FORWARDS

    return OSMWayDirectionCategory.OPEN_IN_BOTH


def get_osm_bicycle_direction_category(osm_way_id: int, tags: dict) -> OSMWayDirectionCategory:
    """
    Determines the direction category of an OSM way for bicycle routing.

    :param osm_way_id: The OSM way ID
    :param tags: Dictionary of OSM tags for the way
    :param log_message: Optional logging function that takes a string message
    :return: Direction category enum value
    """
    # https://github.com/RoutingKit/RoutingKit/blob/13bc2f49f41d2e8a750a299487705ca7217d634d/src/osm_profile.cpp#L568
    oneway_bicycle = tags.get("oneway:bicycle")
    if oneway_bicycle is not None:
        if oneway_bicycle in ["-1", "opposite"]:
            return OSMWayDirectionCategory.ONLY_OPEN_BACKWARDS

        if oneway_bicycle in ["1", "yes", "true", "no_planned"]:
            return OSMWayDirectionCategory.ONLY_OPEN_FORWARDS

        if oneway_bicycle in ["0", "no", "false", "tolerated", "permissive"]:
            return OSMWayDirectionCategory.OPEN_IN_BOTH

        warnings.warn(f'Warning: OSM way {osm_way_id} has unknown oneway tag value "{oneway_bicycle}" '
                      f'for "oneway:bicycle". Way is closed.')
        return OSMWayDirectionCategory.CLOSED

    oneway = tags.get("oneway")
    if oneway is None:
        return OSMWayDirectionCategory.OPEN_IN_BOTH
    else:
        if oneway in ["no", "false", "0"]:
            return OSMWayDirectionCategory.OPEN_IN_BOTH

        cycleway = tags.get("cycleway")
        if cycleway is not None:
            # "opposite" is interpreted as the other direction than cars are allowed.
            # This is not necessarily opposite to the direction of the OSM way.
            #
            # A consequence is that "cycleway=opposite" combined "oneway=-1" does not imply that bicycles are only allowed to drive backwards
            #
            # (Yes, people actually do combine those two tags https://www.openstreetmap.org/way/88925376 )
            if cycleway in ["opposite", "opposite_track", "opposite_lane", "opposite_share_busway"]:
                return OSMWayDirectionCategory.OPEN_IN_BOTH

        cycleway_both = tags.get("cycleway:both")
        if cycleway_both is not None:
            return OSMWayDirectionCategory.OPEN_IN_BOTH

        cycleway_left = tags.get("cycleway:left")
        cycleway_right = tags.get("cycleway:right")
        if cycleway_left is not None and cycleway_right is not None:
            return OSMWayDirectionCategory.OPEN_IN_BOTH

        if oneway in ["-1", "reverse", "backward"]:
            return OSMWayDirectionCategory.ONLY_OPEN_BACKWARDS
        elif oneway in ["yes", "true", "1"]:
            return OSMWayDirectionCategory.ONLY_OPEN_FORWARDS
        elif oneway in ["reversible", "alternating"]:
            return OSMWayDirectionCategory.CLOSED
        else:
            warnings.warn(f'Warning: OSM way {osm_way_id} has unknown oneway tag value "{oneway}" '
                          f'for "oneway". Way is closed.')
            return OSMWayDirectionCategory.CLOSED
