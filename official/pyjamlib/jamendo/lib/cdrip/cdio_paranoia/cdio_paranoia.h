#include <unistd.h>
#include <cdio/cdio.h>

#define MODE_STANDALONE 1
#define MODE_EMBEDDED 0

#define VERBOSE 1
#define SILENT 0

#define CD_FRAMESIZE_RAW 2352

void show_usage();
bool test_presence(int output);
int count_tracks(int output);
void extract_track(int track_num, char *output_file);
void safe_extract_track(int track_num, int out, lsn_t lsn);
lsn_t get_first_lsn_for_track(int track_num);
extern void WriteWav(int f,long bytes);
extern long buffering_write(int outf, char *buffer, long num);
