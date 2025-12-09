"""Dialogs package"""
from .camera_settings import CameraSettingsDialog
from .model_settings import ModelSettingsDialog
from .report_dialog import ReportDialog
from .camera_profiles_dialog import CameraProfilesDialog
from .model_profiles_dialog import ModelProfilesDialog
from .mqtt_settings_dialog import MQTTSettingsDialog

__all__ = ['CameraSettingsDialog', 'ModelSettingsDialog', 'ReportDialog',
           'CameraProfilesDialog', 'ModelProfilesDialog', 'MQTTSettingsDialog']
