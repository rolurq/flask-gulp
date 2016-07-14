from threading import Thread
from werkzeug._reloader import ReloaderLoop

class Watcher(Thread, ReloaderLoop):

    def __init__(self, dirname, interval=1, static, tasks, *args, **kwargs):
        self.dirname = dirname
        self.static = static
        self.tasks = tasks
        super(Watcher, self).__init__(*args, **kwargs)
        ReloaderLoop.__init__(self, interval=interval)

    def run(self):
        time = None
        while True:
            try:
                mtime = os.stat(dirname).st_mtime
            except OSError:
                continue

            if time is None:
                time = mtime
            elif mtime > time:
                self.static.run(self.tasks)
                break
            self._sleep(self.interval)

