from setuptools import setup

import flask_gulp


readme = open('README').read()
version = flask_gulp.__version__

setup(name='Flask-Gulp', license='MIT License', author='Rolando Urquiza',
      author_email='rolurquiza@gmail.com', version=version,
      keywords='flask gulp task watcher',
      description='Task executioner similar to gulp for Python',
      packages=['flask_gulp'], platforms='any',
      install_requires=['flask', 'werkzeug'],
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      url='https://github.com/rolurq/flask-gulp')
