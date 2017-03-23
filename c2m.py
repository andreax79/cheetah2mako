#!/usr/bin/env python
#
# MIT License
#
# Copyright (c) 2017 Andrea Bonomi <andrea.bonomi@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import os
import sys

VAR_RE = re.compile('\\$(\\w+)')
DEF_RE = re.compile('.*"(\w+)')

def pass1(lines):
    result = []
    defs = []
    for line in lines:
        # if and friends
        if '#if' in line:
            line = line.rstrip().replace('#if', '% if')
            line = line.replace('$', '')
            if not line.endswith(':'):
                line = line + ':'

        elif '#elif' in line:
            line = line.rstrip().replace('#elif', '% elif')
            line = line.replace('$', '')
            if not line.endswith(':'):
                line = line + ':'

        elif '#else if' in line:
            line = line.rstrip().replace('#elif', '% elif')
            line = line.replace('$', '')
            if not line.endswith(':'):
                line = line + ':'

        elif '#else' in line:
            line = line.rstrip().replace('#else', '% else')
            if not line.endswith(':'):
                line = line + ':'

        elif '#end if' in line:
            line = line.rstrip().replace('#end if', '% endif')

        # slurp
        if '#slurp' in line:
            line = line.strip()
            line = line.replace('#slurp', '\\')

        # comments
        line = line.replace('#*', '<%doc>\\')
        line = line.replace('*#', '</%doc>\\')

        # def
        if '#def ' in line:
            line = line.strip().replace('#def ', '<%def name="')
            if not line.endswith(')'):
                line = line + '()'
            line = line + '">\\'
            match = DEF_RE.match(line)
            if match is not None:
                defs.append(match.group(1))

        if '#end def' in line:
            line = line.strip().replace('#end def', '</%def>\\')

        # variables
        line = VAR_RE.sub('${\\1}', line)
        result.append(line)
    return result, defs

def pass2(lines, defs):
    result = []
    for line in lines:
        for def_ in defs:
            line = line.replace('${' + def_ + '}', '${' + def_ + '()}')
        result.append(line)
    return result

def c2m(filename):
    with open(filename, 'r') as f:
        lines = f.read().split('\n')
        lines, defs = pass1(lines)
        lines = pass2(lines, defs)
        return '\n'.join(lines)

def main():
    for filename in sys.argv[1:]:
        target = os.path.splitext(filename)[0] + '.mak'
        result = c2m(filename)
        with open(target, 'w') as f:
            f.write(result)

if __name__ == "__main__":
    main()

