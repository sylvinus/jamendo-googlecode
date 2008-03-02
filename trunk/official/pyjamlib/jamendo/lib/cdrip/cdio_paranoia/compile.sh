#/bin/sh

rm ../../../bin/cdio_paranoia.exe
rm ../../../bin/cygwin1.dll

gcc cdio_paranoia.c -o ../../../bin/cdio_paranoia.exe -I/usr/include -lcdio -lcdio_cdda -lcdio_paranoia --static -lm -lwinmm
#gcc cdio_paranoia.c -o ../../../bin/cdio_paranoia.exe -I/usr/include -lcdio -lcdio_cdda -lcdio_paranoia

cp /bin/cygwin1.dll ../../../bin/