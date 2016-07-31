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
            def build_html(items, wrapper):
                return Markup('\n'.join(
                    (wrapper % url_for('static', filename=os.path.relpath(item,
                                       self.app.root_path))
                        for item in items)))

            def css(task):
                wrapper = '<link rel="stylesheet" href="%s" />'
                return build_html(self.tasks[task].items, wrapper)

            def js(task, defer=False, asynchro=False):
                attrs = ['src="%s"']
                if defer:
                    attrs.append('defer')
                if asynchro:
                    attrs.append('async')
                wrapper = "<script %s></script" % ' '.join(attrs)
                return build_html(self.tasks[task].items, wrapper)

            return dict(js=js, css=css)

    def task(self, name):
        def decorator(f):
            self.tasks[name] = Task(f)
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
        # extend function scope
        global src
        def src(*paths):
            global res
            res = self.__loadResources(*paths)
            return res
        globals().update(extensions)

        for task in tasks:
            self.tasks[task].function()
            self.tasks[task].items = [filename for filename, _ in res]

        # retrieve normal scope
        del src, res
        for k in extensions:
            del globals()[k]


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
