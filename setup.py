from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

# Get version in namespace
with open('ovh_dynhost/_version.py') as f:
    code = compile(f.read(), "_version.py", 'exec')
    exec(code)

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='ovh-dynhost',
    version=__version__,
    description='A script to update the OVH DynHost service public IP',
    long_description=long_description,

    url='https://github.com/rubendibattista/ovh-dynhost',

    license='BSD',

    author='Ruben Di Battista',

    author_email='rubendibattista@gmail.com',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: System Administrators',
        'Topic :: Internet :: Name Service (DNS)',

        'Environment :: Console',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
    ],

    keywords='ovh dynhost dynamic dns',
    packages=['ovh_dynhost'],
    install_requires=['requests', 'docopt'],
    extras_require={
        'dev': ['twine']
    },

    entry_points={  # Optional
        'console_scripts': [
            'ovh-dynhost=ovh_dynhost:main',
        ],
    },
)
