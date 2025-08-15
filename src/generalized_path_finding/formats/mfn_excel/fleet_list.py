def parse_fleets_list(lst: str) -> list[str]:
    """
    Parses a pipe ("|") seperated list of fleet identifiers into a list of lowercase fleet identifiers.

    A fleet identifier does not start or end with whitespace and does not contain a pipe ("|").

    :param lst: pipe-seperated list of fleet identifiers as string
    :return: list of lowercase fleet identifiers
    """

    if lst.strip() == '':
        return []
    return [fl.strip().lower() for fl in lst.split("|")]
