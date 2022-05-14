def coalesce(*args):
    """
    Returns first not None value
    :param args: list|tuple
    :return: value
    """
    for arg in args:
        if arg is not None:
            return arg
    return None