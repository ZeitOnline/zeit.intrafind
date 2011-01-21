from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'CHANGES.txt')).read()


version = '0.1dev'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='zeit.intrafind',
    version=version,
    description="vivi intrafind integration",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='',
    author='gocept',
    author_email='mail@gocept.com',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['zeit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['zeit.intrafind=zeit.intrafind:main']
    }
)