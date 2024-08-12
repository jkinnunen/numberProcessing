# -*- coding: UTF-8 -*-
# NumberProcessing
# A global plugin for NVDA
# Copyright Alberto Buffolino, released under GPL
# Add-on to read digit by digit any number of specified length
# from an experimental idea of Derek Riemer
import addonHandler
import config
import globalPluginHandler
import globalVars
import gui
import re
import speech
import ui
import wx

from enum import Enum
from gui import guiHelper, nvdaControls, settingsDialogs
from scriptHandler import script, getLastScriptRepeatCount


addonHandler.initTranslation()

CURRENCY_SYMBOLS = (
	"$",
	"💵",
	"€",
	"💶",
	"£",
	"💷",
	"¥",
	"💴",
)
confspec = {
	"autoEnable": "boolean(default=false)",
	"userMinLen": "integer(default=2)",
}
config.conf.spec["numberProcessing"] = confspec
profileStatus = {}

class Status(Enum):

	DISABLED = 0
	AUTO_ENABLED = 1
	MANUAL_ENABLED = 2

# (re)load config
def loadConfig():
	global myConf, exp1, exp2, curProfile
	myConf = config.conf["numberProcessing"]
	autoEnable = myConf["autoEnable"]
	userMinLen = myConf["userMinLen"]
	exp1 = re.compile(r'\d{%s,}'%userMinLen)
	symbols = ''.join(CURRENCY_SYMBOLS)
	exp2 = re.compile(r'([%s])?\s*([\d,.]+)'%symbols)
	curProfile = config.conf.profiles[-1].name
	# adjust status for current profile
	if autoEnable:
		profileStatus[curProfile] = Status.AUTO_ENABLED
	# adjust after disabling auto enable in settings
	elif profileStatus.get(curProfile, Status.DISABLED) == Status.AUTO_ENABLED:
		profileStatus[curProfile] = Status.DISABLED

loadConfig()

def filter_numberProcessing(speechSequence):
	if not isEnabled():
		return speechSequence
	newSpeechSequence = []
	for item in speechSequence:
		if not isinstance(item, str):
			newSpeechSequence.append(item)
			continue
		# pre-process to avoid problems with decimal separator,
		# appending currency sign to the end of the amount
		item = exp2.sub(r'\2\1', item)
		# add whitespace around digits
		item = exp1.sub(replaceFunc, item)
		newSpeechSequence.append(item)
	return newSpeechSequence

def isEnabled():
	status = profileStatus.get(curProfile, Status.DISABLED)
	return bool(status.value)

def replaceFunc(match):
	# group(0) returns digits captured by match
	fixedText = '  '.join(list(match.group(0)))
	return fixedText


class NumberProcessingSettings(settingsDialogs.SettingsPanel):
	"""Class to define settings."""

	# Translators: title of settings dialog
	title = _("Number Processing")

	def makeSettings(self, settingsSizer):
		loadConfig()
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label for autoEnable  checkbox in settings
		autoEnableText = _("Processing automatically enabled")
		self.autoEnableCheckBox = settingsSizerHelper.addItem(wx.CheckBox(self, label=autoEnableText))
		self.autoEnableCheckBox.SetValue(myConf["autoEnable"])
		# Translators: label for userMinLen checkbox in settings
		userMinLenLabelText = _("Minimum number of digits to process individually")
		self.userMinLenEdit = settingsSizerHelper.addLabeledControl(
			userMinLenLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=2,
			initial=myConf["userMinLen"])

	def onSave(self):
		# Update Configuration
		myConf["autoEnable"] = self.autoEnableCheckBox.IsChecked()
		myConf["userMinLen"] = self.userMinLenEdit.GetValue()
		# reload new config
		loadConfig()


class QuickSettingsDialog(wx.Dialog):

	def __init__(self, parent, profileName):
		if profileName is None:
			profileName = _("normal configuration")
		title = ' - -'.join([_("Number Processing Settings"), profileName])
		super(QuickSettingsDialog, self).__init__(parent, title=title)
		loadConfig()
		sizerHelper = guiHelper.BoxSizerHelper(self, wx.VERTICAL)
		# Translators: label for userMinLen edit box in settings
		userMinLenLabelText = _("Minimum number of digits to process individually")
		self.userMinLenEdit = sizerHelper.addLabeledControl(
			userMinLenLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=2,
			initial=myConf["userMinLen"])
		sizerHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.userMinLenEdit.SetFocus()

	def onOk(self, evt):
		# Update Configuration
		myConf["userMinLen"] = self.userMinLenEdit.GetValue()
		# reload new config
		loadConfig()
		self.Destroy()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()
		loadConfig()
		config.post_configProfileSwitch.register(self.handleConfigProfileSwitch)
		speech.extensions.filter_speechSequence.register(filter_numberProcessing)

	def createMenu(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(NumberProcessingSettings)

	def terminate(self):
		profileStatus.clear()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(NumberProcessingSettings)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Pressed once, enables/disables digit processing; twice, launches quick settings"),
		gesture="kb:nvda+shift+l"
	)
	def script_toggleDigitManager(self, gesture, repeating=False):
		if getLastScriptRepeatCount() and not repeating:
			self.launchQuickSettings()
			self.script_toggleDigitManager(None, repeating=True)
			return
		loadConfig()
		if not isEnabled():
			profileStatus[curProfile] = Status.MANUAL_ENABLED
			message = _("Digit processing on")
		else:
			profileStatus[curProfile] = Status.DISABLED
			message = _("Digit processing off")
		if not repeating:
			ui.message(message)

	def launchQuickSettings(self):
		def run():
			gui.mainFrame.prePopup()
			d = QuickSettingsDialog(None, curProfile)
			if d:
				d.Show()
			gui.mainFrame.postPopup()
		wx.CallAfter(run)

	def handleConfigProfileSwitch(self):
		loadConfig()
