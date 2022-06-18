from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize(["edit_distance.pyx", "jaro_distance.pyx"])
)