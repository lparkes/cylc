# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2017 NIWA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Module used for profiling different cylc versions."""

import os
import re
from subprocess import Popen, PIPE
import sys

from .git import is_git_repo


def get_cylc_directory():
    """Returns the location of cylc's working copy."""
    ver_str, _ = Popen(['cylc', 'version', '--long'], stdout=PIPE
                       ).communicate()
    try:
        return os.path.realpath(re.search('\((.*)\)', ver_str).groups()[0])
    except IndexError:
        sys.exit('Could not locate local git repository for cylc.')


# Ensure that the cylc directory is a git repository.
CYLC_DIR = get_cylc_directory()
os.chdir(CYLC_DIR)
if not is_git_repo():
    print 'ERROR: profiling requires cylc to be a git repository.'
    sys.exit(2)

# Files and directories
PROFILE_DIR_NAME = '.profiling'  # Path to profiling directory.
PROFILE_FILE_NAME = 'results.json'  # Path to profiling results file
PROFILE_PLOT_DIR_NAME = 'plots'  # Path to default plotting directory.
USER_EXPERIMENT_DIR_NAME = 'experiments'  # Path to user defined experiments.
EXPERIMENTS_PATH = os.path.join('dev', 'profile-experiments'
                                )  # Path to built-in experiments.

# Ancestor commit for cylc profile-battery
PROFILE_COMMIT = '0f5a7999ba9c93174d846a6679db4ce413388df7'

# Ancestor commit for analysis-compatible cylc (run|validate) --profile
CYLC_PROFILING_COMMIT = '016e6a97be16eaf1a33ea19398a1ade09f86719e'

# Profiling config.
PROFILE_MODE_TIME = 'PROFILE_MODE_TIME'
PROFILE_MODE_CYLC = 'PROFILE_MODE_CYLC'
PROFILE_MODES = {'time': PROFILE_MODE_TIME,
                 'cylc': PROFILE_MODE_CYLC}

# Profile file suffixes.
PROFILE_FILES = {
    'cmd-out': '',
    'cmd-err': '-cmd.err',
    'time-err': '-time.err',
    'startup': '-startup'
}


# ------------- REGEXES ---------------
# Cylc profiling REGEXES.
SUMMARY_LINE_REGEX = re.compile('([\d]+) function calls \(([\d]+) primitive'
                                ' calls\) in ([\d.]+) CPU seconds')
MEMORY_LINE_REGEX = re.compile('PROFILE: Memory: ([\d]+) KiB: ([\w.]+): (.*)')
LOOP_MEMORY_LINE_REGEX = re.compile('(?:loop #|end main loop \(total loops )'
                                    '([\d]+)(?:: |\): )(.*)')
SLEEP_FUNCTION_REGEX = re.compile('([\d.]+)[\s]+[\d.]+[\s]+\{time.sleep\}')
SUITE_STARTUP_STRING = 'SUITE STARTUP: '


# -------------- METRICS ---------------
METRIC_TITLE = 0  # For display purposes.
METRIC_UNIT = 1  # For display purposes.
METRIC_FILENAME = 2  # For output plots (no extension).
METRIC_FIELDS = 3  # Fields metrics can be derived from in order of preference.
METRICS = {
    '001': ('Elapsed Time', 's', 'elapsed-time', [
            'real', 'Elapsed (wall clock) time (h:mm:ss or m:ss)',
            'cpu time'],),
    '002': ('CPU Time - Total', 's', 'cpu-time', ['total cpu time'],),
    '003': ('CPU Time - User', 's', 'user-time', [
            'user', 'User time (seconds)'],),
    '004': ('CPU Time - System', 's', 'system-time', [
            'sys', 'System time (seconds)'],),
    '005': ('Max Memory', 'kb', 'memory', [
            'maximum resident set size', 'Maximum resident set size (kbytes)',
            'mxmem'],),
    '006': ('File System - Inputs', None, 'file-ins', [
            'block input operations', 'File system inputs'],),
    '007': ('File System - Outputs', None, 'file-outs', [
            'block output operations', 'File system outputs'],),
    '008': ('Startup Time', 's', 'startup-time', ['startup time'],),
    '009': ('Number Of Main Loop Iterations', None, 'loop-count', [
            'loop count'],),
    '010': ('Average Main Loop Iteration Time', 's', 'loop-time', [
            'avg loop time'],),
    '011': ('Elapsed Time - time.sleep()', 's', 'awake-time', [
            'awake cpu time'],)
}
METRICS_BY_FIELD = {}
for metric in METRICS:
    for field in METRICS[metric][METRIC_FIELDS]:
        METRICS_BY_FIELD[field] = metric
QUICK_ANALYSIS_METRICS = set(['001', '002', '005'])


DEFAULT_PROFILE_MODES = ['time']
