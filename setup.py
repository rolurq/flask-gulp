from setuptools import setup


def get_version():
    with open('version') as f:
        return f.read()

setup(name='Flask-Gulp', license='MIT', author='Rolando Urquiza',
      author_email='rolurquiza@gmail.com', version=get_version(),
      description='Task executioner similar to gulp for Python',
      packages=['flask_gulp'], platforms='any',
      install_requires=['flask', 'werkzeug'],
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      url='https://github.com/rolurq/flask-gulp')
