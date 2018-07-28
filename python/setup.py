from setuptools import setup, find_packages

setup(
    name='shippai',
    version='0.3.1',
    description='Interface with Rust errors seamlessly',
    long_description=open('README.rst').read(),
    author='Markus Unterwaditzer',
    author_email='markus-python@unterwaditzer.net',
    url='https://github.com/untitaker/shippai',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    license='MIT',
    classifiers=['License :: OSI Approved :: MIT License']
)
