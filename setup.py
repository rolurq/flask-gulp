from setuptools import setup


def get_version():
    with open('version') as f:
        return f.read()

setup(name='Flask-Static', license='MIT', author='Rolando Urquiza',
      author_email='rolurquiza@gmail.com', version=get_version(),
      description='Task executioner similar to gulp for Python',
      packages=['flask_static'], platforms='any',
      install_requires=['flask', 'werkzeug'],
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'])
