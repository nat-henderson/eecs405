import math

class BPTree:
    def __init__(self, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing = True):
        self.keySize = keySize
        self.dataRecordSize = dataRecord
        self.blockPointerSize = blockPointer
        self.dataPointerSize = dataPointer
        self.blockSize = blockSize
        self.coalescing = coalescing
        self.root = BPleaf(self, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing, keys = [])
    
    def insert(self, key):
        node = self.root
        while not isinstance(node, BPleaf):
            node = node.search(key)
        node.insert(key)
    
    def delete(self, key):
        node = self.root
        while not isinstance(node, BPleaf):
            node = node.search(key)
        node.delete(key)
    
    def lookup(self, key):
        return self.root.findKey(key, 1)
    
    def height(self):
        height = 1
        node = self.root
        while not isinstance(node, BPleaf):
            node = node.children[0]
            height = height + 1
        return height
    
    def numIndexBlocks(self):
        return self.root.numIndexBlocks()
    
    def numDataBlocks(self):
        dataPerBlock = math.floor(self.blockSize / self.dataRecordSize)
        if dataPerBlock == 0:
            return self.numElements()
        else:
            return math.ceil(self.numElements() / dataPerBlock)
    
    def numElements(self):
        return self.root.numElements()
    
    def storageUtil(self):
        return self.root.storageUtil(self.keySize, self.dataRecordSize, self.blockPointerSize, self.dataPointerSize) / (self.numIndexBlocks() * self.blockSize * 1.0)
    
    def __str__(self):
        return str(self.root)

class BPnode:
    def __init__(self, parent, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing, keys=[], children=[]):
        self.keySize=keySize
        self.dataRecordSize = dataRecord
        self.blockPointerSize = blockPointer
        self.dataPointerSize = dataPointer
        self.blockSize = blockSize
        self.parent = parent
        self.order = int(math.floor(float(blockSize-blockPointer)/(keySize+blockPointer))) + 1
        self.keys = keys
        self.coalescing = coalescing
        self.children = children
        
    def insert(self, node):
        minimum = node.findMin()
        
        if len(self.children) == 0:
            self.children.append(node)
        elif len(self.children) == 1:
            if self.children[0].findMin() < minimum:
                self.keys.append(minimum)
                self.children.append(node)
            else:
                self.keys.append(self.children[0].findMin())
                self.children.insert(0,node)
        else:
            if minimum <= self.children[0].findMin():
                self.children.insert(0, node)
                self.keys.insert(0, self.children[1].findMin())
                if isinstance(self.parent, BPnode):
                    self.parent.updateKey(self)
            else:
                index = 0
                while index < len(self.keys) and minimum >= self.keys[index]:
                    index = index + 1
                self.keys.insert(index, minimum)
                self.children.insert(index+1, node)
        
        node.updateParent(self)
        
        if len(self.children) > self.order:
            self.split()
    
    def split(self):
        mid = int(math.ceil(self.order/2.0))
        newKeys = self.keys[:(mid-1)]
        newChildren = self.children[:mid]
        self.keys = self.keys[mid:]
        self.children = self.children[mid:]
        newNode = BPnode(self.parent, self.keySize, self.dataRecordSize, self.blockPointerSize, self.dataPointerSize, self.blockSize, self.coalescing, keys=newKeys, children=newChildren)
        if isinstance(self.parent, BPnode):
            self.parent.updateKey(self)
        
        for child in newChildren:
            child.updateParent(newNode)
        
        if isinstance(self.parent, BPTree):
            tree = self.parent
            newRoot = BPnode(tree, self.keySize, self.dataRecordSize, self.blockPointerSize, self.dataPointerSize, self.blockSize, self.coalescing, keys=[], children=[])
            tree.root = newRoot
            self.parent = newRoot
            newNode.parent = newRoot
            newRoot.insert(self)
            newRoot.insert(newNode)
        else:
            self.parent.insert(newNode)
    
    def combine(self, node):
        if len(self.children) == 1:
            self.children.pop(0)
        else:
            index = self.children.index(node)
            if index == len(self.children) - 1:
                mergeChild = self.children[index-1]
                self.children.pop(index-1)
                self.keys.pop(index-1)
            else:
                mergeChild = self.children[index+1]
                self.children.pop(index+1)
                self.keys.pop(index)
            node.merge(mergeChild)
        
        if isinstance(self.parent, BPTree) and len(self.children) == 1:
            self.parent.root = self.children[0]
            self.children[0].parent = self.parent
        elif not isinstance(self.parent, BPTree) and len(self.children) < math.ceil(self.order/2.0) and self.coalescing:
            self.parent.combine(self)
        elif not isinstance(self.parent, BPTree) and not self.coalescing and len(self.children) == 0:
            self.parent.combine(self)
    
    def merge(self, node):
        if len(self.children) == 0:
            self.keys.extend(node.keys)
            self.children.extend(node.children)
        elif self.findMin() < node.findMin():
            self.keys.append(node.findMin())
            self.keys.extend(node.keys)
            self.children.extend(node.children)
        else:
            node.keys.append(self.findMin())
            node.keys.extend(self.keys)
            self.keys = node.keys
            node.children.extend(self.children)
            self.children = node.children
        
        for child in node.children:
            child.updateParent(self)
        
        if len(self.children) > self.order:
            self.split()
    
    def search(self, key):
        assert len(self.children) > 0
        if len(self.children) == 1:
            return self.children[0]

        child = 0
        while child < len(self.keys) and key >= self.keys[child]:
            child = child + 1
        return self.children[child]
    
    def findKey(self, key, level):
        if len(self.children) == 1:
            return self.children[0].findKey(key, level+1)

        child = 0
        while child < len(self.keys) and key >= self.keys[child]:
            child = child + 1
        return self.children[child].findKey(key, level+1)
    
    def findMin(self):
        return self.children[0].findMin()
    
    def updateKey(self, node):
        index = self.children.index(node)
        if index > 0:
            self.keys[index-1] = node.findMin()
        elif not isinstance(self.parent, BPTree):
            self.parent.updateKey(self)
    
    def updateParent(self, parent):
        self.parent = parent
    
    def numIndexBlocks(self):
        blocks = 1
        for child in self.children:
            blocks = blocks + child.numIndexBlocks()
        return blocks
    
    def storageUtil(self, keySize, dataRecordSize, blockPointerSize, dataPointerSize):
        childrenUtil = 0
        for child in self.children:
            childrenUtil = childrenUtil + child.storageUtil(keySize, dataRecordSize, blockPointerSize, dataPointerSize)
        return keySize*len(self.keys) + blockPointerSize*len(self.children) + childrenUtil
    
    def numElements(self):
        elements = 0
        for child in self.children:
            elements = elements + child.numElements()
        return elements
    
    def __str__(self):
        output = "[ \n"
        output = output + str(self.children[0])
        index = 0
        while index < len(self.keys):
            output = output + str(self.keys[index]) + " " + str(self.children[index+1]) + " "
            index = index + 1
        output = output + "]\n"
        return output

class BPleaf:
    def __init__(self, parent, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing, keys=[]):
        self.parent = parent
        self.keySize=keySize
        self.dataRecordSize = dataRecord
        self.blockPointerSize = blockPointer
        self.dataPointerSize = dataPointer
        self.blockSize = blockSize
        self.order = int(math.floor(float(blockSize-blockPointer)/(keySize+dataPointer)))
        self.keys = keys
        self.coalescing = coalescing
        
    def insert(self, key):
        self.keys.append(key)
        self.keys.sort()
        if len(self.keys) > self.order:
            self.split()
    
    def split(self):
        newNodeList = self.keys[int(math.ceil(self.order/2.0)):]
        self.keys = self.keys[:int(math.ceil(self.order/2.0))]
        newNode = BPleaf(self.parent, self.keySize, self.dataRecordSize, self.blockPointerSize, self.dataPointerSize, self.blockSize, self.coalescing, newNodeList)
        if isinstance(self.parent, BPTree):
            tree = self.parent
            newRoot = BPnode(tree, tree.keySize, tree.dataRecordSize, tree.blockPointerSize, tree.dataPointerSize, tree.blockSize, self.coalescing, keys=[], children=[])
            tree.root = newRoot
            self.parent = newRoot
            newNode.parent = newRoot
            newRoot.insert(self)
            newRoot.insert(newNode)
        else:
            self.parent.updateKey(self)
            self.parent.insert(newNode)
        
    def delete(self, key):
        if key in self.keys:
            index = self.keys.index(key)
            self.keys.remove(key)
            if index == 0 and len(self.keys) > 0 and not isinstance(self.parent, BPTree):
                self.parent.updateKey(self)
            if len(self.keys) < math.ceil(self.order/2.0) and not isinstance(self.parent, BPTree) and self.coalescing:
                self.parent.combine(self)
            elif not self.coalescing and len(self.keys) == 0 and isinstance(self.parent, BPnode):
                self.parent.combine(self)
            return True
        else:
            return False
    
    def merge(self, node):
        if len(self.keys) == 0:
            self.keys = node.keys
        else:
            if node.findMin() < self.findMin():
                self.keys = node.keys + self.keys
            else:
                self.keys = self.keys + node.keys
        if len(self.keys) > self.order:
            self.split()
    
    def findMin(self):
        return self.keys[0]
    
    def findKey(self, key, level):
        if key in self.keys:
            return level
        else:
            return -1;
    
    def updateParent(self, parent):
        self.parent = parent
    
    def numIndexBlocks(self):
        return 1
    
    def storageUtil(self, keySize, dataRecordSize, blockPointerSize, dataPointerSize):
        return blockPointerSize + len(self.keys)*(keySize + dataPointerSize)
    
    def numElements(self):
        return len(self.keys)
    
    def __str__(self):
        output = "[ "
        index = 0
        while index < len(self.keys):
            output = output + str(self.keys[index]) + " "
            index = index + 1
        output = output + "]\n"
        return output
        
