/**

Detect an audio CD insertion on Mac OS X.

Original code from JamloaderMac by Martin Ottenwaelter.

Pasted to a standalone command by Sylvain Zimmer.



**/


#import <Foundation/Foundation.h>
#include <CoreFoundation/CoreFoundation.h>
#include <Carbon/Carbon.h>
#include <IOKit/storage/IOCDTypes.h>
#include <string.h>
#include <stdio.h>
#include <AppKit/NSWorkspace.h>
#include <AppKit/NSApplication.h>
#import <objc/Object.h>






// Constants
#define kAudioCDFilesystemID		(UInt16)(('J' << 8) | 'H' ) // 'JH'; this avoids compiler warning

int detectAudioCD(CFStringRef *outDisplayName) {
	
    OSErr		result = noErr;
	ItemCount	volumeIndex;
    
    // Enumerate all of the mounted volumes on the system looking for audio CDs.
	
	for (volumeIndex = 1; result == noErr || result != nsvErr; volumeIndex++) {
        FSVolumeRefNum	actualVolume;
        HFSUniStr255	volumeName;
        FSVolumeInfo	volumeInfo;
		FSRef			rootDirectory;
		
        bzero((void *) &volumeInfo, sizeof(volumeInfo));
        
        // Get the volume info, which includes the filesystem ID.
		result = FSGetVolumeInfo(kFSInvalidVolumeRefNum,
                                 volumeIndex,
                                 &actualVolume,
                                 kFSVolInfoFSInfo,
                                 &volumeInfo,
                                 &volumeName,
                                 &rootDirectory);
		
		if (result == noErr) {
            // Work around a bug in Mac OS X 10.0.x where the filesystem ID and signature bytes were
            // erroneously swapped. This was fixed in Mac OS X 10.1 (r. 2653443), broken again in Jaguar (r. 3015107),
			// and finally fixed in 10.2.3.
			//
			// This is the same workaround used by iTunes, so if iTunes thinks a disc is an audio CD,
			// so should this sample.
			if (volumeInfo.signature == kAudioCDFilesystemID || volumeInfo.filesystemID == kAudioCDFilesystemID) {
				LSCopyDisplayNameForRef(&rootDirectory,outDisplayName);
				return 1;
            }
        }
    }
	return 0;
}


@interface CdDetector : Object
 - (void) volumeMounted: (NSNotification*) notification;
 - (void) volumeUnmounted: (NSNotification*) notification;
@end


@implementation CdDetector
 
 - (void)volumeMounted: (NSNotification*) notification {
	
	
	CFStringRef outDisplayName;
	char filename[256];
	
	
	// Detect Audio CD and get its volume ref
	if (detectAudioCD(&outDisplayName) == 1) {
	
		CFStringGetCString(outDisplayName, filename, 256, kCFStringEncodingUTF8);
		
		printf("mounted:%s\n",filename);
		fflush( stdout );
	}
	
}
	

 - (void)volumeUnmounted: (NSNotification*) notification {
	
	printf("unmounted:\n");
	fflush( stdout );

	
	
	
}

@end


int main (int argc, const char * argv[]) {
    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];

	printf("start: CD Detection started...\n");
	fflush( stdout );
	

	
    
    CdDetector *cd_detect = [CdDetector new];
    
    
    if (!strcmp(argv[1],"--oneshot")) {
    
    	// Let's see if there is already an audio CD at startup
		[cd_detect volumeMounted:nil];
    
    } else if (!strcmp(argv[1],"--daemon")) {
	    
	    // Register to the "volume mounted" notification in order to handle inserted audio CDs
		[[[NSWorkspace sharedWorkspace] notificationCenter] addObserver:cd_detect
															   selector:@selector(volumeMounted:)
																   name:@"NSWorkspaceDidMountNotification"
																 object:nil];
	
	    // Register to the "volume unmounted" notification in order to handle ejected audio CDs
		[[[NSWorkspace sharedWorkspace] notificationCenter] addObserver:cd_detect
															   selector:@selector(volumeUnmounted:)
																   name:@"NSWorkspaceDidUnmountNotification"
																 object:nil];
	
		
		// Let's see if there is already an audio CD at startup
		[cd_detect volumeMounted:nil];
	
	
		[NSApplication sharedApplication];
		
		[NSApp run];
		
	}
	
    [pool release];
    return 0;
}

