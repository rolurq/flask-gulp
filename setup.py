from setuptools import setup


setup(name='Flask-Gulp', license='MIT', author='Rolando Urquiza',
      author_email='rolurquiza@gmail.com', version='0.2.5',
      description='Task executioner similar to gulp for Python',
      packages=['flask_gulp'], platforms='any',
      install_requires=['flask', 'werkzeug'],
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      url='https://github.com/rolurq/flask-gulp')
