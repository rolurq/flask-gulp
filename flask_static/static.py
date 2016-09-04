import os
from collections import namedtuple

from flask import url_for
from jinja2 import Markup

import wildcard
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
        app.config.setdefault('STATIC_WATCHER_INTERVAL', 1)
        app.config.setdefault('STATIC_INITIAL_PATH', app.root_path)
        app.config.setdefault('STATIC_GENERATED_LINKS_PATH', app.static_folder)
        app.config.setdefault('STATIC_RUN_ON_REFRESH', False)
        self.app = app

        @app.context_processor
        def context_processor():
            def build_html(wrapper, *tasks):
                root = app.config.get('STATIC_GENERATED_LINKS_PATH')
                markup = ''
                temp = os.path.sep
                os.path.sep = '/'
                for task in tasks:
                    markup += Markup('<!-- %s -->\n' % task)
                    markup += Markup('\n'.join(
                        (wrapper %
                            url_for('static', filename=
                                    os.path.relpath(item, root))
                            for item in self.tasks[task].items)))
                    markup += '\n'
                os.path.sep = temp
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

        watcher = Watcher(paths, self, tasks, debug=self.app.debug,
                          interval=self.app.config.
                          get('STATIC_WATCHER_INTERVAL'))
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

    def runall(self):
        self.run(*(task for task in self.tasks))


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
                if not dest and generated:
                    print(generated)
                self.resources[i] = dest, generated
        return self

    def add(self, filename):
        f = open(filename)
        self.resources.append((filename, f.read()))
        f.close()

    def __iter__(self):
        return iter(self.resources)
