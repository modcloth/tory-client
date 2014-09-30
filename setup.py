# vim:fileencoding=utf-8
import os
import re
import sys

from codecs import open

from setuptools import setup, find_packages


HERE = os.path.dirname(os.path.abspath(__file__))


def get_version():
    with open(os.path.join(HERE, 'tory_client', '__init__.py')) as infile:
        return [
            l.decode('utf-8').split(' = ')[1].strip('\' ')
            for l in infile.read().splitlines(False)
            if l.decode('utf-8').startswith('__version__')
        ][0]


def get_requirements():
    with open(os.path.join(HERE, 'requirements.txt')) as infile:
        return [
            l.decode('utf-8').strip()
            for l in infile.read().splitlines(False)
            if not re.match('^(flake8|pytest|tox)', l.decode('utf-8'))
        ]


def main():
    desc = 'client tools for the tory ansible inventory'
    setup(
        name='tory_client',
        url='https://github.com/modcloth/tory-client',
        author='ModCloth, Inc.',
        author_email='platformsphere+pypi@modcloth.com',
        description=desc,
        long_description=desc,
        version=get_version(),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
        ],
        packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
        install_requires=get_requirements(),
        entry_points={
            'console_scripts': [
                'tory-inventory = tory_client.inventory:main',
                'tory-register = tory_client.register:main',
                'tory-unregister = tory_client.unregister:main',
                'tory-status = tory_client.status:main',
                'tory-sync-from-joyent = tory_client.sync_from_joyent:main',
            ]
        }
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
