import argparse, pkg_resources

from PySide2 import QtCore, QtGui, QtWidgets

from system_hotkey import SystemHotkey

import argparseqt.gui
import argparseqt.groupingTools

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

		self.parseArgs()

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

	def parseArgs(self):
		self.parser = argparse.ArgumentParser()

		self.parser.add_argument('--height', type=int, default=20, help='Line height')
		self.parser.add_argument('--offset', type=int, default=0, help='Line offset')

		self.parser.add_argument('--red', type=int, default=255, help='Red value (0-255)')
		self.parser.add_argument('--green', type=int, default=128, help='Green value (0-255)')
		self.parser.add_argument('--blue', type=int, default=1, help='Blue value (0-255)')
		self.parser.add_argument('--alpha', type=int, default=32, help='Alpha value (0-255)')

		self.settings = argparseqt.groupingTools.parseIntoGroups(self.parser)
		self.dialog = argparseqt.gui.ArgDialog(self.parser, '👓 Line Reader Settings')
		self.dialog.setValues(self.settings)
		self.dialog.accepted.connect(self.onSettingsAccepted)

	def buildTrayIcon(self):
		self.trayIcon = QtWidgets.QSystemTrayIcon(QtGui.QIcon(getAssetPath('icon.png')), self)
		self.trayIcon.show()
		self.trayIcon.setToolTip('Line Reader')
		self.trayIcon.activated.connect(self.onTrayIconActivated)

		self.trayMenu = QtWidgets.QMenu('👓 Line Reader')
		self.trayMenu.addAction('Options...')
		self.trayMenu.addAction('Toggle')
		self.trayMenu.addAction('Exit')

		self.trayMenu.triggered.connect(self.onActionTriggered)

		self.trayIcon.setContextMenu(self.trayMenu)

	def onSettingsAccepted(self):
		self.settings = self.dialog.getValues()
		self.update()

	def onHotkeyTriggered(self):
		self.toggle()

	def onTrayIconActivated(self):
		self.toggle()

	def onActionTriggered(self, action):
		if action.text() == 'Options...':
			self.dialog.show()
		elif action.text() == 'Exit':
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
			painter.fillRect(
				0,
				self.mouseLocation.y() + self.settings['offset'] - self.settings['height']/2,
				self.width(),
				self.settings['height'],
				QtGui.QColor(
					self.settings['red'],
					self.settings['green'],
					self.settings['blue'],
					self.settings['alpha']
				)
			)

app = QtWidgets.QApplication()
window = LineWindow()
window.enable()
app.exec_()