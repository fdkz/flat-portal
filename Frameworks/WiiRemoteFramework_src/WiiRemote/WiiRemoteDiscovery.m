//
//  WiiRemoteDiscovery.m
//  DarwiinRemote
//
//  Created by Ian Rickard on 12/9/06.
//  Copyright 2006 __MyCompanyName__. All rights reserved.
//
//  changelog:
//    2012.07.05 Elmo Trolla
//      * wiimote discovery is automatically retried for 3 times, ~30 seconds total.
//      * tested, refactored, fixed some bugs, wrote comments.
//      * it's possible that it won't compile or work on anything less than macosx 10.5
//
//    - this file is a dead end! i downloaded version 0.5 of WiiRemoteFramework from sourceforge and updated that,
//      but it turns out a version >0.6 is on the DarwiinRemote svn repository. way to go, sourceforge documentation.
//      anyway, the >0.6 version doesn't work at all for me, so i'll give up and use this franken-version.
//

#import <IOBluetooth/objc/IOBluetoothDevice.h>
#import <IOBluetooth/objc/IOBluetoothHostController.h>
#import "WiiRemoteDiscovery.h"


// useful logging macros
//#ifndef NSLogDebug
//#if DEBUG
//#	define NSLogDebug(log, ...) NSLog(log, ##__VA_ARGS__)

#define LogIOReturn(result) if (result != kIOReturnSuccess) { printf ("IOReturn error (%s [%d]): system 0x%x, sub 0x%x, error 0x%x\n", __FILE__, __LINE__, err_get_system (result), err_get_sub (result), err_get_code (result)); }
//#else
//#	define NSLogDebug(log, ...)
//#	define LogIOReturn(result)
//#endif
//#endif

// TODO: how to detect wiimote fake connects?

// Use categories to get rid of "m_connectWiimote declaration not found" error if the method is at the end of the
// file. Works only starting from macosx 10.5 and shouldn't be necessary anymore on xcode 4.3.
@interface WiiRemoteDiscovery ()
	- (void) m_connectWiimote:(IOBluetoothDevice*)device;
@end


@implementation WiiRemoteDiscovery

+ (WiiRemoteDiscovery*) discoveryWithDelegate:(id)delegate {
	WiiRemoteDiscovery *out = [[WiiRemoteDiscovery alloc] init];
	[out setDelegate: delegate];
	return out;
}

// this init is from 2012.07.07 trunk version of WiiRemoteFramework
- (id) init {
	self = [super init];
	if (self != nil) {
		// cam: calling IOBluetoothLocalDeviceAvailable has two advantages:
		// 1. it sets up a event source in the run loop (bug for C version of the bluetooth api )
		// 2. it checks for the availability of the BT hardware
		//if (IOBluetoothLocalDeviceAvailable () == FALSE)
		if ([IOBluetoothHostController defaultController] == nil)
		{
			[self release];
			self = nil;			
			[NSException raise:NSGenericException format:@"Bluetooth hardware not available"];
		}		
	}
	return self;
}

- (void) dealloc {
	if (nil != inquiry)
		[self stop];
	[super dealloc];
}

- (void) setDelegate:(id)delegate {
	// prevent delegate change while there could be pending events for the previous delegate.
	assert(inquiry == nil);
	_delegate = delegate;
}

// start scanning for the wiimote.
// return:
//    kIOReturnSuccess on successful start
//    every other value is an error. calling stop is not necessary, but you can try calling start again.
- (IOReturn) start {
	if (nil != inquiry) {
		NSLog(@"Warning: Attempted to start already-started WiiRemoteDiscovery");
		return kIOReturnSuccess;
	}

	if (nil == _delegate) {
		NSLog(@"Warning: Attempted to start WiiRemoteDiscovery without delegate set");
		return kIOReturnError;
	}

	inquiry = [IOBluetoothDeviceInquiry inquiryWithDelegate: self];
	[inquiry retain];
	[inquiry setSearchCriteria:kBluetoothServiceClassMajorAny majorDeviceClass:0x05 minorDeviceClass:0x01];
	//[inquiry setUpdateNewDeviceNames: true]; // true is default
	[inquiry setUpdateNewDeviceNames:NO];

	// This line has no effect under macosx 10.6.8, the default 10 seconds remains set, although reading it out from
	// the API with inquiryLength returns the new value. And in any case - connecting to wiimote after discovering it
	// can still take up to 10s. could be that the bluetooth subsystem can't open a data-stream before the previous
	// discovery process timeout fires.
	//[inquiry setInquiryLength: 4]; // 10 is default
	//NSLog(@"start: inquiryLength %i", [inquiry inquiryLength]);

	if (nil == inquiry) {
		NSLog(@"Error: Failed to alloc IOBluetoothDeviceInquiry");
		return kIOReturnNotAttached;
	}

	IOReturn ret = [inquiry start];

	if (ret == kIOReturnSuccess) {
		// retain ourselves while there's an outstanding inquiry, don't want to go disappearing before we get
		// called as a delegate
		[self retain];
	} else {
		NSLog(@"Error: Inquiry did not start, error %d", ret);
		[inquiry setDelegate:nil];
		[inquiry release];
		inquiry = nil;
	}

	return ret;
}

- (IOReturn) stop {
	// only way that the inquiry can be non-nil is if the discovery process is active.
	if (nil == inquiry) {
		//NSLog(@"Warning: Attempted to stop already-stopped WiiRemoteDiscovery");
		return kIOReturnSuccess;
	}
	
	IOReturn ret = [inquiry stop];

	if (ret != kIOReturnSuccess && ret != kIOReturnNotPermitted) {
		// kIOReturnNotPermitted is returned if inquiry has already stopped
		NSLog(@"Error: Inquiry did not stop, error %d", ret);
	}

	[inquiry setDelegate:nil];
	[inquiry release];
	inquiry = nil;

	// and release the hold on ourselves in case the parent already released us while we were
	// still waiting for IOBluetoothDeviceInquiry results.
	[self release];

	return ret;
}

#pragma mark - IOBluetoothDeviceInquiry delegates

- (void) deviceInquiryComplete:(IOBluetoothDeviceInquiry*)sender error:(IOReturn)error aborted:(BOOL)aborted {
	//NSLog(@"deviceInquiryComplete error %i aborted %i", error, aborted);
	if (aborted) return; // called by stop ;)

	if (kIOReturnSuccess != error) {
		[self stop];
		LogIOReturn(error);
		[_delegate WiiRemoteDiscoveryError: error];
		return;
		// Damn, IOService:stringFromReturn is only available for kernel code. But what does my error 0xbc mean then?
		// There's no such code in IOError.h. Probably means that no devices at all were discovered.
		//NSLog(@"deviceInquiryComplete error %i", error);
	}

	// clear the list, or we wouldn't get any more deviceInquiryDeviceFound events.
	[inquiry clearFoundDevices];
	IOReturn ret = [inquiry start];

	if (ret != kIOReturnSuccess) {
		NSLog(@"deviceInquiryComplete Error: Restarting Inquiry failed. stopping discorey: %d", ret);
		[_delegate WiiRemoteDiscoveryError: ret];
		[self stop];
	}
}

// deviceInquiryDeviceFound - called right away if a device is found during device inquiry
// deviceInquiryDeviceNameUpdated - called for every found device, but at the end of device inquiry (10s after start).

// If the device inquiry updateNewDeviceNames is TRUE, then this delegate gets called every time the main
// scanning part of the device inquiry process is complete. This delegate is used as a fallback case if
// deviceInquiryDeviceFound returns a device that has no name yet. Happens (maybe) only if the computer sees
// the wiimote for the first time ever.
- (void) deviceInquiryDeviceNameUpdated:(IOBluetoothDeviceInquiry*)sender device:(IOBluetoothDevice*)device devicesRemaining:(int)devicesRemaining {
	NSLog(@"deviceInquiryDeviceNameUpdated devicesRemaining %i name %@", devicesRemaining, [device name]);
	if ([[device name] isEqualToString:@"Nintendo RVL-CNT-01"]) {
		// stop the discovery process.
		[self stop];
		[self m_connectWiimote: device];
	}
}

// This delegate gets called right away when a device is found. Except that if the device inquiry clearFoundDevices
// is not called before restarting the discovery process, then this delegate never gets called again and only the
// deviceInquiryDeviceNameUpdated gets called every time on device inquiry process timeout.
- (void) deviceInquiryDeviceFound:(IOBluetoothDeviceInquiry*)sender device:(IOBluetoothDevice*)device {
	NSLog(@"deviceInquiryDeviceFound %@", [device name]);
	if ([[device name] isEqualToString:@"Nintendo RVL-CNT-01"]) {
		// stop the discovery process.
		[self stop];
		[self m_connectWiimote: device];
	}
}

#pragma mark - private methods

- (void) m_connectWiimote:(IOBluetoothDevice*)device {
	//NSLog(@"connectWiimote nameOrAddress '%@' name '%@' lastup '%@'", [device nameOrAddress], [device name], [device getLastNameUpdate]);
	assert([[device name] isEqualToString:@"Nintendo RVL-CNT-01"]);

	WiiRemote* wii = [[WiiRemote alloc] init];
	IOReturn ret = [wii connectTo:device];

	if (ret == kIOReturnSuccess) {
		[_delegate WiiRemoteDiscovered: wii];
	} else {
		[wii release];
		LogIOReturn(ret);
		// discovery process is stopped at this point. you have to restart it manually.
		[_delegate WiiRemoteDiscoveryError: ret];
	}
}

@end
