from setuptools import (
    find_packages,
    setup,
)

import service

requirements = [
    'protobuf-soa==0.0.1',
    'protobuf-to-dict==0.1.0',
]

setup_requirements = [
    'nose>=1.0',
    'coverage>=1.0',
    'mock==1.0.1',
]

setup(
    name='python-soa-protobuf',
    version=service.__version__,
    description='service layer using protobufs',
    packages=find_packages(exclude=[
        "*.tests",
        "*.tests.*",
        "tests.*",
        "tests",
    ]),
    install_requires=requirements,
    setup_requires=setup_requirements,
    scripts=[
        'service/commands/soa-shell',
    ],
    dependency_links=[
        'https://github.com/getcircle/protobuf-soa/tarball/master#egg=protobuf-soa',
    ],
)
