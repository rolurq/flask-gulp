from setuptools import setup

setup(name='Flask-Static', license='MIT', author='Rolando Urquiza',
      author_email='rolurquiza@gmail.com',
      description='Task executioner similar to gulp for Python',
      packages=['flask_static'], platforms='any',
      install_requires=['werkzeug'],
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'])
