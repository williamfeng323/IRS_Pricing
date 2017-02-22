#!/usr/bin/python
# Reference from http://stackoverflow.com/questions/2598437/how-to-implement-a-binary-tree
# Add function binaryTreePaths(), updateRoot(), bindLeft(), bindRight(), addLeft(), addRight(), getAllLeft()


class Node:
    def __init__(self, val):
        self.l = None
        self.r = None
        self.v = val


class Tree:
    def __init__(self, val=None):
        self.root = val

    def getRoot(self):
        return self.root

    def add(self, val):
        if self.root is None:
            self.root = Node(val)
        else:
            self._add(val, self.root)

    def _add(self, val, node):
        if val < node.v:
            if node.l is not None:
                self._add(val, node.l)
            else:
                node.l = Node(val)
        else:
            if node.r is not None :
                self._add(val, node.r)
            else:
                node.r = Node(val)

    def updateRoot(self, val):
        self.root = Node(val)

    def addLeft(self, val):
        if self.root is None:
            return None
        else:
            self.root.l = Node(val)

    def addRight(self, val):
        if self.root is None:
            return None
        else:
            self.root.r = Node(val)

    def bindLeft(self, node):
        if self.root is None:
            return None
        else:
            self.root.l = node

    def bindRight(self, node):
        if self.root is None:
            return None
        else:
            self.root.r = node

    def find(self, val):
        if self.root is not None :
            return self._find(val, self.root)
        else:
            return None

    def _find(self, val, node):
        if val is node.v:
            return node
        elif val < node.v and node.l is not None:
            self._find(val, node.l)
        elif val > node.v and node.r is not None:
            self._find(val, node.r)

    def deleteTree(self):
        # garbage collector will do this for us.
        self.root = None

    def printTree(self):
        if self.root is not None:
            self._printTree(self.root)

    def _printTree(self, node):
        if node is not None:
            self._printTree(node.l)
            print(str(node.v) + ' ')
            self._printTree(node.r)

    def getAllLeft(self):
        if self.root is None:
            return None
        next_left = self.root
        left_values = []
        while next_left is not None:
            left_values.append(next_left.v)
            next_left = self.getNextLeft(next_left.l)
        return left_values

    def getNextLeft(self, node):
        if node is None:
            return None
        else:
            return node

    def binaryTreePaths(self, val):
        self.ans = list()
        if self.root is None:
            return self.ans

        def dfs(root, path):
            if root.v == val:
                self.ans += path,
            if root.l:
                dfs(root.l, path + "->" + str(root.l.v))
            if root.r:
                dfs(root.r, path + "->" + str(root.r.v))

        dfs(self.root, str(self.root.v))
        return self.ans