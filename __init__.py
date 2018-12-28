from .core import core
import os
import sys

modules = ['core', 'propublica', 'twitter']
module_paths = [os.path.join(os.path.dirname(__file__), module)
                for module in modules]

sys.path.append(module_paths)
