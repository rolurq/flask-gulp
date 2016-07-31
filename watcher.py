import os

from threading import Thread
from werkzeug._reloader import ReloaderLoop


class Watcher(Thread, ReloaderLoop):

    def __init__(self, paths, static, tasks, interval=1, *args, **kwargs):
        self.paths = paths
        self.static = static
        self.tasks = tasks
        super(Watcher, self).__init__(*args, **kwargs)
        ReloaderLoop.__init__(self, interval=interval)

    def run(self):
        times = {}
        while not self._Thread__stopped:
            for filename in self.paths:
                try:
                    currtime = os.stat(filename).st_mtime
                except OSError:
                    continue

                oldtime = times.get(filename)
                if oldtime and currtime > oldtime:
                    self.static.run(*self.tasks)
                times[filename] = mtime
            self._sleep(self.interval)

