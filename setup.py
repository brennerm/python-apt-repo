from os import path
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='apt-repo',
    version='0.3',
    packages=['apt_repo'],
    url='https://github.com/brennerm/python-apt-repo',
    license='MIT',
    author='brennerm',
    author_email='xamrennerb@gmail.com',
    description='Python library to query APT repositories',
    long_description_content_type='text/markdown',
    long_description=long_description,
    python_requires='>=3.5'
)
