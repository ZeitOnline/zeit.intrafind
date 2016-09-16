from setuptools import setup, find_packages


setup(
    name='zeit.intrafind',
    version='2.4.1.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi intrafind integration",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.lxml',
        'mock',
        'setuptools',
        'zeit.cms>=2.89.0.dev0',
        'zope.interface',
        'zope.schema',
    ]
)
