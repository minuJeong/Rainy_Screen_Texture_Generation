"""
author: minujeong
"""

import time

import moderngl as mg
import numpy as np
import imageio as ii

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


class ScreenMesh(object):
    def __init__(self, gl):
        super(ScreenMesh, self).__init__()
        vbo = [-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0]
        ibo = [0, 1, 2, 2, 1, 3]
        self.vbo = gl.buffer(np.array(vbo).astype(np.float32))
        self.content = [(self.vbo, "2f", "in_pos")]
        self.ibo = gl.buffer(np.array(ibo).astype(np.int32))


class PreviewRenderer(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(PreviewRenderer, self).__init__()
        self.u_width, self.u_height, self.u_depth = 304, 304, 304
        self.gx = int(self.u_width / 4)
        self.gy = int(self.u_height / 4)
        self.gz = int(self.u_depth / 4)
        self.buffer_size = self.u_width * self.u_height * self.u_depth * 4 * 4

        self.setMinimumSize(self.u_width, self.u_height)
        self.setMaximumSize(self.u_width, self.u_height)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

    def read(self, path):
        with open(path, "r") as fp:
            return fp.read()

    def set_uniform(self, uniform_dict, *programs):
        for program in programs:
            for n, v, in uniform_dict.items():
                if n not in program:
                    continue

                program[n].value = v

    def recompile_shaders(self):
        try:
            self.cs = self.gl.compute_shader(self.read("./gl/compute.glsl"))
            self.preview_program = self.gl.program(
                vertex_shader=self.read("./gl/preview_verts.glsl"),
                fragment_shader=self.read("./gl/preview_frags.glsl"),
            )

            uniform_dict = {
                "u_width": self.u_width,
                "u_height": self.u_height,
                "u_depth": self.u_depth,
            }

            self.set_uniform(uniform_dict, self.cs, self.preview_program)

            self.vao = self.gl.vertex_array(
                self.preview_program, self.screen_mesh.content, self.screen_mesh.ibo
            )

            print("Shaders recompiled!")

        except Exception as e:
            print(e)

    def initializeGL(self):

        self.gl = mg.create_context()

        # build screen mesh
        self.screen_mesh = ScreenMesh(self.gl)
        self.buffer_0 = self.gl.buffer(reserve=self.buffer_size)
        self.buffer_0.bind_to_storage_buffer(0)

        if not self.gl:
            raise Exception("Can't create gl context")

        self.recompile_shaders()

        self.observer_thread = ObserverPollingThread()
        self.observer_thread.on_modified.connect(self.recompile_shaders)
        self.observer_thread.start()

    def paintGL(self):
        self.u_time = time.time() % 1000.0

        self.cs.run(self.gx, self.gy, self.gz)
        self.vao.render()
        self.update()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            print("reading buffer_0...")

            data = self.buffer_0.read()
            data = np.frombuffer(data, dtype=np.float32)
            data = np.multiply(data, 255.0)
            data = data.reshape((self.u_depth, self.u_height, self.u_width, 4))
            data = data.astype(np.uint8)

            buffer_0_writer = ii.get_writer("buffer_0.mp4")
            for layer in data:
                buffer_0_writer.append_data(layer)


def main():
    app = QtWidgets.QApplication([])
    renderer = PreviewRenderer()
    renderer.show()
    app.exec()


if __name__ == "__main__":
    main()
