import os, sys

def get_environment():
    return os.environ.get('ENV', 'development')