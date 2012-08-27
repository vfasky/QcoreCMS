#coding=utf-8
from setuptools import setup

setup(
    name = "Qcore-cms",
    version = "1.0 DEV",
    author = "vfasky",
    author_email = "vfasky@gmail.com",
    description = ("基于 tornado 的 cms"),
    install_requires = [
        'tornado',
        'MySQL-python',
        'PIL'
        ],
    platforms='any',
    license = "",
    url = "http://vfasky.com",
    packages=[],
    scripts = [],
)
