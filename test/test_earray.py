# Eh! python!, We are going to include isolatin characters here
# -*- coding: latin-1 -*-

import sys
import unittest
import os
import tempfile

from numarray import *
from numarray import strings
from tables import *

try:
    import Numeric
    numeric = 1
except:
    numeric = 0

from test_all import verbose, allequal

class BasicTestCase(unittest.TestCase):
    # Default values
    flavor = "numarray"
    type = Int32
    shape = (2,0)
    start = 0
    stop = 10
    step = 1
    length = 1
    chunksize = 5
    nappends = 10
    compress = 0
    complib = "zlib"  # Default compression library
    shuffle = 0
    fletcher32 = 0
    reopen = 1  # Tells whether the file has to be reopened on each test or not

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")
        self.rootgroup = self.fileh.root
        self.populateFile()
        if self.reopen:
            # Close the file
            self.fileh.close()
        
    def populateFile(self):
        group = self.rootgroup
        if self.flavor == "numarray":
            if str(self.type) == "CharType":
                object = strings.array(None, itemsize=self.length,
                                       shape=self.shape)
            else:
                object = zeros(type=self.type, shape=self.shape)
        else:
                object = Numeric.zeros(typecode=typecode[self.type],
                                       shape=self.shape)
        title = self.__class__.__name__
        earray = self.fileh.createEArray(group, 'earray1', object, title,
                                         compress = self.compress,
                                         complib = self.complib,
                                         shuffle = self.shuffle,
                                         fletcher32 = self.fletcher32,
                                         expectedrows = 1)

        # Fill it with rows
        self.rowshape = list(earray.shape)
        self.objsize = self.length
        for i in self.rowshape:
            if i <> 0:
                self.objsize *= i
        self.extdim = earray.extdim
        self.objsize *= self.chunksize
        self.rowshape[earray.extdim] = self.chunksize
        if self.flavor == "numarray":
            if str(self.type) == "CharType":
                object = strings.array("a"*self.objsize, shape=self.rowshape,
                                       itemsize=earray.itemsize)
            else:
                object = arange(self.objsize, shape=self.rowshape,
                                type=earray.type)
        else:  # Numeric flavor
            object = Numeric.arange(self.objsize,
                                    typecode=typecode[earray.type])
            object = Numeric.reshape(object, self.rowshape)
        if verbose:
            if self.flavor == "numarray":
                print "Object to append -->", object.info()
            else:
                print "Object to append -->", repr(object)
        for i in range(self.nappends):
            if str(self.type) == "CharType":
                earray.append(object)
            elif self.flavor == "numarray":
                earray.append(object*i)
            else:
                object = object * i
                # For Numeric arrays, we still have to undo the type upgrade
                earray.append(object.astype(typecode[earray.type]))

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        
    #----------------------------------------

    def test01_iterEArray(self):
        """Checking enlargeable array iterator"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_iterEArray..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        if self.reopen:
            self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "EArray descr:", repr(earray)
            print "shape of read array ==>", earray.shape
            print "reopening?:", self.reopen
            
        # Build the array to do comparisons
        if self.flavor == "numarray":
            if str(self.type) == "CharType":
                object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                        itemsize=earray.itemsize)
            else:
                object_ = arange(self.objsize, shape=self.rowshape,
                                 type=earray.type)
            object_.swapaxes(earray.extdim, 0)
        else:
            object_ = Numeric.arange(self.objsize,
                                     typecode=typecode[earray.type])
            object_ = Numeric.reshape(object_, self.rowshape)
            object_ = Numeric.swapaxes(object_, earray.extdim, 0)
            
        # Read all the array
        for row in earray:
            chunk = int(earray.nrow % self.chunksize)
            if chunk == 0:
                if str(self.type) == "CharType":
                    object__ = object_
                else:
                    object__ = object_ * (earray.nrow / self.chunksize)
                    if self.flavor == "Numeric":
                        object__ = object__.astype(typecode[earray.type])
            object = object__[chunk]
            # The next adds much more verbosity
            if verbose and 0:
                print "number of row ==>", earray.nrow
                if hasattr(object, "shape"):
                    print "shape should look as:", object.shape
                print "row in earray ==>", repr(row)
                print "Should look like ==>", repr(object)

            assert self.nappends*self.chunksize == earray.nrows
            assert allequal(row, object, self.flavor)
            if hasattr(row, "shape"):
                assert len(row.shape) == len(self.shape) - 1
            else:
                # Scalar case
                assert len(self.shape) == 1

    def test02_sssEArray(self):
        """Checking enlargeable array iterator with (start, stop, step)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_sssEArray..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        if self.reopen:
            self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "EArray descr:", repr(earray)
            print "shape of read array ==>", earray.shape
            print "reopening?:", self.reopen
            
        # Build the array to do comparisons
        if self.flavor == "numarray":
            if str(self.type) == "CharType":
                object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                        itemsize=earray.itemsize)
            else:
                object_ = arange(self.objsize, shape=self.rowshape,
                                 type=earray.type)
            object_.swapaxes(earray.extdim, 0)
        else:
            object_ = Numeric.arange(self.objsize,
                                     typecode=typecode[earray.type])
            object_ = Numeric.reshape(object_, self.rowshape)
            object_ = Numeric.swapaxes(object_, earray.extdim, 0)
            
        # Read all the array
        for row in earray(start=self.start, stop=self.stop, step=self.step):
            if self.chunksize == 1:
                index = 0
            else:
                index = int(earray.nrow % self.chunksize)
            if str(self.type) == "CharType":
                object__ = object_
            else:
                object__ = object_ * (earray.nrow / self.chunksize)
                if self.flavor == "Numeric":
                    object__ = object__.astype(typecode[earray.type])
            object = object__[index]
            # The next adds much more verbosity
            if verbose and 0:
                print "number of row ==>", earray.nrow
                if hasattr(object, "shape"):
                    print "shape should look as:", object.shape
                print "row in earray ==>", repr(row)
                print "Should look like ==>", repr(object)

            assert self.nappends*self.chunksize == earray.nrows
            assert allequal(row, object, self.flavor)
            if hasattr(row, "shape"):
                assert len(row.shape) == len(self.shape) - 1
            else:
                # Scalar case
                assert len(self.shape) == 1

    def test03_readEArray(self):
        """Checking read() of enlargeable arrays"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_readEArray..." % self.__class__.__name__
            
        # Create an instance of an HDF5 Table
        if self.reopen:
            self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "EArray descr:", repr(earray)
            print "shape of read array ==>", earray.shape
            print "reopening?:", self.reopen
            
        # Build the array to do comparisons
        if self.flavor == "numarray":
            if str(self.type) == "CharType":
                object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                        itemsize=earray.itemsize)
            else:
                object_ = arange(self.objsize, shape=self.rowshape,
                                 type=earray.type)
            object_.swapaxes(earray.extdim, 0)
        else:
            object_ = Numeric.arange(self.objsize,
                                     typecode=typecode[earray.type])
            object_ = Numeric.reshape(object_, self.rowshape)
            object_ = Numeric.swapaxes(object_, earray.extdim, 0)
            
        rowshape = self.rowshape
        rowshape[self.extdim] *= self.nappends
        if self.flavor == "numarray":
            if str(self.type) == "CharType":
                object__ = strings.array(None, shape=rowshape,
                                         itemsize=earray.itemsize)
            else:
                object__ = array(None, shape = rowshape, type=self.type)
            object__.swapaxes(0, self.extdim)
        else:
            object__ = Numeric.zeros(self.rowshape, typecode[earray.type])
            object__ = Numeric.swapaxes(object__, earray.extdim, 0)

        for i in range(self.nappends):
            j = i * self.chunksize
            if str(self.type) == "CharType":
                object__[j:j+self.chunksize] = object_
            else:
                if self.flavor == "numarray":
                    object__[j:j+self.chunksize] = object_ * i
                else:
                    object__[j:j+self.chunksize] = (object_ * i).astype(typecode[earray.type])
        stop = self.stop
        if self.nappends:
            # stop == None means read only the element designed by start
            # (in read() contexts)
            if self.stop == None:
                if self.start == -1:  # corner case
                    stop = earray.nrows
                else:
                    stop = self.start + 1
            # Protection against number of elements less than existing
            #if rowshape[self.extdim] < self.stop or self.stop == 0:
            if rowshape[self.extdim] < stop:
                # self.stop == 0 means last row only in read()
                # and not in [::] slicing notation
                stop = rowshape[self.extdim]
            # do a copy() in order to ensure that len(object._data)
            # actually do a measure of its length
            object = object__[self.start:stop:self.step].copy()
            # Swap the axes again to have normal ordering
            if self.flavor == "numarray":
                object.swapaxes(0, self.extdim)
            else:
                object = Numeric.swapaxes(object, 0, self.extdim)
        else:
            if self.flavor == "numarray":
                object = array(None, shape = self.shape, type=self.type)
            else:
                object = Numeric.zeros(self.shape, typecode[self.type])

        # Read all the array
        try:
            row = earray.read(self.start,self.stop,self.step)
        except IndexError:
            if self.flavor == "numarray":
                row = array(None, shape = self.shape, type=self.type)
            else:
                row = Numeric.zeros(self.shape, typecode[self.type])

        if verbose:
            if hasattr(object, "shape"):
                print "shape should look as:", object.shape
            print "Object read ==>", repr(row)
            print "Should look like ==>", repr(object)
            
        assert self.nappends*self.chunksize == earray.nrows
        assert allequal(row, object, self.flavor)
        if hasattr(row, "shape"):
            assert len(row.shape) == len(self.shape)
        else:
            # Scalar case
            assert len(self.shape) == 1

    def test04_getitemEArray(self):
        """Checking enlargeable array __getitem__ special method"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_getitemEArray..." % self.__class__.__name__

        if not hasattr(self, "slices"):
            # If there is not a slices attribute, create it
            self.slices = (slice(self.start, self.stop, self.step),)
            
        # Create an instance of an HDF5 Table
        if self.reopen:
            self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        #earray._v_maxTuples = 3   # this does not really changes the chunksize
        if verbose:
            print "EArray descr:", repr(earray)
            print "shape of read array ==>", earray.shape
            print "reopening?:", self.reopen

        # Build the array to do comparisons
        if str(self.type) == "CharType":
            object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                    itemsize=earray.itemsize)
        else:
            object_ = arange(self.objsize, shape=self.rowshape,
                             type=earray.type)
        object_.swapaxes(earray.extdim, 0)
            
        rowshape = self.rowshape
        rowshape[self.extdim] *= self.nappends
        if str(self.type) == "CharType":
            object__ = strings.array(None, shape=rowshape,
                                     itemsize=earray.itemsize)
        else:
            object__ = array(None, shape = rowshape, type=self.type)
        object__.swapaxes(0, self.extdim)

        for i in range(self.nappends):
            j = i * self.chunksize
            if str(self.type) == "CharType":
                object__[j:j+self.chunksize] = object_
            else:
                object__[j:j+self.chunksize] = object_ * i

        stop = self.stop
        if self.nappends:
            # Swap the axes again to have normal ordering
            object__.swapaxes(0, self.extdim)
            # do a copy() in order to ensure that len(object._data)
            # actually do a measure of its length
            object = object__.__getitem__(self.slices).copy()
        else:
            object = array(None, shape = self.shape, type=self.type)

        if self.flavor == "Numeric":
            # Convert the object to Numeric
            object = Numeric.array(object, typecode=typecode[self.type])

        # Read all the array
        row = earray.__getitem__(self.slices)
        try:
            row = earray.__getitem__(self.slices)
        except IndexError:
            print "IndexError!"
            if self.flavor == "numarray":
                row = array(None, shape = self.shape, type=self.type)
            else:
                row = Numeric.zeros(self.shape, typecode[self.type])

        if verbose:
            if hasattr(object, "shape"):
                print "Original object shape:", self.shape
                print "Shape read:", row.shape
                print "shape should look as:", object.shape
            print "Object read:\n", repr(row) #, row.info()
            print "Should look like:\n", repr(object) #, row.info()

        assert self.nappends*self.chunksize == earray.nrows
        assert allequal(row, object, self.flavor)
        if not hasattr(row, "shape"):
            # Scalar case
            assert len(self.shape) == 1


class BasicWriteTestCase(BasicTestCase):
    type = Int32
    shape = (0,)
    chunksize = 5
    nappends = 10
    step = 1

class BasicWrite2TestCase(BasicTestCase):
    type = Int32
    shape = (0,)
    chunksize = 5
    nappends = 10
    step = 1
    reopen = 0  # This case does not reopen files
    
class EmptyEArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0)
    chunksize = 5
    nappends = 0
    start = 0
    stop = 10
    step = 1

class EmptyEArray2TestCase(BasicTestCase):
    type = Int32
    shape = (2, 0)
    chunksize = 5
    nappends = 0
    start = 0
    stop = 10
    step = 1
    reopen = 0  # This case does not reopen files

class SlicesEArrayTestCase(BasicTestCase):
    compress = 1
    complib = "lzo"
    type = Int32
    shape = (2, 0)
    chunksize = 5
    nappends = 2
    slices = (slice(1,2,1), slice(1,3,1))

class EllipsisEArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0)
    chunksize = 5
    nappends = 2
    #slices = (slice(1,2,1), Ellipsis)
    slices = (Ellipsis, slice(1,2,1))

class Slices2EArrayTestCase(BasicTestCase):
    compress = 1
    complib = "lzo"
    type = Int32
    shape = (2, 0, 4)
    chunksize = 5
    nappends = 20
    slices = (slice(1,2,1), slice(None, None, None), slice(1,4,2))

class Ellipsis2EArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0, 4)
    chunksize = 5
    nappends = 20
    slices = (slice(1,2,1), Ellipsis, slice(1,4,2))

class Slices3EArrayTestCase(BasicTestCase):
    compress = 1      # To show the chunks id DEBUG is on
    complib = "lzo"
    type = Int32
    shape = (2, 3, 4, 0)
    chunksize = 5
    nappends = 20
    slices = (slice(1, 2, 1), slice(0, None, None), slice(1,4,2))  # Don't work
    #slices = (slice(None, None, None), slice(0, None, None), slice(1,4,1)) # W
    #slices = (slice(None, None, None), slice(None, None, None), slice(1,4,2)) # N
    #slices = (slice(1,2,1), slice(None, None, None), slice(1,4,2)) # N
    # Disable the failing test temporarily with a working test case
    slices = (slice(1,2,1), slice(1, 4, None), slice(1,4,2)) # Y
    #slices = (slice(1,2,1), slice(0, 4, None), slice(1,4,1)) # Y
    slices = (slice(1,2,1), slice(0, 4, None), slice(1,4,2)) # N
    #slices = (slice(1,2,1), slice(0, 4, None), slice(1,4,2), slice(0,100,1)) # N

class Slices4EArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 4, 0, 5, 6)
    chunksize = 5
    nappends = 20
    slices = (slice(1, 2, 1), slice(0, None, None), slice(1,4,2),
              slice(0,4,2), slice(3,5,2), slice(2,7,1))

class Ellipsis3EArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 4, 0)
    chunksize = 5
    nappends = 20
    slices = (Ellipsis, slice(0, 4, None), slice(1,4,2))
    slices = (slice(1,2,1), slice(0, 4, None), slice(1,4,2), Ellipsis) 

class Ellipsis4EArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 4, 0)
    chunksize = 5
    nappends = 20
    slices = (Ellipsis, slice(0, 4, None), slice(1,4,2))
    slices = (slice(1,2,1), Ellipsis, slice(1,4,2))

class Ellipsis5EArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 4, 0)
    chunksize = 5
    nappends = 20
    slices = (slice(1,2,1), slice(0, 4, None), Ellipsis)

class Ellipsis6EArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 4, 0)
    chunksize = 5
    nappends = 2
    slices = (slice(1,2,1), slice(0, 4, None), 2, Ellipsis)

class MD3WriteTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0, 3)
    chunksize = 4
    step = 2

class MD5WriteTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0, 3, 4, 5)  # ok
    #shape = (1, 1, 0, 1)  # Minimum shape that shows problems with HDF5 1.6.1
    #shape = (2, 3, 0, 4, 5)  # Floating point exception (HDF5 1.6.1)
    #shape = (2, 3, 3, 0, 5, 6) # Segmentation fault (HDF5 1.6.1)
    chunksize = 1
    nappends = 1
    start = 1
    stop = 10
    step = 10

class MD6WriteTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 3, 0, 5, 6)
    chunksize = 1
    nappends = 10
    start = 1
    stop = 10
    step = 3

class MD6WriteTestCase__(BasicTestCase):
    type = Int32
    shape = (2, 0)
    chunksize = 1
    nappends = 3
    start = 1
    stop = 3
    step = 1

class MD7WriteTestCase(BasicTestCase):
    type = Int32
    shape = (2, 3, 3, 4, 5, 0, 3)
    chunksize = 10
    nappends = 1
    start = 1
    stop = 10
    step = 2

class MD10WriteTestCase(BasicTestCase):
    type = Int32
    shape = (1, 2, 3, 4, 5, 5, 4, 3, 2, 0)
    chunksize = 5
    nappends = 10
    start = -1
    stop = -1
    step = 10

class ZlibComprTestCase(BasicTestCase):
    compress = 1
    complib = "zlib"
    start = 3
    #stop = 0   # means last row
    stop = None   # means last row from 0.8 on
    step = 10

class ZlibShuffleTestCase(BasicTestCase):
    shuffle = 1
    compress = 1
    complib = "zlib"
    # case start < stop , i.e. no rows read
    start = 3
    stop = 1
    step = 10

class LZOComprTestCase(BasicTestCase):
    compress = 1  # sss
    complib = "lzo"
    chunksize = 10
    nappends = 100
    start = 3
    stop = 10
    step = 3

class LZOShuffleTestCase(BasicTestCase):
    compress = 1
    shuffle = 1
    complib = "lzo"
    chunksize = 100
    nappends = 10
    start = 3
    stop = 10
    step = 7

class UCLComprTestCase(BasicTestCase):
    compress = 1
    complib = "ucl"
    chunksize = 100
    nappends = 10
    start = 3
    stop = 10
    step = 8

class UCLShuffleTestCase(BasicTestCase):
    compress = 1
    shuffle = 1
    complib = "ucl"
    chunksize = 100
    nappends = 10
    start = 3
    stop = 10
    step = 6

class Fletcher32TestCase(BasicTestCase):
    compress = 0
    fletcher32 = 1
    chunksize = 50
    nappends = 20
    start = 4
    stop = 20
    step = 7

class AllFiltersTestCase(BasicTestCase):
    compress = 1
    shuffle = 1
    fletcher32 = 1
    complib = "ucl"
    chunksize = 20  # sss
    nappends = 50
    start = 2
    stop = 99 
    step = 6
#     chunksize = 3
#     nappends = 2
#     start = 1
#     stop = 10
#     step = 2

class FloatTypeTestCase(BasicTestCase):
    type = Float64
    shape = (2,0)
    chunksize = 5
    nappends = 10
    start = 3
    stop = 10
    step = 20

class CharTypeTestCase(BasicTestCase):
    type = "CharType"
    length = 20
    shape = (2,0)
    chunksize = 5
    nappends = 10
    start = 3
    stop = 10
    step = 20

class CharType2TestCase(BasicTestCase):
    type = "CharType"
    length = 20
    shape = (0,)
    chunksize = 5
    nappends = 10
    start = 1
    stop = 10
    step = 2

class CharTypeComprTestCase(BasicTestCase):
    type = "CharType"
    length = 20
    shape = (20,0,10)
    compr = 1
    #shuffle = 1  # this shouldn't do nothing on chars
    chunksize = 50
    nappends = 10
    start = -1
    stop = 100
    step = 20

class Numeric1TestCase(BasicTestCase):
    #flavor = "Numeric"
    type = "Int32"
    shape = (2,0)
    compr = 1
    shuffle = 1
    chunksize = 50
    nappends = 20
    start = -1
    stop = 100
    step = 20

class Numeric2TestCase(BasicTestCase):
    flavor = "Numeric"
    type = "Float32"
    shape = (0,)
    compr = 1
    shuffle = 1
    chunksize = 2
    nappends = 1
    start = -1
    stop = 100
    step = 20

class NumericComprTestCase(BasicTestCase):
    flavor = "Numeric"
    type = "Float64"
    compress = 1
    shuffle = 1
    shape = (0,)
    compr = 1
    chunksize = 2
    nappends = 1
    start = 51
    stop = 100
    step = 7

# It remains a test of Numeric char types, but the code is getting too messy

class OffsetStrideTestCase(unittest.TestCase):
    mode  = "w" 
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        
    #----------------------------------------

    def test01a_String(self):
        """Checking earray with offseted numarray strings appends"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01a_StringAtom..." % self.__class__.__name__

        # Create an string atom
        earray = self.fileh.createEArray(root, 'strings',
                                         strings.array(None, itemsize=3,
                                                       shape=(0,2,2)),
                                         "Array of strings")
        a=strings.array([[["a","b"],["123", "45"],["45", "123"]]], itemsize=3)
        earray.append(a[:,1:])
        a=strings.array([[["s", "a"],["ab", "f"],["s", "abc"],["abc", "f"]]])
        earray.append(a[:,2:])

        # Read all the rows:
        row = earray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", earray._v_pathname, ":", earray.nrows
            print "Second row in earray ==>", row[1].tolist()
            
        assert earray.nrows == 2
        assert row[0].tolist() == [["123", "45"],["45", "123"]]
        assert row[1].tolist() == [["s", "abc"],["abc", "f"]]
        assert len(row[0]) == 2
        assert len(row[1]) == 2

    def test01b_String(self):
        """Checking earray with strided numarray strings appends"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_StringAtom..." % self.__class__.__name__

        # Create an string atom
        earray = self.fileh.createEArray(root, 'strings',
                                         strings.array(None, itemsize=3,
                                                       shape=(0,2,2)),
                                         "Array of strings")
        a=strings.array([[["a","b"],["123", "45"],["45", "123"]]], itemsize=3)
        earray.append(a[:,::2])
        a=strings.array([[["s", "a"],["ab", "f"],["s", "abc"],["abc", "f"]]])
        earray.append(a[:,::2])

        # Read all the rows:
        row = earray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", earray._v_pathname, ":", earray.nrows
            print "Second row in earray ==>", row[1].tolist()
            
        assert earray.nrows == 2
        assert row[0].tolist() == [["a","b"],["45", "123"]]
        assert row[1].tolist() == [["s", "a"],["s", "abc"]]
        assert len(row[0]) == 2
        assert len(row[1]) == 2

    def test02a_int(self):
        """Checking earray with offseted numarray ints appends"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02a_int..." % self.__class__.__name__

        # Create an string atom
        earray = self.fileh.createEArray(root, 'EAtom',
                                         array(None, shape = (0,3),
                                               type=Int32),
                                         "array of ints")
        a=array([(0,0,0), (1,0,3), (1,1,1), (0,0,0)], type=Int32)
        earray.append(a[2:])  # Create an offset
        a=array([(1,1,1), (-1,0,0)], type=Int32)
        earray.append(a[1:])  # Create an offset

        # Read all the rows:
        row = earray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", earray._v_pathname, ":", earray.nrows
            print "Third row in vlarray ==>", row[2]
            
        assert earray.nrows == 3
        assert allequal(row[0], array([1,1,1], type=Int32))
        assert allequal(row[1], array([0,0,0], type=Int32))
        assert allequal(row[2], array([-1,0,0], type=Int32))

    def test02b_int(self):
        """Checking earray with strided numarray ints appends"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02b_int..." % self.__class__.__name__

        # Create an string atom
        earray = self.fileh.createEArray(root, 'EAtom',
                                         array(None, shape = (0,3),
                                               type=Int32),
                                         "array of ints")
        a=array([(0,0,0), (1,0,3), (1,1,1), (3,3,3)], type=Int32)
        earray.append(a[::3])  # Create an offset
        a=array([(1,1,1), (-1,0,0)], type=Int32)
        earray.append(a[::2])  # Create an offset

        # Read all the rows:
        row = earray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", earray._v_pathname, ":", earray.nrows
            print "Third row in vlarray ==>", row[2]
            
        assert earray.nrows == 3
        assert allequal(row[0], array([0,0,0], type=Int32))
        assert allequal(row[1], array([3,3,3], type=Int32))
        assert allequal(row[2], array([1,1,1], type=Int32))


#----------------------------------------------------------------------

def suite():
    theSuite = unittest.TestSuite()
    global numeric
    niter = 1

    #theSuite.addTest(unittest.makeSuite(BasicWriteTestCase))
    #theSuite.addTest(unittest.makeSuite(BasicWrite2TestCase))
    #theSuite.addTest(unittest.makeSuite(EmptyEArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(EmptyEArray2TestCase))
    #theSuite.addTest(unittest.makeSuite(SlicesEArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(EllipsisEArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Slices2EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Ellipsis2EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Slices3EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Slices4EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Ellipsis3EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Ellipsis4EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Ellipsis5EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(Ellipsis6EArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(MD3WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(MD5WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(MD6WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(MD7WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(MD10WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(ZlibComprTestCase))
    #theSuite.addTest(unittest.makeSuite(ZlibShuffleTestCase))
    #theSuite.addTest(unittest.makeSuite(LZOComprTestCase))
    #theSuite.addTest(unittest.makeSuite(LZOShuffleTestCase))
    #theSuite.addTest(unittest.makeSuite(UCLComprTestCase))
    #theSuite.addTest(unittest.makeSuite(UCLShuffleTestCase))
    #theSuite.addTest(unittest.makeSuite(FloatTypeTestCase))
    #theSuite.addTest(unittest.makeSuite(CharTypeTestCase))
    #theSuite.addTest(unittest.makeSuite(CharType2TestCase))
    #theSuite.addTest(unittest.makeSuite(CharTypeComprTestCase))
    #theSuite.addTest(unittest.makeSuite(Numeric1TestCase))
    #theSuite.addTest(unittest.makeSuite(Numeric2TestCase))
    #theSuite.addTest(unittest.makeSuite(NumericComprTestCase))
    #theSuite.addTest(unittest.makeSuite(OffsetStrideTestCase))
    #theSuite.addTest(unittest.makeSuite(AllFiltersTestCase))

    for n in range(niter):
        theSuite.addTest(unittest.makeSuite(BasicWriteTestCase))
        theSuite.addTest(unittest.makeSuite(BasicWrite2TestCase))
        theSuite.addTest(unittest.makeSuite(EmptyEArrayTestCase))
        theSuite.addTest(unittest.makeSuite(EmptyEArray2TestCase))
        theSuite.addTest(unittest.makeSuite(SlicesEArrayTestCase))
        theSuite.addTest(unittest.makeSuite(EllipsisEArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Slices2EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Ellipsis2EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Slices3EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Slices4EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Ellipsis3EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Ellipsis4EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Ellipsis5EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(Ellipsis6EArrayTestCase))
        theSuite.addTest(unittest.makeSuite(MD3WriteTestCase))
        theSuite.addTest(unittest.makeSuite(MD5WriteTestCase))
        theSuite.addTest(unittest.makeSuite(MD6WriteTestCase))
        theSuite.addTest(unittest.makeSuite(MD7WriteTestCase))
        theSuite.addTest(unittest.makeSuite(MD10WriteTestCase))
        theSuite.addTest(unittest.makeSuite(ZlibComprTestCase))
        theSuite.addTest(unittest.makeSuite(ZlibShuffleTestCase))
        theSuite.addTest(unittest.makeSuite(LZOComprTestCase))
        theSuite.addTest(unittest.makeSuite(LZOShuffleTestCase))
        theSuite.addTest(unittest.makeSuite(UCLComprTestCase))
        theSuite.addTest(unittest.makeSuite(UCLShuffleTestCase))
        theSuite.addTest(unittest.makeSuite(FloatTypeTestCase))
        theSuite.addTest(unittest.makeSuite(CharTypeTestCase))    
        theSuite.addTest(unittest.makeSuite(CharType2TestCase))    
        theSuite.addTest(unittest.makeSuite(CharTypeComprTestCase))
        if numeric:
            theSuite.addTest(unittest.makeSuite(Numeric1TestCase))
            theSuite.addTest(unittest.makeSuite(Numeric2TestCase))
            theSuite.addTest(unittest.makeSuite(NumericComprTestCase))
        theSuite.addTest(unittest.makeSuite(OffsetStrideTestCase))
        theSuite.addTest(unittest.makeSuite(Fletcher32TestCase))
        theSuite.addTest(unittest.makeSuite(AllFiltersTestCase))

    return theSuite


if __name__ == '__main__':
    unittest.main( defaultTest='suite' )
