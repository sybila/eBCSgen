from setuptools import setup, find_packages

setup(name='eBCSgen',
      version='1.3',
      description='eBSCgen is a tool for development and analysis of models written in Biochemical Space Language',
      url='https://github.com/sybila/eBCSgen',
      author='Mate Trojak',
      author_email='xtrojak@fi.muni.cz',
      license='MIT',
      packages=find_packages(exclude=['*Testing*']),
      test_suite="Testing",
      zip_safe=False)
