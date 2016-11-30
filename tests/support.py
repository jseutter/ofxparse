import os


def open_file(filename, mode='rb'):
    """
    Load a file from the fixtures directory.
    """
    path = os.path.join('fixtures', filename)
    if 'tests' in os.listdir('.'):
        path = os.path.join('tests', path)
    return open(path, mode=mode)
