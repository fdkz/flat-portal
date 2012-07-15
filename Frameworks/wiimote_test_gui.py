
"""
random notes
------------

http://stackoverflow.com/questions/626898/how-do-i-create-delegates-in-objective-c
http://svn.red-bean.com/pyobjc/tags/pyobjc-1.3.6/Doc/classes.html
http://www.cocoabuilder.com/archive/cocoa/167803-writing-application-without-interface-builder.html
http://developer.apple.com/library/mac/#documentation/Cocoa/Reference/ApplicationKit/Miscellaneous/AppKit_Functions/Reference/reference.html

for objc.typedSelector(..)
    https://developer.apple.com/library/mac/#documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html

Declaring conformance to a formal protocol is done by using the formal protocol as a mix-in, and by implementing its methods:

    NSLocking = objc.protocolNamed('NSLocking')
    class MyLockingObject(NSObject, NSLocking):
        def lock(self):
            pass
        def unlock(self):
            pass
"""

from objc import *
from Cocoa import *
import AppKit
from PyObjCTools import AppHelper

from wii_remote_framework import WiiRemoteDiscovery, WiiRemote
from wii_remote_framework import WiiButtonType

import PyObjCTools.Debugging as d
d.installVerboseExceptionHandler()
objc.setVerbose(1)

# no such module
#from PyObjCTools import Signals
#Signals.dumpStackOnFatalSignal()
#NSLog(txt)

class WiiDelegate(NSObject):
    # note that __init__ never gets called, since the following is used to create the object instance:
    # WiiDelegate.alloc().init()
    def init(self):
        self = super(WiiDelegate, self).init()
        if self is None: return None
        self.wiimote = None
        return self

    #
    # GUI delegates
    #

    def applicationDidFinishLaunching_(self, sender):
        print "PYTHON hello"

    def stopDiscovery_(self, sender):
        print "PYTHON stopping the discovery process"
        if self.wiimote:
            self.wiimote.closeConnection()
            self.wiimote = None
        global discovery
        discovery.stop()

    def startDiscovery_(self, sender):
        print "PYTHON starting the discovery process"
        if self.wiimote:
            self.wiimote.closeConnection()
            self.wiimote = None
        global discovery
        discovery.start()

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

    #- (void) buttonChanged:(WiiButtonType)type isPressed:(BOOL)isPressed wiiRemote:(WiiRemote*)wiiRemote
    # TODO: is v@:ii@ really correct? no memory leaks anywhere?
    # @objc.typedSelector('v@:ii^WiiRemote'):
    #     ValueError: invalid signature
    # @objc.typedSelector('v@:ii^@'):
    #     2012-07-08 02:53:05.447 Python[22505:60f] PyObjCPointer created: at 0x103d76f90 of type @
    @objc.typedSelector('v@:ii@')
    def buttonChanged_isPressed_wiiRemote_(self, button_type, is_pressed, wiimote):
        print "PYTHON button changed %s" % is_pressed

    @objc.typedSelector('v@:iiii@')
    def accelerationChanged_accX_accY_accZ_wiiRemote_(self, acc_type, acc_x, acc_y, acc_z, wiimote):
        print "PYTHON accel changed %i %i %i %i" % (acc_type, acc_x, acc_y, acc_z)


if __name__ == "__main__":

    app = NSApplication.sharedApplication()


    win = NSWindow.alloc()
    frame = ((200.0, 300.0), (340.0, 100.0))
    win.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
    win.setTitle_( 'wii' )
    win.setLevel_( 3 ) # floating window

    hel = NSButton.alloc().initWithFrame_ (((10.0, 10.0), (110.0, 80.0)))
    win.contentView().addSubview_ (hel)
    hel.setBezelStyle_( 4 )
    hel.setTitle_( 'stop discovery' )
    hel.setTarget_( app.delegate() )
    hel.setAction_( "stopDiscovery:" )

    hel = NSButton.alloc().initWithFrame_ (((130.0, 10.0), (110.0, 80.0)))
    win.contentView().addSubview_ (hel)
    hel.setBezelStyle_( 4 )
    hel.setTitle_( 'start discovery' )
    hel.setTarget_( app.delegate() )
    hel.setAction_( "startDiscovery:" )

    bye = NSButton.alloc().initWithFrame_ (((250.0, 10.0), (80.0, 80.0)))
    win.contentView().addSubview_ (bye)
    bye.setBezelStyle_( 4 )
    bye.setTarget_ (app)
    bye.setAction_ ('stop:')
    bye.setEnabled_ ( 1 )
    bye.setTitle_( 'exit' )

    win.display()
    win.orderFrontRegardless()


    wiidelegate = WiiDelegate.alloc().init()
    app.setDelegate_(wiidelegate)

    discovery = WiiRemoteDiscovery.alloc().init()
    discovery.setDelegate_(wiidelegate)
    discovery.start()

    # TODO:
    #  what's the difference between this:
    #    runloop = NSRunLoop.currentRunLoop()
    #    runloop.run()
    #  and this:
    #    AppHelper.runEventLoop()

    # TODO: close the program reliably on errors and on keyboard interrupts.
    #       installInterrupt parameter seems to do nothing.
    AppHelper.runEventLoop(installInterrupt=True)

    # no, this does not help against the WiiRemoteDiscoveryError_ error code 188 (0xbc)
    #if self.wiidelegate.wiimote:
    #    self.wiimote.closeConnection()

    discovery.stop()
