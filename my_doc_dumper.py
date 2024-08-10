#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from msodumper import globals, docstream
import sys
import os
import xml.dom.minidom

if not globals.PY3:
    sys = reload(sys)
    sys.setdefaultencoding("utf-8")


class DOCDumper:
    def __init__(self, filepath, params):
        self.filepath = filepath
        self.params = params

    def dump(self):
        file = open(self.filepath, 'rb')
        strm = docstream.createDOCFile(file.read(), self.params)
        file.close()
        dirnames = strm.getDirectoryNames()
        print('<?xml version="1.0"?>\n<streams ole-type="%s">' % strm.getName())
        if strm.error:
            print('<error what="%s"/>' % strm.error)
        for dirname in dirnames:
            if len(dirname) == 0 or dirname in [b'Root Entry']:
                continue
            strm.getDirectoryStreamByName(dirname).dump()
        print('</streams>')

def traverse(node, callback):
    if node.nodeType == node.TEXT_NODE:
        pass
    else:
        callback(node)
        for child in node.childNodes:
            traverse(child, callback)

def remove_offsets(node):
    if node.nodeType == node.ELEMENT_NODE:
        if node.hasAttribute('offset'):
            node.removeAttribute('offset')

def main(args):

    orig_stdout = sys.stdout
    f = open(sys.argv[1] + '.xml', 'w', encoding='utf-8')
    sys.stdout = f

    params = globals.Params()
    dumper = DOCDumper(args[1], params)
    dumper.dump()

    sys.stdout = orig_stdout
    f.close()

    with open(sys.argv[1] + '.xml', 'r', encoding='utf-8') as f:
        # this is a xml file, so we can use the xml parser
        # to format the output
        doc = xml.dom.minidom.parse(f)
        # get the streams>stream[name="WordDocument"] element content
        wordDoc = doc.getElementsByTagName('stream')
        for stream in wordDoc:
            if stream.getAttribute('name') == 'WordDocument':
                # traverse the content of the WordDocument stream tree
                # remove all offset attributes
                traverse(stream, remove_offsets)
                # get the text of the content
                text = stream.toprettyxml()
                text = '\n'.join([s for s in text.splitlines() if s.strip()])
                # remove all offset attributes
                # write the content to the WordDocument.xml file
                with open(sys.argv[1] + '.WordDocument.xml', 'w', encoding='utf-8') as f:
                    f.write(text)

if __name__ == '__main__':
    main(sys.argv)




# vim:set filetype=python shiftwidth=4 softtabstop=4 expandtab:
