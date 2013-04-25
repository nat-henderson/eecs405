import math

class BTree(object):

    def __init__(self, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing = True):
        self.keySize = keySize
        self.dataRecordSize = dataRecord
        self.blockPointerSize = blockPointer
        self.dataPointerSize = dataPointer
        self.blockSize = blockSize
        self.coalescing = coalescing
        self.root = Leaf(self, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing, keys = [])
    
    def insert(self, key):
        node = self.root
        while not isinstance(node, Leaf):
            node = node.insertSearch(key)
        node.insert(key)
    
    def delete(self, key):
        node = self.root
        while not isinstance(node, Leaf):
            nextNode = node.deleteSearch(key)
            if nextNode == node:
                break
            node = nextNode
        node.delete(key)
    
    def lookup(self, key):
        return self.root.findKey(key,1)
    
    def height(self):
        height = 1
        node = self.root
        while not isinstance(node, Leaf):
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

class Node(object):
    
    def __init__(self, parent, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing, keys=[], children=[]):
        self.parent = parent
        self.order = int(math.floor(float(blockSize-blockPointer)/(keySize+blockPointer+dataPointer))) + 1
        self.keys = keys
        self.coalescing = coalescing
        self.children = children
    
    def insertSearch(self, key):
        assert len(self.children) > 0
        if len(self.children) == 1:
            return self.children[0]
        
        child = 0
        while child < len(self.keys) and key >= self.keys[child]:
            child = child + 1
        return self.children[child]
    
    def deleteSearch(self, key):
        if key in self.keys:
            return self
        
        assert len(self.children) > 0
        if len(self.children) == 1:
            return self.children[0]
        
        child = 0
        while child < len(self.keys) and key >= self.keys[child]:
            child = child + 1
        return self.children[child]
    
    def findKey(self, key, level):
        if key in self.keys:
            return level
        else:
            if len(self.children) == 1:
                return self.children[0].findKey(key,level+1)
        
            child = 0
            while child < len(self.keys) and key >= self.keys[child]:
                child = child + 1
            return self.children[child].findKey(key,level+1)
    
    def combine(self, node):
        if node in self.children:
            if len(self.children) == 1:
                self.children.pop(0);
                if isinstance(self.parent, Node):
                    self.parent.combine(self)
                return
            
            index = self.children.index(node)
            if index == len(self.children) - 1:
                mergeChild = self.children[index-1]
                self.children.pop(index-1)
                parentKey = self.keys[index-1]
                self.keys.pop(index-1)
            else:
                mergeChild = self.children[index+1]
                self.children.pop(index+1)
                parentKey = self.keys[index]
                self.keys.pop(index)
            node.merge(mergeChild, parentKey)
            
            if isinstance(self.parent, BTree) and len(self.children) == 1:
                self.parent.root = self.children[0]
                self.children[0].parent = self.parent
            elif isinstance(self.parent, Node) and len(self.children) < math.ceil(self.order/2.0) and self.coalescing:
                self.parent.combine(self)
            elif isinstance(self.parent, Node) and len(self.children) == 0 and not self.coalescing:
                self.parent.combine(self)
    
    def merge(self, node, parentKey):
        if len(self.children) == 0:
            self.keys.extend(node.keys)
            self.children.extend(node.children)
        elif self.findMin() < node.findMin:
            self.children.extend(node.children)
            self.keys.append(parentKey)
            self.keys.extend(node.keys)
        else:
            node.children.extend(self.children)
            node.keys.append(parentKey)
            node.keys.extend(self.keys)
            self.children = node.children
            self.keys = node.keys
        
        for child in node.children:
            child.updateParent(self)
            
        if len(self.children) > self.order:
            self.split()
            
    def split(self):
        mid = int(math.ceil(self.order/2.0))
        newKeys = self.keys[:(mid-1)]
        parentKey = self.keys[(mid-1)]
        self.keys = self.keys[mid:]
        newChildren = self.children[:mid]
        self.children = self.children[mid:]
        newNode = Node(self.parent, 1, 0, 0, 0, self.order-1, self.coalescing, keys=newKeys, children=newChildren)
        
        for child in newChildren:
            child.updateParent(newNode)
        
        if isinstance(self.parent, BTree):
            tree = self.parent
            newRoot = Node(tree, 1, 0, 0, 0, self.order-1, self.coalescing, keys=[], children=[self])
            tree.root = newRoot
            self.parent = newRoot
            newNode.parent = newRoot
            newRoot.insertPair(newNode, parentKey)
        else:
            self.parent.insertPair(newNode, parentKey)
    
    def insertPair(self, node, key):
        minimum = node.findMin()
        
        if len(self.children) == 1:
            if self.children[0].findMin() < minimum:
                self.keys.append(key)
                self.children.append(node)
            else:
                self.keys.append(key)
                self.children.insert(0,node)
        else:
            index = 0
            while index < len(self.children) and minimum > self.children[index].findMin():
                index = index + 1
            self.children.insert(index, node)
            index = 0
            while index < len(self.keys) and key > self.keys[index]:
                index = index + 1
            self.keys.insert(index, key)
        
        node.updateParent(self)
            
        if len(self.children) > self.order:
            self.split()
    
    def delete(self, key):
        if key in self.keys:
            index = self.keys.index(key)
            replacement = self.children[index+1].findMin()
            self.keys.remove(key)
            self.keys.insert(index,replacement)
            self.children[index+1].delete(replacement)
            return True
        else:
            return False
    
    def findMin(self):
        return self.children[0].findMin()
    
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
        return (keySize + dataPointerSize)*len(self.keys) + blockPointerSize*len(self.children) + childrenUtil
    
    def numElements(self):
        childElements = 0
        for child in self.children:
            childElements = childElements + child.numElements()
        return len(self.keys) + childElements
    
    def __str__(self):
        output = "[ \n"
        output = output + str(self.children[0])
        index = 0
        while index < len(self.keys):
            output = output + str(self.keys[index]) + " " + str(self.children[index+1]) + " "
            index = index + 1
        output = output + "]\n"
        return output

class Leaf(object):
    
    def __init__(self, parent, keySize, dataRecord, blockPointer, dataPointer, blockSize, coalescing, keys=[]):
        self.parent = parent
        self.order = int(math.floor(float(blockSize-blockPointer)/(keySize+dataPointer)))
        self.keys = keys
        self.coalescing = coalescing
    
    def delete(self, key):
        if key in self.keys:
            self.keys.remove(key)
            if self.coalescing and isinstance(self.parent, Node) and len(self.keys) < math.ceil(self.order/2.0):
                self.parent.combine(self)
            elif not self.coalescing and isinstance(self.parent, Node) and len(self.keys) == 0:
                self.parent.combine(self)
            return True
        else:
            return False
    
    def insert(self, key):
        self.keys.append(key)
        self.keys.sort()
        if len(self.keys) > self.order:
            self.split()
    
    def merge(self, node, parentKey):
        if len(self.keys) == 0 or len(node.keys) == 0:
            self.keys.append(parentKey)
            self.keys.extend(node.keys)
        elif self.findMin() < node.findMin():
            self.keys.append(parentKey)
            self.keys.extend(node.keys)
        else:
            node.keys.append(parentKey)
            node.keys.extend(self.keys)
            self.keys = node.keys
            
        if len(self.keys) > self.order:
            self.split()
    
    def split(self):
        mid = int(math.ceil(self.order/2.0))
        newKeys = self.keys[:(mid)]
        parentKey = self.keys[(mid)]
        self.keys = self.keys[(mid+1):]
        newNode = Leaf(self.parent, 1, 0, 0, 0, self.order, self.coalescing, keys=newKeys)
        if isinstance(self.parent, BTree):
            tree = self.parent
            newRoot = Node(tree, tree.keySize, tree.dataRecordSize, tree.blockPointerSize, tree.dataPointerSize, tree.blockSize, self.coalescing, keys=[], children=[self])
            tree.root = newRoot
            self.parent = newRoot
            newNode.parent = newRoot
            newRoot.insertPair(newNode, parentKey)
        else:
            self.parent.insertPair(newNode, parentKey)
    
    def findMin(self):
        return self.keys[0]
    
    def findKey(self, key, level):
        if key in self.keys:
            return level
        else:
            return -1
    
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
