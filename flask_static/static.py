import os
import re
from collections import namedtuple

from flask import url_for
from jinja2 import Markup

from flask_static.extensions import extensions
from flask_static.watcher import Watcher


Task = namedtuple('Task', ['function', 'items', 'watched'])


class Static(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
        self.tasks = {}

    def init_app(self, app):
        app.config.setdefault('STATIC_WATCHER_INTERVAL', 2)
        app.config.setdefault('STATIC_INITIAL_PATH', app.root_path)
        app.config.setdefault('STATIC_GENERATED_LINKS_PATH', app.static_folder)
        self.app = app

        @app.context_processor
        def context_processor():
            def build_html(wrapper, *tasks):
                root = app.config.get('STATIC_GENERATED_LINKS_PATH')
                markup = ''
                for task in tasks:
                    markup += Markup('<!-- %s -->\n' % task)
                    markup += Markup('\n'.join(
                        (wrapper %
                            url_for('static', filename=
                                    os.path.relpath(item, root))
                            for item in self.tasks[task].items)))
                    markup += '\n'
                return markup

            def css(*tasks):
                """
                    Create links to style files using results from task
                """
                # run unwatched tasks
                self.run(*(task for task in tasks
                           if not self.tasks[task].watched))
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

                # run unwatched tasks
                self.run(*(task for task in tasks
                           if not self.tasks[task].watched))
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
            self.tasks[name] = Task(function=f, items=[], watched=False)

            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
        return decorator

    def watch(self, path, *tasks):
        for task in tasks:
            self.tasks[task] = self.tasks[task]._replace(watched=True)

        watcher = Watcher(path, self, tasks, debug=self.app.debug,
                          interval=self.app.config.
                          get('STATIC_WATCHER_INTERVAL'))
        watcher.start()

    def findFiles(self, *paths):
        if self.app is None:
            raise ValueError('You should pass a valid application')
        wildcards = [re.compile(r) for r in paths]
        root = self.app.config.get('STATIC_INITIAL_PATH')

        for dirpath, _, filenames in os.walk(root):
            rpath = os.path.relpath(dirpath, root)
            # TODO: delete unnecesary directories
            for f in filenames:
                for reg in wildcards:
                    if reg.match(os.path.join(rpath, f)):
                        yield os.path.join(dirpath, f)

    def __loadResources(self, *paths):
        res = StaticResources()
        for filename in self.findFiles(*paths):
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
            if self.app.debug:
                print('[*] running %s...' % task)
            t.function()
            self.tasks[task] = t._replace(items=[filename
                                                 for filename, _ in res
                                                 if filename])
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
