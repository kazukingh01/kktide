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
        'kkpsgre @ git+https://github.com/kazukingh01/kkpsgre.git@9200e84429b12a11d6e897d8b478b7946075bf0e',
        'pandas==1.5.3',
        'numpy==1.24.2',
        'requests==2.28.2',
        'beautifulsoup4==4.11.2',
        'matplotlib==3.7.1',
        'folium==0.15.1',
    ],
    python_requires='>=3.11.2'
)
