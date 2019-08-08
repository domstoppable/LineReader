import pkg_resources

from PySide2 import QtCore, QtGui, QtWidgets

from system_hotkey import SystemHotkey

def getAssetPath(resource):
	return pkg_resources.resource_filename(__name__, 'assets/' + resource)

class HotkeyManager(QtCore.QObject):
	triggered = QtCore.Signal(object)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.keys = []
		self.hk = SystemHotkey()

	def addKey(self, keyCombo):
		self.hk.register(keyCombo, callback=self.triggered.emit)


class LineWindow(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

		self.mouseLocation = None

		self.buildTrayIcon()

		self.hotkeyManager = HotkeyManager()
		self.hotkeyManager.addKey(('super', 'shift', 'l'))
		self.hotkeyManager.triggered.connect(self.onHotkeyTriggered)

		self.timer = QtCore.QTimer()
		self.timer.setInterval(16)
		self.timer.timeout.connect(self._poll)


	def buildTrayIcon(self):
		self.trayIcon = QtWidgets.QSystemTrayIcon(QtGui.QIcon(getAssetPath('icon.png')), self)
		self.trayIcon.show()
		self.trayIcon.setToolTip('Line Reader')
		self.trayIcon.activated.connect(self.onTrayIconActivated)

		self.trayMenu = QtWidgets.QMenu('👓 Line Reader')
		self.trayMenu.addAction('Toggle')
		self.trayMenu.addAction('Exit')

		self.trayMenu.triggered.connect(self.onActionTriggered)

		self.trayIcon.setContextMenu(self.trayMenu)

	def onHotkeyTriggered(self):
		self.toggle()

	def onTrayIconActivated(self):
		self.toggle()

	def onActionTriggered(self, action):
		if action.text() == 'Exit':
			QtWidgets.QApplication.instance().exit()
		elif action.text() == 'Toggle':
			self.toggle()

	def enable(self):
		self.timer.start()
		self.show()
		self.setGeometry(QtGui.QGuiApplication.screens()[0].availableVirtualGeometry())

	def disable(self):
		self.timer.stop()
		self.hide()

	def toggle(self):
		if self.isVisible():
			self.disable()
		else:
			self.enable()

	def _poll(self):
		self.mouseLocation = QtGui.QCursor.pos() - self.pos()
		self.update()

	def paintEvent(self, event):
		super().paintEvent(event)
		if self.mouseLocation is not None:
			painter = QtGui.QPainter(self)
			painter.fillRect(0, self.mouseLocation.y()+10, self.width(), 2, QtGui.QColor(255, 128, 0, 96))

app = QtWidgets.QApplication()
window = LineWindow()
window.enable()
app.exec_()