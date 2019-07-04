import setuptools

# https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
setuptools.setup(
    name='Aim',
    version='0.1',
    packages=["aim"],
    license='',
    long_description=open('README.md').read(),
    install_requires=["toml", "cerberus"],
    entry_points={
        "console_scripts": ["aim=bin.entry:main"]

    }
)
