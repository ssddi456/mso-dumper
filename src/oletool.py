#!/usr/bin/env python2
########################################################################
#
#  Copyright (c) 2011 Noel Power
#  
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without
#  restriction, including without limitation the rights to use,
#  copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following
#  conditions:
#  
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#
########################################################################

import sys, os.path, optparse
sys.path.append(sys.path[0]+"/src")

import ole, globals, vbahelper

class DateTime:
    def __init__(self):
        self.day = 0
        self.month = 0 
        self.year = 0
        self.hour = 0
        self.second = 0

class DirNode:

    def __init__(self, entry, olecontainer):
        self.Nodes = []
        self.Entry = entry;
        self.HierachicalName = ''
        self.OleContainer = olecontainer
    def isStorage(self):
        return self.Entry.DirIDRoot > 0

    def getName(self):
        return self.Entry.Name

    def getHierarchicalName(self):
        return self.HierachicalName

    def getChildren(self):
        return self.Nodes  

    def getStream(self):
        return self.OleContainer.getStreamForEntry( self.Entry )

class OleContainer:

    def __init__(self,filePath, params ):
        self.filePath = filePath
        self.header = None
        self.rootNode = None
        self.params = params
        
    def __getModifiedTime(self, entry):
        # need parse/decode Entry.TimeModified
        # ( although the documentation indicates that it might not be
        # worth it 'cause they are not universally used
        modified  = DateTime
        modified.day = 0
        modified.month = 0 
        modified.year = 0
        modified.hour = 0
        modified.second = 0
        return modified

    def __parseFile (self):
        if self.rootNode == None:
            file = open(self.filePath, 'rb')
            self.chars = file.read()
            file.close()    
            self.header = ole.Header(self.chars, self.params)
            self.header.parse()
            self.obj = self.header.getDirectory()
            self.obj.parseDirEntries()
            count = 0
            self.rootNode = self.__buildTree( self.obj.entries )   

    def __addSiblings( self, entries, parent, child ):
        # add left siblings
        nextLeft = child.Entry.DirIDLeft
        if ( nextLeft > 0 ):
            newEntry = DirNode( entries[ nextLeft ], self )
#            newEntry.HierachicalName = parent.HierachicalName + globals.encodeName( newEntry.Entry.Name )
            newEntry.HierachicalName = parent.HierachicalName + newEntry.Entry.Name
            if  newEntry.Entry.DirIDRoot > 0:
                newEntry.HierachicalName = newEntry.HierachicalName + '/'

            self.__addSiblings( entries, parent, newEntry ) 
            parent.Nodes.insert( 0, newEntry )

        nextRight = child.Entry.DirIDRight
        # add children to the right 
        if ( nextRight > 0 ):
            newEntry = DirNode( entries[ nextRight ], self )
#            newEntry.HierachicalName = parent.HierachicalName + globals.encodeName( newEntry.Entry.Name )
            newEntry.HierachicalName = parent.HierachicalName + newEntry.Entry.Name
            if  newEntry.Entry.DirIDRoot > 0:
                newEntry.HierachicalName = newEntry.HierachicalName + '/'
            self.__addSiblings( entries, parent, newEntry ) 
            parent.Nodes.append( newEntry )

    def __buildTreeImpl(self, entries, parent ):

        if ( parent.Entry.DirIDRoot > 0 ):
            newEntry = DirNode( entries[ parent.Entry.DirIDRoot ], self )
#            newEntry.HierachicalName = parent.HierachicalName + globals.encodeName( newEntry.Entry.Name )
            newEntry.HierachicalName = parent.HierachicalName +  newEntry.Entry.Name
            if ( newEntry.Entry.DirIDRoot > 0 ):
                newEntry.HierachicalName =  newEntry.HierachicalName + '/'

            self.__addSiblings( entries, parent, newEntry )
            parent.Nodes.append( newEntry )
            
        for child in parent.Nodes:
            if child.Entry.DirIDRoot > 0:
                self.__buildTreeImpl( entries, child )

    def __buildTree(self, entries ):
        treeRoot = DirNode( entries[0], self ) 
        self.__buildTreeImpl( entries, treeRoot )
        return treeRoot

    def __findEntryByHierachicalName( self, node, name ):
        if node.HierachicalName == name:
            return node.Entry
        else:
            for child in node.Nodes:
                result = self.__findEntryByHierachicalName( child, name )
                if result != None:
                    return result 
        return None 

    def __printListReport( self, treeNode ):

        dateInfo = self.__getModifiedTime( treeNode.Entry )

        if len( treeNode.HierachicalName ) > 0 :
            print '{0:8d}  {1:0<2d}-{2:0<2d}-{3:0<2d} {4:0<2d}:{5:0<2d}   {6}'.format(treeNode.Entry.StreamSize, dateInfo.day, dateInfo.month, dateInfo.year, dateInfo.hour, dateInfo.second, treeNode.HierachicalName )
     
        for node in treeNode.Nodes:
            # ignore the root
            self.__printListReport( node )

    def __printHeader(self):
        print ("OLE: %s")%self.filePath
        print (" Length     Date   Time    Name")
        print ("--------    ----   ----    ----")

    def list(self):
        # need to share the inititialisation and parse stuff between the different options
       
        self.__parseFile()
        if  self.rootNode != None:
            self.__printHeader()
            self.__printListReport( self.rootNode )
            # need to print a footer ( total bytes, total files like unzip )

    def getStreamForEntry( self, entry ):
        if  entry == None or entry.DirIDRoot > 0 :
            raise Exception("can't get stream for invalid entry")
        bytes = bytearray()
        bytes = self.obj.getRawStream( entry )
        bytes = bytes[0:entry.StreamSize]
        return bytes

    def getStreamForName( self, name ):
        self.__parseFile()
        if  self.rootNode != None:
            entry = self.__findEntryByHierachicalName( self.rootNode, name )
            return self.getStreamForEntry( entry )

    def extract(self, name):
        self.__parseFile()
        if  self.rootNode != None:
            entry = self.__findEntryByHierachicalName( self.rootNode, name )
            bytes = self.getStreamForEntry( entry )
            file = open(entry.Name, 'wb') 
            file.write( bytes )
            file.close
        else:
            print("failed to initialise ole container")

    def read(self):
        self.__parseFile()

    def getRoot(self):
        self.__parseFile()
        return self.rootNode 

# alot of records done follow the id, sizeofrecord pattern
# many of the dir records seems to be id, sizeofstring, stringbuffer, reserved,
#   sizeofstring(unicode), stringbuffer(unicode)
class DefaultBuffReservedBuffReader:
    def __init__ (self, reader, recname ):
        self.reader = reader
        self.recname = recname
    def parse(self):
        # pos before header
        pos = self.reader.getCurrentPos() - 2        
        print ("0x%x: skipping %s"%(pos,self.recname))
        # buffer
        size = self.reader.readUnsignedInt( 4 )
        self.reader.readBytes(size)        
        # reserved
        self.reader.readBytes(2)        
        # buffer
        size = self.reader.readUnsignedInt( 4 )
        self.reader.readBytes(size)    

class DocStringReader( DefaultBuffReservedBuffReader ):
    def __init__ (self, reader ):
        DefaultBuffReservedBuffReader.__init__(self, reader, "PROJECTDOCSTRING")

class HelpFilePathReader( DefaultBuffReservedBuffReader ):
    def __init__ (self, reader ):
        DefaultBuffReservedBuffReader.__init__(self, reader, "PROJECTHELPFILEPATH" )

class ProjectConstantsReader( DefaultBuffReservedBuffReader ):
    def __init__ (self, reader ):
        DefaultBuffReservedBuffReader.__init__(self, reader, "PROJECTCONSTANTS" )

class ReferenceNameReader( DefaultBuffReservedBuffReader ):
    def __init__ (self, reader ):
        DefaultBuffReservedBuffReader.__init__(self, reader, "REFERENCENAMEREADER" )

class ModuleStreamNameReader( DefaultBuffReservedBuffReader ):
    def __init__ (self, reader ):
        DefaultBuffReservedBuffReader.__init__(self, reader, "MODULESTREAMNAME" )

class ModuleDocStringReader( DefaultBuffReservedBuffReader ):
    def __init__ (self, reader ):
        DefaultBuffReservedBuffReader.__init__(self, reader, "MODULEDOCSTRING" )

class ProjectVersionReader:
    def __init__ (self, reader ):
        self.reader = reader
    def parse(self):
        # pos before header
        pos = self.reader.getCurrentPos() - 2        
        print ("0x%x: skipping %s"%(pos,"PROJECTVERSION"))
        self.reader.readBytes(10)

# map of record id and description of records
#dir stream contains
dirRecordData = {
    #PROJECTINFORMATION RECORD
    #  which contains any of the following sub records
    0x0001: ["PROJECTSYSKIND", "SysKindRecord"],
    0x0002: ["PROJECTLCID", "LcidRecord"],
    0x0003: ["PROJECTCODEPAGE", "CodePageRecord"],
    0x0004: ["PROJECTNAME", "NameRecord"],
    0x0005: ["PROJECTDOCSTRING", "DocStringRecord", DocStringReader ],
    0x0006: ["PROJECTHELPFILEPATH", "HelpFilePathRecord", HelpFilePathReader],
    0x0007: ["PROJECTHELPCONTEXT", "HelpContextRecord"],
    0x0008: ["PROJECTLIBFLAGS", "LibFlagsRecord"],
    0x0009: ["PROJECTVERSION", "VersionRecord", ProjectVersionReader],
    0x0010: ["DIRTERMINATOR", "DirTerminator"],
    0x000C: ["PROJECTCONSTANTS", "ConstantsRecord", ProjectConstantsReader],
    0x0014: ["PROJECTLCIDINVOKE", "LcidInvokeRecord"],
    #PROJECTREFERENCES
    # which contains any of the following sub records
    0x0016: ["REFERENCENAME", "NameRecord", ReferenceNameReader ],
    0x000D: ["REFERENCEREGISTERED", "ReferenceRegistered"],
    0x000E: ["REFERENCEPROJECT", "ReferenceProject"],
    0x002F: ["REFERENCECONTROL", "ReferenceControl"],
    0x0033: ["REFERENCEORIGINAL", "ReferenceOriginal"],
    #
    0x000F: ["PROJECTMODULES", "ModulesRecord"],
    0x0013: ["PROJECTCOOKIE", "CookieRecord"],
    0x002B: ["PROJECTMODULETERM", "ModuleTerminator"],
    0x0019: ["MODULENAME", "ModuleName"],
    0x0047: ["MODULENAMEUNICODE", "ModuleNameUnicode"],
    0x001A: ["MODULESTREAMNAME", "ModuleStreamName", ModuleStreamNameReader],
    0x001C: ["MODULEDOCSTRING", "ModuleDocString", ModuleDocStringReader],
    0x0031: ["MODULEOFFSET", "ModuleOffSet"],
    0x001E: ["MODULEHELPCONTEXT", "ModuleHelpContext"],
    0x002C: ["MODULECOOKIE", "ModuleCookie"],
    0x0021: ["MODULETYPE", "ModuleTypeProcedural"],
    0x0022: ["MODULETYPE", "ModuleTypeDocClassOrDesgn"],
    0x0025: ["MODULEREADONLY", "ModuleReadOnly"],
    0x0028: ["MODULEPRIVATE", "ModulePrivate"],
}    

    
        
class DirStreamReader( globals.ByteStream ): 
    def __init__ (self, bytes ):
        globals.ByteStream.__init__(self, bytes)

    def parse(self):
        print("============ Dir Stream ============")
        while self.isEndOfRecord() == False:
            pos = self.getCurrentPos()
            recordID = self.readUnsignedInt( 2 )
            name = "Unknown"
            if dirRecordData.has_key( recordID ):
                name = dirRecordData[ recordID ][0]
            # if we have a handler let it deal with the record
            if ( dirRecordData.has_key( recordID ) and len( dirRecordData[ recordID ] ) > 2 ):
                reader =  dirRecordData[ recordID ][2]( self )
                reader.parse()
            else:
                size = self.readUnsignedInt( 4 )
                print ("0x%x: %s [0x%x] with size %i"%(pos,name,recordID,size))
                if size:
                    self.readBytes(size)        

class VBAContainer:
    def __init__( self, vbaroot ):
        self.vbaroot = vbaroot

    def __findNodeByHierarchicalName( self, node, name ):
        if node.getHierarchicalName() == name:
            return node
        else:
            for child in node.getChildren():
                result = self.__findNodeByHierarchicalName( child, name )
                if result != None:
                    return result 
        return None 


    def dump( self ):
        # dump the PROJECTxxx streams
        for child in self.vbaroot.getChildren():
            # first level children are PROJECT, PROJECTwm & PROJECTlk
            if child.isStorage() == False:
                bytes = child.getStream()
                print("%s (stream, size: %d bytes)"%(child.getName(), len(bytes)))
                globals.dumpBytes( bytes, 512) 
        # need to read the dir stream
        dirName = self.vbaroot.getHierarchicalName() + "VBA/dir"
        dirNode = self.__findNodeByHierarchicalName( self.vbaroot, dirName )
        if dirNode != None:
            #decompress 
            bytes = dirNode.getStream()
            compressed = vbahelper.CompressedVBAStream( bytes, 0 )
            bytes = compressed.decompress()
            reader = DirStreamReader( bytes )
            reader.parse()
            

def main ():
    parser = optparse.OptionParser()
    parser.add_option("-l", "--list", action="store_true", dest="list", default=False, help="lists ole contents")
    parser.add_option("-x", "--extract", action="store_true", dest="extract", default=False, help="extract file")
    parser.add_option("-b", "--basic", action="store_true", dest="dumpbasic", default=False, help="dump basic related info")


    options, args = parser.parse_args()

    params = globals.Params()

    params.list =  options.list
    params.extract =  options.extract
    params.dumpbasic =  options.dumpbasic

    if len(args) < 1:
        globals.error("takes at least one arguments\n")
        parser.print_help()
        sys.exit(1)

    container =  OleContainer( args[ 0 ], params )

    if params.list == True:
        container.list() 
    if params.extract:
       files = args
       files.pop(0)
           
       for file in files:
           container.extract( file ) 
#        container.listEntries() 
    if params.dumpbasic:
        print("dump basic related info!") 
        container.read()
        root = container.getRoot()
        # find basic container
        for child in root.getChildren():
            # "Macros" is the 'word' VBA container, 
            # "_VBA_PROJECT_CUR" is the 'excel" VBA container
            if child.getName() == "_VBA_PROJECT_CUR" or child.getName() == "Macros":
             
                print("vba root storage  %s"%child.getName())
                vba = VBAContainer( child ) 
                vba.dump()

if __name__ == '__main__':
    main()
