from PySide2 import QtCore, QtGui, QtWidgets

class LineWindow(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

		self.mouseLocation = None

		self.timer = QtCore.QTimer()
		self.timer.setInterval(16)
		self.timer.timeout.connect(self._poll)

	def enable(self):
		self.timer.start()
		self.show()
		self.setGeometry(QtGui.QGuiApplication.screens()[0].availableVirtualGeometry())

	def disable(self):
		self.timer.stop()
		self.hide()

	def _poll(self):
		self.mouseLocation = QtGui.QCursor.pos() - self.pos()
		self.update()

	def paintEvent(self, event):
		super().paintEvent(event)
		if self.mouseLocation is not None:
			painter = QtGui.QPainter(self)
			painter.fillRect(0, self.mouseLocation.y()+10, self.width(), 2, QtCore.Qt.red)

app = QtWidgets.QApplication()
window = LineWindow()
window.enable()
app.exec_()