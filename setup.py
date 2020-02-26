import os
from distutils.core import setup

NAME = "aioeventbus"

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESC = f.read()

here = os.path.dirname(__file__)
ABOUT = {}

with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), ABOUT)

setup(
    name=NAME,
    description="Simple, in-process, event-driven programming for Python based on asyncio.",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    version=ABOUT["__version__"],
    author="momocow",
    author_email="momocow.me@gmail.com",
    license="MIT",
    url="https://github.com/momocow/python-aioeventbus",
    packages=["aioeventbus"],
    classifiers=[
        "Framework :: AsyncIO",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7"
    ]
)
