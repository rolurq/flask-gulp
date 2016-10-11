from __future__ import print_function
import os
import sys
from collections import OrderedDict

from flask import url_for
from jinja2 import Markup

from . import wildcard, File, Task
from .extensions import extensions
from .watcher import Watcher


class Static(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
        self.tasks = OrderedDict()

    def init_app(self, app):
        app.config.setdefault('STATIC_WATCHER_INTERVAL', 1)
        app.config.setdefault('STATIC_INITIAL_PATH', app.root_path)
        app.config.setdefault('STATIC_GENERATED_LINKS_PATH', app.static_folder)
        app.config.setdefault('STATIC_RUN_ON_REFRESH', False)
        app.config.setdefault('STATIC_DEBUG', app.debug)
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
                            url_for('static', filename=os.path
                                    .relpath(item, root).replace('\\', '/'))
                            for item in self.tasks[task].items)))
                    markup += '\n'
                return markup

            def css(*tasks):
                """
                    Create links to style files using results from task
                """
                run_tasks = self.app.config.get('STATIC_RUN_ON_REFRESH')

                # run unwatched tasks
                if run_tasks:
                    self.run(*(task for task in tasks
                               if not self.tasks[task].watched))
                return build_html('<link rel="stylesheet" href="%s"/>', *tasks)

            def js(*tasks, **options):
                """
                    Create links to script files using results from task
                """
                run_tasks = self.app.config.get('STATIC_RUN_ON_REFRESH')

                options.setdefault('defer', False)
                options.setdefault('asynchro', False)
                attrs = ['src="%s"']
                if options['defer']:
                    attrs.append('defer')
                if options['asynchro']:
                    attrs.append('async')

                # run unwatched tasks
                if run_tasks:
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

    def watch(self, paths, *tasks):
        for task in tasks:
            self.tasks[task] = self.tasks[task]._replace(watched=True)

        watcher = Watcher(paths, self, tasks,
                          debug=self.app.config.get('STATIC_DEBUG'),
                          interval=self.app.config
                          .get('STATIC_WATCHER_INTERVAL'))
        self.run(*tasks)
        watcher.daemon = True
        watcher.start()

    def findFiles(self, *paths):
        if self.app is None:
            raise ValueError('You should pass a valid application')
        root = self.app.config.get('STATIC_INITIAL_PATH')

        for path in paths:
            for filename in wildcard.wildcard(os.path.join(root, path)):
                yield filename

    def __loadResources(self, *paths):
        res = StaticResources()
        for filename, relativ in self.findFiles(*paths):
            res.add(filename, relativ)
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
            if self.app.config.get('STATIC_DEBUG'):
                print('[*] running %s...' % task)
            t.function()
            res.close()
            self.tasks[task] = t._replace(items=[f.filename
                                                 for f in res
                                                 if f.filename])
            # retrieve normal scope
            del t.function.__globals__['src']
            for k in extensions:
                del t.function.__globals__[k]

    def runall(self):
        self.run(*(task for task in self.tasks))


class StaticResources(object):

    def __init__(self, *files):
        self.resources = []
        for f in files:
            self.add(f)
        self.gen = None

    def pipe(self, extension):
        if self.gen:
            self.close()
        self.gen = extension(self.resources)
        return self

    def close(self):
        self.resources = []
        for generated in self.gen:
            if not generated.filename and generated.content:
                print(generated.content, file=sys.stderr)
            else:
                self.resources.append(generated)

    def add(self, filename, rel):
        self.resources.append(File(filename, rel, None))

    def __iter__(self):
        return iter(self.resources)
