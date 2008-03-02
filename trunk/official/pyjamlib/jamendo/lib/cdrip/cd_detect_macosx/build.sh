#!/bin/sh
gcc -arch i386 -arch ppc -O3  -framework AppKit -framework Foundation -framework CoreFoundation -framework IOKit -framework Carbon main.m -o ../../../bin/cd_detect_macosx -lobjc
