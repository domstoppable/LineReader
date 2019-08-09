import argparse, pkg_resources

from PySide2 import QtCore, QtGui, QtWidgets

from system_hotkey import SystemHotkey

import argparseqt.gui
import argparseqt.groupingTools
import argparseqt.typeHelpers

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

		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

		self.mouseLocation = None

		self.buildTrayIcon()

		self.hotkeyManager = HotkeyManager()
		self.hotkeyManager.addKey(('super', 'shift', 'l'))
		self.hotkeyManager.triggered.connect(self.onHotkeyTriggered)

		self.timer = QtCore.QTimer()
		self.timer.setInterval(33)
		self.timer.timeout.connect(self._poll)

	def parseArgs(self):
		self.parser = argparse.ArgumentParser()

		self.parser.add_argument('--height', type=int, default=20, help='Line height')
		self.parser.add_argument('--offset', type=int, default=0, help='Line offset')

		self.parser.add_argument('--color', type=argparseqt.typeHelpers.rgba, default='ff800020', help='Color')

		self.settings = argparseqt.groupingTools.parseIntoGroups(self.parser)
		self.dialog = argparseqt.gui.ArgDialog(self.parser, '👓 Line Reader Settings')
		self.dialog.setValues(self.settings)

		self.dialog.valueAdjusted.connect(self.onValueAdjusted)
		self.dialog.accepted.connect(self.onSettingsAccepted)
		self.dialog.rejected.connect(self.onSettingsRejected)

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

	def onValueAdjusted(self):
		self.settings = self.dialog.getValues()
		self.update()

	def onSettingsAccepted(self):
		# TODO: save setings for persistance
		self.settings = self.dialog.getValues()
		self.update()

	def onSettingsRejected(self):
		self.settings = self.preservedSettings
		self.update()

	def onHotkeyTriggered(self):
		self.toggle()

	def onTrayIconActivated(self, reason):
		if reason in [QtWidgets.QSystemTrayIcon.DoubleClick, QtWidgets.QSystemTrayIcon.MiddleClick]:
			self.showDialog()
		else:
			self.toggle()

	def showDialog(self):
		self.preservedSettings = self.settings
		self.dialog.setValues(self.settings)
		self.dialog.show()

	def onActionTriggered(self, action):
		if action.text() == 'Options...':
			self.showDialog()
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
				QtGui.QColor(*self.settings['color']),
			)

app = QtWidgets.QApplication()
window = LineWindow()
window.enable()
app.exec_()