import os


def open_file(filename, mode='rb'):
    ''' Load a file from the fixtures directory. '''
    path = 'fixtures/' + filename
    if ('tests' in os.listdir('.')):
        path = 'tests/' + path
    return open(path, mode=mode)
