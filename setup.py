try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import flask_gulp


readme = open('README.rst').read()
version = flask_gulp.__version__

setup(name='Flask-Gulp', license='MIT License', author='Rolando Urquiza',
      author_email='rolurquiza@gmail.com', version=version,
      keywords='flask gulp task watcher',
      description='Task executioner similar to gulp for Python',
      long_description=readme,
      packages=['flask_gulp'], platforms='any',
      install_requires=['flask', 'werkzeug'],
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'],
      url='https://github.com/rolurq/flask-gulp')
