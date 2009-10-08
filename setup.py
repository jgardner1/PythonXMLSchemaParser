from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='XMLSchemaParser',
      version=version,
      description="Parses XML files according to XML Schema",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='XML Schema parse WSDL',
      author='Jonathan Gardner',
      author_email='jgardner@jonathangardner.net',
      url='http://tech.jonathangardner.net/w/Python/XMLSchemaParser',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
