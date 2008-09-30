#!/usr/bin/python

"""
Simple system monitor program.

It connects to the controller's "state" object via Pyro,
and displays its contents in a terminal.

See system_status.py for class documentation.

For color terminal ASCII escape codes, see
http://ascii-table.com/ansi-escape-sequences.php
"""

import os
import sys
import Pyro.core

from time import sleep
from string import ljust, rjust, split, upper, lower

class kit:
    def __init__( self, title ):
        self.pos = 1
        title = " " + title + " "
        self.title = title
        self.len = len( title )

    def boof( self ):
        a = b = '\033[1;31m'
        for i in range( 1, self.len - 1 ):
            if i == self.pos:
                a += 'o\033[0m'
                b += self.title[i] + '\033[0m'
            else:
                a += ' '
                b += self.title[i]

        if self.pos == self.len:
            self.pos = 1
        else:
            self.pos += 1

        return [a,b] 

title = kit( "EcoConnect System Monitor" )

while True:
    # the following "try" ... "except" block allows the system monitor
    # to keep trying if it can't find the pyro nameserver. This means
    # the the monitor doesn't die when the controller is killed and
    # restarted, but on the other hand bugs in the monitor aren't
    # distinguishable from no nameserver found... 
    # ... could be done better I suspect.

    try: 
    
        remote = Pyro.core.getProxyForURI("PYRONAME://" + "state" )

        while True:

            status = remote.get_status()

            max_name_len = 0
            max_state_len = 0
            max_total_len = 0
            max_prog_len = 0
            lines = {}

            for task_id in status.keys():
                [name, reftime] = split( task_id, "_" )
                [state, complete, total, latest ] = status[ task_id ]

                if len( name ) > max_name_len:
                    max_name_len = len( name )

                if len( total ) > max_total_len:
                    max_total_len = len( total )

                if int( total ) > max_prog_len:
                    max_prog_len = int( total )

                if len( state ) > max_state_len:
                    max_state_len = len( state )

            for task_id in status.keys():

                [name, reftime] = split( task_id, "_" )
                [state, complete, total, latest ] = status[ task_id ]

                prog = ""
                for k in range( 1, int(total) + 1):
                    if k <= int(complete):
                        prog += "|"
                    else:
                        prog += "-"

                prog = ljust( prog, max_prog_len + 1 )

                name = ljust( name, max_name_len + 1 )
                frac = rjust( complete + "/" + total, 2 * max_total_len + 1 )

                ctrl_end = "\033[0m"

                if state == "running":
                    state = ljust( state, max_state_len + 1 )
                    foo_start = "\033[1;37;44m"   # bold white on blue
                    bar_start = "\033[1;34m"  # bold blue
                    line = bar_start + "  " + ctrl_end + foo_start + name + ctrl_end + " " + bar_start + state + " " + frac + " " + prog + " " + latest + ctrl_end

                elif state == "waiting":
                    state = ljust( state, max_state_len + 1 )
                    foo_start = "\033[32m"        # green
                    line = foo_start + "  " + name + " " + state + " " + frac + " " + prog + " " + latest + ctrl_end

                elif state == "finishd":
                    state = ljust( state, max_state_len + 1 )
                    foo_start = "\033[0m"         # black
                    line = foo_start + "  " + name + " " + state + " " + frac + " " + prog + " " + latest + ctrl_end

                else:
                    line = "!ERROR!"

                if reftime in lines.keys(): 
                    lines[ reftime ].append( line )
                else:
                    lines[ reftime ] = [ line ]

            # sort reference times using int( string )
            reftimes = lines.keys()
            reftimes.sort( key = int )

            blit = title.boof()
            for rt in reftimes:
                blit.append( "\033[1;31m" + "__________" + "\033[0m" ) # red
                blit.append( "\033[1;31m" + rt + "\033[0m" )  # red

                for line in lines[rt]:
                    blit.append( line )

            os.system( "clear" )
            for line in blit:
                print line
            sleep(0.5)

    except:
        os.system( "clear" )
        for line in title.boof():
            print line
        print "Connection to nameserver failed ..."

    sleep( 0.5 )
