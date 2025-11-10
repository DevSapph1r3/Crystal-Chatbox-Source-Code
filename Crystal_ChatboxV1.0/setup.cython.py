from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize(
        [
            "main.py",
            "routes.py",
            "heart_rate_monitor.py",
            "spotify.py",
            "window_tracker.py",
            "settings.py"
        ],
        compiler_directives={'language_level': "3"},
        annotate=False
    )
)
