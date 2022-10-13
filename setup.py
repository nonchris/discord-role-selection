from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='discord-role-selection',
    version='2.1.0',
    description='A role selection bot using drop down menus',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nonchris/discord-role-selection',
    author='nonchris',
    author_email='info@nonchris.eu',

    project_urls={
        'Bug Reports': 'https://github.com/nonchris/discord-role-selection/issues',
        'Source': 'https://github.com/nonchris/discord-role-selection/discord-bot',
    },

    keywords='discord-bot',

    python_requires='>=3.8, <4',

    install_requires=install_requires,

    classifiers=[

        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Intended Audience :: Other Audience',
        'Topic :: Communications :: Chat',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',

        'Typing :: Typed',
    ],

    package_dir={'': 'src/'},

    packages=find_packages(where='src/'),

    entry_points={
        'console_scripts': [
            'discord-bot=bot:main',
        ],
    },
)
