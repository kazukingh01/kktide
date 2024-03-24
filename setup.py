from setuptools import setup, find_packages

packages = find_packages(
        where='.',
        include=['kktide*']
)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='kktide',
    version='1.0.0',
    description="Collecting and analyze the TIDE's data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kazukingh01/kktide",
    author='kazukingh01',
    author_email='kazukingh01@gmail.com',
    license='Private License',
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Private License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'kkpsgre @ git+https://github.com/kazukingh01/kkpsgre.git@7177981dbeb7fefcb8dc07ae368e780e60ddbd86',
        'pandas==2.2.1',
        'numpy==1.26.4',
        'requests==2.28.2',
        'beautifulsoup4==4.12.3',
        'matplotlib==3.8.3',
        'folium==0.15.1',
    ],
    python_requires='>=3.12.2'
)
