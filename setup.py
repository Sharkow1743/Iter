from setuptools import setup, find_packages

setup(
    name='iter-api',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        'requests', 'DrissionPage'
    ],
    python_requires=">=3.9"
)
