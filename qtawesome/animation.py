from qtpy.QtCore import QTimer


class Spin:
    def __init__(self, parent_widget, interval=10, step=1, autostart=True):
        self.parent_widget = parent_widget
        self.interval = interval
        self.step = step
        self.autostart = autostart

        self.info = {}

    def _update(self):
        if self.parent_widget in self.info:
            timer, angle, step = self.info[self.parent_widget]

            if angle >= 360:
                angle = 0

            angle += step
            self.info[self.parent_widget] = timer, angle, step
            self.parent_widget.update()

    def setup(self, icon_painter, painter, rect):
        if self.parent_widget not in self.info:
            timer = QTimer(self.parent_widget)
            timer.timeout.connect(self._update)
            self.info[self.parent_widget] = [timer, 0, self.step]
            if self.autostart:
                timer.start(self.interval)
        else:
            timer, angle, self.step = self.info[self.parent_widget]
            x_center = rect.width() * 0.5
            y_center = rect.height() * 0.5
            painter.translate(x_center, y_center)
            painter.rotate(angle)
            painter.translate(-x_center, -y_center)

    def start(self):
        timer: QTimer = self.info[self.parent_widget][0]
        timer.start(self.interval)

    def stop(self):
        timer: QTimer = self.info[self.parent_widget][0]
        timer.stop()


class Pulse(Spin):
    def __init__(self, parent_widget, autostart=True):
        super().__init__(parent_widget, interval=300, step=45, autostart=autostart)
