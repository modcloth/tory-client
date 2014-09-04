import sys

from setuptools import setup


__version__ = '0.5.1'


def main():
    desc = 'client tools for the tory ansible inventory'
    setup(
        name='tory-client',
        url='https://github.com/modcloth/tory-client',
        author='ModCloth, Inc.',
        author_email='platformsphere+pypi@modcloth.com',
        description=desc,
        long_description=desc,
        version=__version__,
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
        py_modules=[
            'tory_inventory',
            'tory_register',
            'tory_sync_from_joyent',
        ],
        entry_points={
            'console_scripts': [
                'tory-inventory = tory_inventory:main',
                'tory-register = tory_register:main',
                'tory-sync-from-joyent = tory_sync_from_joyent:main',
            ]
        }
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
