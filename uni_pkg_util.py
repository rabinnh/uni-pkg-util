#!/usr/bin/env python3

"""
Copyright 2024 Richard Bross

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import sys
import subprocess
from columnar import columnar


# Create a class to search for available and installed packages
class UniPackage:
    def __init__(self):
        self.snapList = []
        self.aptList = []

    # Usage text
    def Usage(self):
        print('USAGE: uni_okg_util.py search|installed package_name')

    # Extract the package name and version
    def normalizeSnapSearch(self, raw, package):
        # Remove header
        del raw[0]
        for entry in raw:
            cols = entry.split()
            if len(cols) < 2:
                continue
            if package not in cols[0]:
                continue
            self.snapList.append([cols[0].strip(), cols[1].strip()])

    # For apt, it's a two step process
    def getAptVersion(self, raw, package):
        unique = set()
        for entry in raw:
            cols = entry.split('|')
            if package not in cols[0]:
                continue
            if f'{cols[0]}|{cols[1]}' not in unique:
                unique.add(f'{cols[0]}|{cols[1]}')
                self.aptList.append([cols[0].strip(), cols[1].strip()])

    # In this case, we use the specific package name to get the package version
    def normalizeAptSearch(self, raw, package):
        # Might be dupes in these
        for entry in raw:
            cols = entry.split()
            if len(cols) == 0:
                continue
            if package not in cols[0]:
                continue
            aptVersion = subprocess.check_output(['apt-cache', 'madison', cols[0]]).decode("utf-8").split('\n')
            self.getAptVersion(aptVersion, cols[0])

    # See which apps are installed
    def normalizeAptInstalled(self, raw, package):
        # Might be dupes in these
        unique = set()
        for entry in raw:
            cols = entry.split('=')
            if len(cols) < 2:
                continue
            if package not in cols[0]:
                continue
            if f'{cols[0]}|{cols[1]}' not in unique:
                unique.add(f'{cols[0]}|{cols[1]}')
                self.aptList.append([cols[0].strip(), cols[1].strip()])

    # Search for available packages
    def searchPackages(self, package):
        snapSearch = subprocess.check_output(['snap', 'find', package]).decode("utf-8").split('\n')
        aptSearch = subprocess.check_output(['apt-cache', 'search', package]).decode("utf-8").split('\n')
        self.normalizeSnapSearch(snapSearch, package)
        self.normalizeAptSearch(aptSearch, package)

    # Search for installed packages
    def installedPackages(self, package):
        snapSearch = subprocess.check_output(['snap', 'list', package]).decode("utf-8").split('\n')
        aptSearch = subprocess.check_output(['aptitude', '-q', '-F', '"%?p=%?V"', 'search', package]).decode("utf-8").split('\n')
        self.normalizeSnapSearch(snapSearch, package)
        self.normalizeAptInstalled(aptSearch, package)


if __name__ == '__main__':
    uniCommand = UniPackage()
    if len(sys.argv) != 3:
        uniCommand.Usage()
        exit(1)

    if sys.argv[1] != 'search' and sys.argv[1] != 'installed':
        uniCommand.Usage()
        exit(1)

    if sys.argv[1] == 'search':
        uniCommand.searchPackages(sys.argv[2])
        print('--- Available Snap Packages ---')
        headers = ['Package Name', 'Version']
        table = columnar(uniCommand.snapList, headers, no_borders=True)
        print(table)
        print('\n--- Available Repo Packages ---')
        table = columnar(uniCommand.aptList, headers, no_borders=True)
        print(table)

    if sys.argv[1] == 'installed':
        uniCommand.installedPackages(sys.argv[2])
        print('--- Installed Snap Packages ---')
        headers = ['Package Name', 'Version']
        table = columnar(uniCommand.snapList, headers, no_borders=True)
        print(table)
        print('\n--- Installed Repo Packages ---')
        table = columnar(uniCommand.aptList, headers, no_borders=True)
        print(table)
