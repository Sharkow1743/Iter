from setuptools import setup

version = '1.0.0'

setup(
    name='itd-iter-api',
    version=version,
    packages=['iter', 'iter.routes', 'iter.models'],
    install_requires=[
        'requests', 'DrissionPage', 'verboselogs'
    ],
    python_requires=">=3.9"
)
