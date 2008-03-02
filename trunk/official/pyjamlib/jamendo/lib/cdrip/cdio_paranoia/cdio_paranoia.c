/*
 *  
 * 
 * 
 * 
 * 
 * 
 * 
 * 
 *
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <limits.h>
//#include <endian.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <sys/types.h>
#include <cdio/cdio.h>
#include <cdio/cd_types.h>
#include <cdio/cdda.h>
#include <cdio/paranoia.h>

#include "cdio_paranoia.h"

typedef unsigned short u_int16_t;

int mode;
long batch_first;
long batch_last;
int output_endian=0;
int sample_offset=0;
int offset_skip=0;

int main(int argc, char *argv[]) {
	if (argc < 3) {
		show_usage();
		exit(0);
	} else {

		/*int i;
		 for(i=1; i < argc; i++)
		 {
		 printf("%d -> %s\n", i, argv[i]);
		 }*/
		if ( !strcmp(argv[1], "--standalone") ) {
			mode = MODE_STANDALONE;
		} else if ( !strcmp(argv[1], "--embedded") ) {
			mode = MODE_EMBEDDED;
		} else {
			show_usage();
			exit(0);
		}

		if ( !strcmp(argv[2], "--test-presence") ) {
			test_presence(VERBOSE);
		} else if ( !strcmp(argv[2], "--count-tracks") ) {
			count_tracks(VERBOSE);
		} else if ( !strcmp(argv[2], "--extract-track") ) {
			if (argc < 5) {
				show_usage();
				exit(0);
			}
			char *endptr;
			errno = 0;
			int track_number = strtol(argv[3], &endptr, 10);

			if ((errno == ERANGE && (track_number == LONG_MAX || track_number
					== LONG_MIN)) || (errno != 0&& track_number == 0)) {
				show_usage();
				printf(" !!! track number is not a numerical value !!!\n\n");
				exit(0);
			} else if (track_number == 0) {
				show_usage();
				printf(" !!! track number is not a numerical value !!!\n\n");
				exit(0);
			} else {
				extract_track(track_number, (argv[4]));
			}
		} else {
			show_usage();
			exit(0);
		}

	}

	return 1;
}

static inline int bigendianp(void) {
	int test=1;
	char *hack=(char *)(&test);
	if (hack[0])
		return (0);
	return (1);
}

static inline int16_t swap16(int16_t x) {
	return ((((u_int16_t)x & 0x00ffU) << 8) |(((u_int16_t)x & 0xff00U) >> 8));
}

void show_usage() {
	printf("\n CDDA to WAV extraction tool developped for Jamloader3\n by Maxime Appolonia for Jamendo.com\n\n Command params are :\n  --standalone : program return human readable output to the command line\n  --embedded : return a computable output\n  --test-presence : return 1 if a CDDA is present, 0 if not\n  --count-tracks : return the number of tracks\n  --extract-track N FILE: extract cd audio track number N to destination wav file FILE ");
	printf("\n\n");
}

bool test_presence(int output) {
	if ( !mode==0&& output==VERBOSE) {
		printf("testing CDDA presence ... ");
	}
	CdIo_t *p_cdio = cdio_open (NULL, DRIVER_UNKNOWN);
	if (NULL == p_cdio) {
		if (output==VERBOSE) {
			if ( !mode==0) {
				printf("no cdrom drive found !\n\n");
			} else {
				printf("0");
			}
		}
		return false;
	} else {
		track_t first_track_num = cdio_get_first_track_num(p_cdio);
		track_t i_tracks = cdio_get_num_tracks(p_cdio);
		int num_audio = 0;

		int i;
		int first_audio = -1;
		for (i = first_track_num; i <= i_tracks; i++) {
			if (TRACK_FORMAT_AUDIO == cdio_get_track_format(p_cdio, i)) {
				num_audio++;
				if (-1 == first_audio)
					first_audio = i;
			}
		}
		if (num_audio == 0) {
			if (output==VERBOSE) {
				if ( !mode==0) {
					printf("No audio cd found !\n\n");
				} else {
					printf("0");
				}
			}
			return false;
		} else {
			if (output==VERBOSE) {
				if ( !mode==0) {
					printf("present\n\n");
				} else {
					printf("1");
				}
			}
			return true;
		}
	}

}

int count_tracks(int output) {
	bool present = test_presence(SILENT);
	if (present==0) {
		if (output=VERBOSE ) {
			printf("CDDA presence test failed !");
		} else {
			printf("0");
		}
		return 0;
	} else {
		if ( !mode==0&& output==VERBOSE) {
			printf("counting tracks ... ");
		}

		CdIo_t *p_cdio = cdio_open (NULL, DRIVER_UNKNOWN);
		track_t first_track_num = cdio_get_first_track_num(p_cdio);
		track_t i_tracks = cdio_get_num_tracks(p_cdio);
		int num_audio = 0;

		int i;
		int first_audio = -1;
		for (i = first_track_num; i <= i_tracks; i++) {
			if (TRACK_FORMAT_AUDIO == cdio_get_track_format(p_cdio, i)) {
				num_audio++;
				if (-1 == first_audio)
					first_audio = i;
			}
		}
		if (num_audio == 0) {
			if (output==VERBOSE) {
				if ( !mode==0) {
					printf("No audio cd found !\n\n");
				} else {
					printf("0");
				}
			}
			return 0;
		} else {
			if (output==VERBOSE) {
				if ( !mode==0) {
					printf("%d tracks\n\n", num_audio);
				} else {
					printf("%d", num_audio);
				}
			}
			return num_audio;
		}

	}
}

void extract_track(int track_num, char *output_file) {
	bool present = test_presence(SILENT);
	if (present==0) {
		if ( !mode==0) {
			printf("No audio cd found !\n\n");
		} else {
			printf("-1");
		}
		//return 0;
	} else {
		int tracks_count = count_tracks(SILENT);
		if (tracks_count>=track_num ) {
			// ADD CODE TO VERIFY THAT DESTINATION FILE DOES NOT EXIST OR IS WRITABLE
			int out=open(output_file, O_RDWR|O_CREAT|O_TRUNC, 0666);
			if (out==-1) {
				printf("Cannot open specified output file %s", output_file);
			}
			lsn_t lsn = get_first_lsn_for_track(track_num);
			safe_extract_track(track_num, out, lsn);
		} else {
			if ( !mode==0) {
				printf("The track you try to extract does not exists !\n\n");
			} else {
				printf("-1");
			}
			//return 0;
		}
	}

}

void safe_extract_track(int track_num, int out, lsn_t i_first_lsn) {
	if ( !mode==0) {
		printf("Extracting tracks %d ... \n", track_num);
	}

	cdrom_drive_t *d = NULL;
	char **ppsz_cd_drives;
	ppsz_cd_drives = cdio_get_devices_with_cap(NULL, CDIO_FS_AUDIO, false);
	d = cdio_cddap_identify(*ppsz_cd_drives, 1, NULL);
	cdio_free_device_list(ppsz_cd_drives);
	/* We'll set for verbose paranoia messages. */
	//cdio_cddap_verbose_set(d, CDDA_MESSAGE_PRINTIT, CDDA_MESSAGE_PRINTIT);
	cdio_cddap_open(d);

	{
		cdrom_paranoia_t *p = cdio_paranoia_init(d);
		//lsn_t i_first_lsn = cdio_cddap_disc_firstsector(d);
		if (-1 == i_first_lsn) {
			printf("Trouble getting starting LSN\n");
		} else {
			lsn_t i_cursor;
			track_t i_track = cdio_cddap_sector_gettrack(d, i_first_lsn);
			lsn_t i_last_lsn = cdio_cddap_track_lastsector(d, i_track);

			batch_last = i_last_lsn;
			batch_first = i_first_lsn;
			int	batch_count = i_last_lsn - i_first_lsn;
			

			WriteWav(out, (batch_last-batch_first+1)*CD_FRAMESIZE_RAW);


			printf("Reading track %d from LSN %ld to LSN %ld count is %ld\n", i_track,
					(long int) i_first_lsn, (long int) i_last_lsn, (long int) batch_count);

			/* Set reading mode for full paranoia, but allow skipping sectors. */
			paranoia_modeset(p, PARANOIA_MODE_FULL ^ PARANOIA_MODE_NEVERSKIP);

			paranoia_seek(p, i_first_lsn, SEEK_SET);

			int last_percent = 0;
			
			for (i_cursor = i_first_lsn; i_cursor <= i_last_lsn; i_cursor++) {
				/* read a sector */
				
				/* output percent processing */
				int batch_current = (i_cursor - batch_first);
				int batch_progress =  (batch_current * 100) / batch_count;
				
				//if(batch_progress > last_percent){
					last_percent = batch_progress;
					printf("%d\n", last_percent);
				//}
				
				int16_t *p_readbuf = cdio_paranoia_read(p, NULL);
				char *psz_err = cdio_cddap_errors(d);
				char *psz_mes = cdio_cddap_messages(d);

				if (psz_mes || psz_err)
					printf("%s%s\n", psz_mes ? psz_mes : "", psz_err ? psz_err
							: "");

				if (psz_err)
					free(psz_err);
				if (psz_mes)
					free(psz_mes);
				if (!p_readbuf) {
					printf("paranoia read error. Stopping.\n");
					break;
				}

				//write(out, p_readbuf, sizeof(int16_t));

				if (output_endian!=bigendianp()) {
					int i;
					for (i=0; i<CD_FRAMESIZE_RAW/2; i++)
						p_readbuf[i]=swap16(p_readbuf[i]);
				}

				//callback(cursor*(CD_FRAMEWORDS)-1,-2);
				//printf(".");

				if (buffering_write(out, ((char *)p_readbuf)+offset_skip,
						CD_FRAMESIZE_RAW-offset_skip)) {
					printf("Error writing output: %s", strerror(errno));
					exit(1);
				}
				offset_skip=0;

				if (output_endian!=bigendianp()) {
					int i;
					for (i=0; i<CD_FRAMESIZE_RAW/2; i++)
						p_readbuf[i]=swap16(p_readbuf[i]);
				}

				/*
				 // One last bit of silliness to deal with sample offsets 
				 if(sample_offset && i_cursor>batch_last){
				 int i;
				 // read a sector and output the partial offset.  Save the
				 //	rest for the next batch iteration 
				 p_readbuf=cdio_paranoia_read(p,NULL);
				 char *psz_err = cdio_cddap_errors(d);
				 char *psz_mes = cdio_cddap_messages(d);
				 
				 if (psz_mes || psz_err)
				 printf("%s%s\n", psz_mes ? psz_mes : "", psz_err ? psz_err : "");
				 
				 if (psz_err)
				 free(psz_err);
				 if (psz_mes)
				 free(psz_mes);
				 if (!p_readbuf) {
				 printf("paranoia read error. Stopping.\n");
				 break;
				 }
				 
				 //if(skipped_flag && abort_on_skip)break;
				 //skipped_flag=0;
				 // do not move the cursor 
				 
				 if(output_endian!=bigendianp())
				 for(i=0;i<CD_FRAMESIZE_RAW/2;i++)
				 offset_buffer[i]=swap16(p_readbuf[i]);
				 else
				 memcpy(offset_buffer,p_readbuf,CD_FRAMESIZE_RAW);
				 
				 offset_buffer_used=sample_offset*4;
				 
				 //callback(cursor*(CD_FRAMEWORDS),-2);
				 
				 if(buffering_write(out,(char *)offset_buffer, offset_buffer_used)){
				 //report2("Error writing output: %s",strerror(errno));
				 printf("error writing output");
				 exit(1);
				 }
				 }
				 */

			}
			//callback(cursor*(CD_FRAMESIZE_RAW/2)-1,-1);
			buffering_close(out);
		}
		cdio_paranoia_free(p);
	}

}

lsn_t get_first_lsn_for_track(int track_num) {
	CdIo_t *p_cdio = cdio_open(NULL, DRIVER_UNKNOWN);
	track_t i_first_track;
	track_t i_tracks;
	int j, i;
	lsn_t lsn;

	i_tracks = cdio_get_num_tracks(p_cdio);
	i_first_track = i = cdio_get_first_track_num(p_cdio);

	for (j = 0; j < i_tracks; i++, j++) {
		if ( (j+1) == track_num ) {
			lsn = cdio_get_track_lsn(p_cdio, i);
		}

	}
	cdio_destroy(p_cdio);
	return lsn;

}

static void PutNum(long num, int f, int endianness, int bytes) {
	int i;
	unsigned char c;

	if (!endianness)
		i=0;
	else
		i=bytes-1;
	while (bytes--) {
		c=(num>>(i<<3))&0xff;
		if (write(f, &c, 1)==-1) {
			perror("Could not write to output.");
			exit(1);
		}
		if (endianness)
			i--;
		else
			i++;
	}
}

void WriteWav(int f, long bytes) {
	/* quick and dirty */

	write(f, "RIFF", 4); /*  0-3 */
	PutNum(bytes+44-8, f, 0, 4); /*  4-7 */
	write(f, "WAVEfmt ", 8); /*  8-15 */
	PutNum(16, f, 0, 4); /* 16-19 */
	PutNum(1, f, 0, 2); /* 20-21 */
	PutNum(2, f, 0, 2); /* 22-23 */
	PutNum(44100, f, 0, 4); /* 24-27 */
	PutNum(44100*2*2, f, 0, 4); /* 28-31 */
	PutNum(4, f, 0, 2); /* 32-33 */
	PutNum(16, f, 0, 2); /* 34-35 */
	write(f, "data", 4); /* 36-39 */
	PutNum(bytes, f, 0, 4); /* 40-43 */
}

long blocking_write(int outf, char *buffer, long num) {
	long words=0, temp;

	while (words<num) {
		temp=write(outf, buffer+words, num-words);
		if (temp==-1) {
			if (errno!=EINTR && errno!=EAGAIN)
				return (-1);
			temp=0;
		}
		words+=temp;
	}
	return (0);
}

#define OUTBUFSZ 32*1024

/* GLOBALS FOR BUFFERING CALLS */
static int bw_fd = -1;
static long bw_pos = 0;
static char bw_outbuf[OUTBUFSZ];

/* buffering_write() - buffers data to a specified size before writing.
 *
 * Restrictions:
 * - MUST CALL BUFFERING_CLOSE() WHEN FINISHED!!!
 *
 */
long buffering_write(int fd, char *buffer, long num) {
	if (fd != bw_fd) {
		/* clean up after buffering for some other file */
		if (bw_fd >= 0&& bw_pos > 0) {
			if (blocking_write(bw_fd, bw_outbuf, bw_pos)) {
				perror("write (in buffering_write, flushing)");
			}
		}
		bw_fd = fd;
		bw_pos = 0;
	}

	if (bw_pos + num > OUTBUFSZ) {
		/* fill our buffer first, then write, then modify buffer and num */
		memcpy(&bw_outbuf[bw_pos], buffer, OUTBUFSZ - bw_pos);
		if (blocking_write(fd, bw_outbuf, OUTBUFSZ)) {
			perror("write (in buffering_write, full buffer)");
			return (-1);
		}
		num -= (OUTBUFSZ - bw_pos);
		buffer += (OUTBUFSZ - bw_pos);
		bw_pos = 0;
	}
	/* save data */
	memcpy(&bw_outbuf[bw_pos], buffer, num);
	bw_pos += num;

	return (0);
}

/* buffering_close() - writes out remaining buffered data before closing
 * file.
 *
 */
int buffering_close(int fd) {
	if (fd == bw_fd && bw_pos > 0) {
		/* write out remaining data and clean up */
		if (blocking_write(fd, bw_outbuf, bw_pos)) {
			perror("write (in buffering_close)");
		}
		bw_fd = -1;
		bw_pos = 0;
	}
	return (close(fd));
}
