# Copyright (c) dabeLabs
# All rights reserved.

import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Lab-Scripts',
    version='1',
    author='Davide Beretta',
    author_email='mail.davide.beretta@gmail.com',
    description='toolbox for small features segmentation from optical images',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dabeLab/Lab-Scripts/blob/main/imaging/segmentation/optical_image',
    license='dabeLabs',
    packages=['optical_image'],
    install_requires=['requests'],
)