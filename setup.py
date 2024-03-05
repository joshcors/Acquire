from setuptools import setup
from setuptools.command.install import install

import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

class InitializeMetadata(install):
    def run(self):
        print("Hello")
        install.run(self)
        os.system(f"python {os.path.join(dir_path), 'src', 'Game', 'metadata.py'}")
setup(
    name="Acquire",
    description="Python source code for Acquire Board Game logic and UI",
    package_dir={"": "src"},
    packages=["Game", "UI", "Web"]
)