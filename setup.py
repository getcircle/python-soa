from setuptools import (
    find_packages,
    setup,
)

import service

requirements = [
    'protobuf-soa>=0.1.1',
    'protobuf-to-dict==0.1.0',
]

setup(
    name='python-soa',
    version=service.__version__,
    description='service layer using protobufs',
    packages=find_packages(exclude=[
        "*.tests",
        "*.tests.*",
        "tests.*",
        "tests",
    ]),
    install_requires=requirements,
    scripts=[
        'service/commands/soa-shell',
    ],
    dependency_links=[
        'git+ssh://git@github.com/getcircle/protobuf-soa.git#egg=protobuf-soa-0.1.1',
    ],
)
