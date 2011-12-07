#!/usr/bin/env python
import os

here = os.path.dirname(os.path.abspath(__file__))

bins = os.path.join(here, 'bin')

new_text = """#!/usr/bin/env python
# This implements something like virtualenv-style activation whenever
# you use the script:
import sys, os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Only do this if we're not in a virtualenv already
if not getattr(sys, 'real_prefix', None):
    prev_sys_path = list(sys.path)
    import site
    site.addsitedir(base)
    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    # Put our entries first
    sys.path[:0] = new_sys_path
"""

SKIP_NAMES = [
    'activate', 'activate.csh', 'activate.fish', 'activate_this.py',
    'python', 'python2.4', 'python2.5', 'python2.6', 'python2.7',
    'easy_install', 'pip']


def main():
    for name in sorted(os.listdir(bins)):
        if name in SKIP_NAMES or name.split('-')[0] in SKIP_NAMES:
            continue
        fn = os.path.join(bins, name)
        fp = open(fn)
        content = fp.read()
        fp.close()
        if not content.startswith('#!'):
            if not name.startswith('python'):
                print '%s: not a #! script' % name
            continue
        lines = content.splitlines(True)
        if lines[0].startswith('#!/usr/bin/env'):
            continue
        if 'python' not in lines[0]:
            print '%s: not a python script' % name
            continue
        good = None
        for i in range(len(lines)):
            if 'EASY-INSTALL-ENTRY-SCRIPT' in lines[i]:
                good = lines[i:]
                break
        else:
            print '%s: Not a Setuptools script' % name
            continue
        new_lines = [new_text] + good
        print '%s: updating' % name
        fp = open(fn, 'w')
        fp.writelines(new_lines)
        fp.close()

if __name__ == '__main__':
    main()
