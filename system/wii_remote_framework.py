# Load the framework relative to the executable in the .app bundle

# pyobjc doc recommended moving the framework wrapper to a separate python file.

import sys
import objc

# if app is standalone, import the framework from the app itself. else use the development path.
if hasattr(sys, "frozen"):
    # TODO: what is this objc.pathForFramework?
    #objc.loadBundle("WiiRemoteFramerowk", globals(), bundle_path=objc.pathForFramework(u'@executable_path@/../../Frameworks/WiiRemote.framework'))
    objc.loadBundle("WiiRemoteFramerowk", globals(), bundle_path=u'@executable_path@/../../Frameworks/WiiRemote.framework')
else:
#    objc.loadBundle("WiiRemoteFramework", globals(), bundle_path=u"Frameworks/WiiRemote.framework")
    objc.loadBundle("WiiRemoteFramework", globals(), bundle_path=u"/Users/fdkz/Library/Developer/Xcode/DerivedData/WiiRemoteFramework-azcjpedhwzbkwigedekxtdjiaqcs/Build/Products/Debug/WiiRemote.framework")

# pyobjc 2.3 doc: It is currently necessary to import the wrapper modules for all frameworks that are used by
# your framework. Not doing this may lead to subtle bugs in other parts of the code. This is a limitation of
# PyObjC that will be lifted in a future version.
objc.loadBundle('IOBluetooth', globals(), bundle_path=u'/System/Library/Frameworks/IOBluetooth.framework')

#
# enums from WiiRemote.h
#

class WiiButtonType:
    WiiRemoteAButton = 0
    WiiRemoteBButton = 1
    WiiRemoteOneButton = 2
    WiiRemoteTwoButton = 3
    WiiRemoteMinusButton = 4
    WiiRemoteHomeButton = 5
    WiiRemotePlusButton = 6
    WiiRemoteUpButton = 7
    WiiRemoteDownButton = 8
    WiiRemoteLeftButton = 9
    WiiRemoteRightButton = 10

    WiiNunchukZButton = 11
    WiiNunchukCButton = 12

    WiiClassicControllerXButton = 13
    WiiClassicControllerYButton = 14
    WiiClassicControllerAButton = 15
    WiiClassicControllerBButton = 16
    WiiClassicControllerLButton = 17
    WiiClassicControllerRButton = 18
    WiiClassicControllerZLButton = 19
    WiiClassicControllerZRButton = 20
    WiiClassicControllerUpButton = 21
    WiiClassicControllerDownButton = 22
    WiiClassicControllerLeftButton = 23
    WiiClassicControllerRightButton = 24
    WiiClassicControllerMinusButton = 25
    WiiClassicControllerHomeButton = 26
    WiiClassicControllerPlusButton = 27

class WiiExpansionPortType:
    WiiExpNotAttached = 0
    WiiNunchuk = 1
    WiiClassicController = 2

class WiiAccelerationSensorType:
    WiiRemoteAccelerationSensor = 0
    WiiNunchukAccelerationSensor = 1
