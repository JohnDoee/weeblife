import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')) as f:
    requirements = f.read().strip().split('\n')


setup(
    name="weeblife",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,

    install_requires=requirements,
    author="Anders Jensen",
    author_email="johndoee@tidalstream.org",
    description="Random wallpapers and loading animations.",
    license="MIT",
    url="https://github.com/JohnDoee/weeblife",

)
