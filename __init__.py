import re
import os

from jinja2 import Markup
from flask import url_for
from collections import namedtuple
Task = namedtuple('Task', ['function', 'items'])


class Static(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
        self.tasks = {}

    def init_app(self, app):
        self.root_path = app.root_path

        @app.context_processor
        def context_processor():
            def build_html(items, wrapper):
                return Markup('\n'.join((wrapper %
                    url_for('static', filename=item) for item in items)))

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
        pass

    def __loadResources(*paths):
        if app is None:
            raise ValueError('You should pass a valid application')
        wildcards = [re.compile(r) for r in paths]

        res = StaticResources()
        for dirpath, _, filenames in os.walk(self.root_path):
            rpath = os.relpath(dirpath, root)
            # TODO: delete unnecesary directories
            for f in filenames:
                for reg in wildcards:
                    if reg.match(os.join(rpath, f)):
                        res.add(os.join(dirpath, f))
        return res

    def run(self, *tasks):
        for t in tasks:
            global src
            src = self.__loadResources
            self.tasks[t].function()
            del src


class StaticResources(object):

    def __init__(self, *files):
        self.content = []
        for f in files:
            self.add(f)

    def pipe(self, ext):
        self.content = ext(self.content)
        return self

    def add(self, filename):
        f = open(filename)
        self.content.append((filename, f.read()))
        f.close()

