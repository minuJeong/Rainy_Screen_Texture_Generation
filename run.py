"""
author: minujeong
"""

import moderngl as mg
import numpy as np

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class ObserverPollingThread(QtCore.QThread):

    class _H(FileSystemEventHandler):

        def __init__(self, callback):
            self.callback = callback

        def on_modified(self, e):
            self.callback()

    on_modified = QtCore.pyqtSignal()

    def __init__(self):
        super(ObserverPollingThread, self).__init__()

    def on_mod(self):
        self.on_modified.emit()

    def run(self):
        observer = Observer()
        handler = ObserverPollingThread._H(self.on_mod)
        observer.schedule(handler, "./gl")
        observer.start()
        observer.join()


class PreviewRenderer(QtWidgets.QOpenGLWidget):

    def __init__(self):
        super(PreviewRenderer, self).__init__()

    def read(self, path):
        with open(path, 'r') as fp:
            return fp.read()

    def recompile_shaders(self):
        try:
            self.cs = self.gl.compute_shader(self.read("./gl/compute.glsl"))

            print("RECO")

        except Exception as e:
            print(e)

    def initializeGL(self):

        self.gl = mg.create_context()

        if not self.gl:
            raise Exception("Can't create gl context")

        self.recompile_shaders()

        self.observer_thread = ObserverPollingThread()
        self.observer_thread.on_modified.connect(self.recompile_shaders)
        self.observer_thread.start()

    def paintGL(self):
        pass


def main():
    app = QtWidgets.QApplication([])
    renderer = PreviewRenderer()
    renderer.show()
    app.exec()


if __name__ == "__main__":
    main()
