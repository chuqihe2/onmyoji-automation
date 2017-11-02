RESET_POS = (1000, 20)


def check_not_none(var):
    """
    Throws an ValueError if given None. Otherwise returns the value itself.
    """
    if var is None:
        raise ValueError('None value unexpected!')
    return var
