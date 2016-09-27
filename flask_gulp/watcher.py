import os
from threading import Thread

from werkzeug._reloader import ReloaderLoop


class Watcher(Thread, ReloaderLoop):

    def __init__(self, paths, static, tasks, interval=1, *args, **kwargs):
        self.paths = paths
        self.static = static
        self.tasks = tasks
        self.debug = kwargs.get('debug')
        del kwargs['debug']
        super(Watcher, self).__init__(*args, **kwargs)
        ReloaderLoop.__init__(self, interval=interval)

    def run(self):
        times = {}
        while not self._Thread__stopped:
            for filename, _ in self.static.findFiles(*self.paths):
                try:
                    currtime = os.stat(filename).st_mtime
                except OSError:
                    continue

                oldtime = times.get(filename)
                if oldtime and currtime > oldtime:
                    if self.debug:
                        print('[*] detected changes on %s' % filename)
                    self.static.run(*self.tasks)
                    times[filename] = currtime
                    break
                times[filename] = currtime
            self._sleep(self.interval)
