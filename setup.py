from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
    
setup(
    name='factvest', # name your package
    packages=['factvest'], # same name as above
    version='0.1.0.dev1',
    description='get stock market data through iex api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mirprest/factvest',
    author='Terrell Vest',
    author_email='terrell@terrellvest.com',
    license='MIT',
    keywords='stock market data iex price',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers :: Analysts',
        'Topic :: Software Development :: API Tool',
        'License :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['pandas', 'xlsxwriter', 'requests'],
    project_urls={
        'Bug Reports': 'https://github.com/mirprest/factvest/issues',
        'Say Thanks!': 'https://twitter.com/TerrellVest7',
        'Source': 'https://github.com/mirprest/factvest/',
    },
) 
     