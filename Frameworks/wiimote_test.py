
"""
look into wiimote_test_gui.py for more documentation
"""

from objc import *
from Cocoa import *
import AppKit
from PyObjCTools import AppHelper

from wii_remote_framework import WiiRemoteDiscovery, WiiRemote, WiiButtonType

import PyObjCTools.Debugging as d
d.installVerboseExceptionHandler()
#d.installPythonExceptionHandler()
objc.setVerbose(1)


class WiiDelegate(NSObject):
    # note that __init__ never gets called, since the following is used to create the object instance:
    # WiiDelegate.alloc().init()
    def init(self):
        self = super(WiiDelegate, self).init()
        if self is None: return None
        self.wiimote = None
        return self

    #
    # WiiRemoteDiscovery delegates
    #

    @objc.typedSelector('v@:i')
    def WiiRemoteDiscoveryError_(self, code):
        print "PYTHON WiiRemoteDiscoveryError_ code %s. discovery stopped." % (code)

    def WiiRemoteDiscovered_(self, wiimote):
        print "PYTHON WiiRemoteDiscovered_"
        assert not self.wiimote
        self.wiimote = wiimote
        wiimote.setDelegate_(self)
        print "PYTHON enabling leds 1 & 4"
        wiimote.setLEDEnabled1_enabled2_enabled3_enabled4_(True, False, False, True)
        print "PYTHON enabling motion sensor"
        wiimote.setMotionSensorEnabled_(True)

    @objc.typedSelector('v@:@')
    def wiiRemoteDisconnected_(self, device):
        print "PYTHON wiiRemoteDisconnected_. discovery stopped."
        assert self.wiimote
        self.wiimote = None

    #
    # WiiRemote delegates
    #

    @objc.typedSelector('v@:ii@')
    def buttonChanged_isPressed_wiiRemote_(self, button_type, is_pressed, wiimote):
        print "PYTHON button changed %s" % is_pressed

    @objc.typedSelector('v@:iiii@')
    def accelerationChanged_accX_accY_accZ_wiiRemote_(self, acc_type, acc_x, acc_y, acc_z, wiimote):
        print "PYTHON accel changed %i %i %i %i" % (acc_type, acc_x, acc_y, acc_z)


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    wiidelegate = WiiDelegate.alloc().init()

    app.setDelegate_(wiidelegate)

    discovery = WiiRemoteDiscovery.alloc().init()
    discovery.setDelegate_(wiidelegate)
    print "PYTHON starting wiimote discovery"
    discovery.start()

    #AppHelper.runEventLoop()
    try:
        AppHelper.runConsoleEventLoop(installInterrupt=True)
    except KeyboardInterrupt:
        print "error"
        AppHelper.stopEventLoop()

    #runloop.run()
    #AppKit.NSApp.run()
    #AppHelper.stopEventLoop()

    discovery.stop()
