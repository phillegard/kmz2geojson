from setuptools import setup, find_packages

with open("README.md", "w") as f:
    f.write("# KMZ to GeoJSON Converter\n\nConvert KMZ/KML files to GeoJSON with automatic attribute parsing from HTML tables.\n")

setup(
    name='kmz2geojson',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'lxml>=5.1.0',
        'beautifulsoup4>=4.12.0',
        'click>=8.1.0',
        'geojson>=3.1.0',
    ],
    entry_points={
        'console_scripts': [
            'kmz2geojson=kmz2geojson.cli:main',
        ],
    },
    python_requires='>=3.8',
    author='Phil Legard',
    description='Convert KMZ/KML files to GeoJSON with automatic attribute parsing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
