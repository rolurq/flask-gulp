import re
import os

from jinja2 import Markup
from flask import url_for
from collections import namedtuple
from itertools import cycle

from flask_static.watcher import Watcher
from flask_static.extensions import extensions

Task = namedtuple('Task', ['function', 'items'])


class Static(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
        self.tasks = {}

    def init_app(self, app):
        self.app = app

        @app.context_processor
        def context_processor():
            def build_html(wrapper, *tasks):
                markup = ''
                for task in tasks:
                    markup = markup.join('<!-- %s -->' % task)
                    markup = markup.join(Markup('\n'.join(
                        (wrapper % url_for('static', filename=os.path.relpath(item,
                            self.app.root_path)) for item in self.tasks[task].items))))
                return markup

            def css(*tasks):
                """
                    Create links to style files using results from task
                """
                if not self.app.debug:
                    self.run(*tasks)
                return build_html('<link rel="stylesheet" href="%s"/>', *tasks)

            def js(*tasks, **options):
                """
                    Create links to script files using results from task
                """
                options.setdefault('defer', False)
                options.setdefault('asynchro', False)
                attrs = ['src="%s"']
                if options['defer']:
                    attrs.append('defer')
                if options['asynchro']:
                    attrs.append('async')
                if not self.app.debug:
                    self.run(*tasks)
                return build_html("<script %s></script>" % ' '.join(attrs),
                                  *tasks)

            return dict(js=js, css=css)

    def task(self, name):
        """
            Decorator to create tasks

            Inside the decorated function scope extensions will be available as
            globals, also, the `src` function, wich return the object to create
            the pipeline.
        """
        def decorator(f):
            self.tasks[name] = Task(f, [])

            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
        return decorator

    def watch(self, path, *tasks):
        watcher = Watcher(cycle(self.__findFiles(path)), self, tasks)
        watcher.start()

    def __findFiles(self, *paths):
        if self.app is None:
            raise ValueError('You should pass a valid application')
        wildcards = [re.compile(r) for r in paths]

        for dirpath, _, filenames in os.walk(self.app.root_path):
            rpath = os.path.relpath(dirpath, self.app.root_path)
            # TODO: delete unnecesary directories
            for f in filenames:
                for reg in wildcards:
                    if reg.match(os.path.join(rpath, f)):
                        yield os.path.join(dirpath, f)

    def __loadResources(self, *paths):
        res = StaticResources()
        for filename in self.__findFiles(*paths):
            res.add(filename)
        return res

    def run(self, *tasks):
        def src(*paths):
            global res
            res = self.__loadResources(*paths)
            return res

        for task in tasks:
            t = self.tasks[task]
            # extend function scope
            t.function.__globals__.update(extensions)
            t.function.__globals__['src'] = src
            t.function()
            t.items.extend((filename for filename, _ in res))
            # retrieve normal scope
            del t.function.__globals__['src']
            for k in extensions:
                del t.function.__globals__[k]


class StaticResources(object):

    def __init__(self, *files):
        self.resources = []
        for f in files:
            self.add(f)

    def pipe(self, extension):
        for i, (filename, data) in enumerate(self.resources):
            result = extension(filename, data)
            if result:
                dest, generated = result
                if not dest:
                    print(generated)
                else:
                    self.resources[i] = dest, generated
        return self

    def add(self, filename):
        f = open(filename)
        self.resources.append((filename, f.read()))
        f.close()

    def __iter__(self):
        return iter(self.resources)
