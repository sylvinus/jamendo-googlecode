"""
Portable vaguely pexpect-like module.
Not seeking feature-completeness nor full compatibility.
Do not use for passwords (it's not a tty).
"""

import os
import re
import subprocess
import threading
import time

if os.name == 'nt':
    import win32api
elif os.name == 'posix':
    import signal

class EOF(Exception):
    pass

class TIMEOUT(Exception):
    pass

class _nonblocking_reader(threading.Thread):
    # TODO: limit buffer size ? maxsize currently unused
    def __init__(self, infile, maxsize=200):
        threading.Thread.__init__(self)
        self.cond = threading.Condition()

        self.maxsize = maxsize
        self.infile = infile
        self.setDaemon(True)

        # locked data
        self.dead = False
        self.buffer = ''
        self.char_array=[]
        # locked data


    def _get_buffer(self):
        """Merge recent chars into the buffer. (Less inefficient
        if done several at a time.)
        
        Please call only after having acquired the lock."""

        if self.char_array:
            self.buffer += ''.join(self.char_array)
            self.char_array = []
        buffer = self.buffer
        return buffer

    def run(self):
        alive = True
        while alive:
            # potentially blocking read
            c = self.infile.read(1)
            self.cond.acquire()
            if c:
                if c == '\n':
                    self.char_array.append('\r\n')
                else:
                    self.char_array.append(c)
            else:
                # c == '' on EOF, stop reading
                self.dead = True
            self.cond.notify()
            alive = not self.dead
            self.cond.release()


    def match_regexps(self, cres, timeout=30):
        """Find the first match for the buffer from a list of
        compiled regexps."""

        end_time = time.time() + timeout
        self.cond.acquire()
        idx = -1
        while idx == -1:
            start_time = time.time()
            if start_time > end_time:
                self.cond.release()
                raise TIMEOUT()

            self._get_buffer()
            for cre_num, cre in enumerate(cres):
                match = cre.search(self.buffer)
                if match is None:
                    continue
                # find match closest to the beginning
                if idx > match.start() or idx == -1:
                    selected_cre = cre_num
                    self.match = match
                    idx = match.start()
                    
            if idx == -1:
                if self.dead:
                    self.cond.release()
                    raise EOF()
                self.cond.wait(end_time-start_time)
                
        end = self.match.end()
        self.before = self.buffer[:idx]
        self.buffer = self.buffer[end:]
        self.after = self.buffer
        
        self.cond.release()
        return selected_cre


class spawn(object):
    """See pexpect. Limited functionality."""
    def __init__(self, command):
        
        self.sub = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._reader = _nonblocking_reader(self.sub.stdout)
        self._reader.start()

    def send(self, s):
        self.sub.stdin.write(s)
    
    def sendline(self, s):
        self.send(s + '\n')

    def terminate(self, force=False):
        self.sub.stdin.close()
        for i in range(500):
            time.sleep(0.01)
            r = self.sub.poll()
            if r is not None:
                break
        if r is None:
            # closing input stream was not enough
            if os.name == 'nt':
                PROCESS_TERMINATE = 1
                handle = win32api.OpenProcess(PROCESS_TERMINATE, False, self.sub.pid)
                win32api.TerminateProcess(handle, -1)
                win32api.CloseHandle(handle)
            elif os.name == 'posix':
                # send SIGTERM if survived closing of input
                os.kill(self.sub.pid, signal.SIGTERM)
                for i in range(500):
                    time.sleep(0.01)
                    r = self.sub.poll()
                    if r is not None:
                        break
                if r is None:
                    # send SIGKILL if survived SIGTERM
                    os.kill(self.sub.pid, signal.SIGKILL)

    def expect(self, patterns, timeout=30):
        compiled_patterns = [re.compile(pat) for pat in patterns]
        return self._reader.match_regexps(compiled_patterns, timeout)

    def _get_before(self):
        return self._reader.before
    def _get_after(self):
        return self._reader.after
    def _get_match(self):
        return self._reader.match
    before = property(_get_before, None)
    after  = property(_get_after, None)
    match  = property(_get_match, None)


""" from pexpect """
def split_command_line(command_line):
    """This splits a command line into a list of arguments.
    It splits arguments on spaces, but handles
    embedded quotes, doublequotes, and escaped characters.
    It's impossible to do this with a regular expression, so
    I wrote a little state machine to parse the command line.
    """
    arg_list = []
    arg = ''

    # Constants to name the states we can be in.
    state_basic = 0
    state_esc = 1
    state_singlequote = 2
    state_doublequote = 3
    state_whitespace = 4 # The state of consuming whitespace between commands.
    state = state_basic

    for c in command_line:
        if state == state_basic or state == state_whitespace:
            if c == '\\': # Escape the next character
                state = state_esc
            elif c == r"'": # Handle single quote
                state = state_singlequote
            elif c == r'"': # Handle double quote
                state = state_doublequote
            elif c.isspace():
                # Add arg to arg_list if we aren't in the middle of whitespace.
                if state == state_whitespace:
                    None # Do nothing.
                else:
                    arg_list.append(arg)
                    arg = ''
                    state = state_whitespace
            else:
                arg = arg + c
                state = state_basic
        elif state == state_esc:
            arg = arg + c
            state = state_basic
        elif state == state_singlequote:
            if c == r"'":
                state = state_basic
            else:
                arg = arg + c
        elif state == state_doublequote:
            if c == r'"':
                state = state_basic
            else:
                arg = arg + c

    if arg != '':
        arg_list.append(arg)
    return arg_list
