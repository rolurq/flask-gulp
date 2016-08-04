import sys
from collections import deque


if sys.version_info.major == 3:
    xrange = range

Asterisk = 256
DoubleAsterisk = 257


def compile(*patterns):
    wildtree = Wildcard()
    last = 0
    # create GOTO
    for s in patterns:
        q = j = 0
        while wildtree.goto(q, s[j]) is not None:
            q = wildtree.goto(q, s[j])
            j += 1
        scape = False
        lenght = len(s)
        while j < lenght:
            if s[j] == '\\' and j + 1 < lenght and s[j + 1] == '*':
                scape = True
                continue
            symbol = s[j]
            if symbol == '*':
                if scape:
                    last += 1
                    wildtree.addGoto(q, symbol, last)
                    q = last
                    scape = False
                elif j + 1 < lenght and s[j + 1] == '*':
                    wildtree.addOutput(q, DoubleAsterisk)
                    j += 1
                else:
                    wildtree.addOutput(q, Asterisk)
            else:
                last += 1
                wildtree.addGoto(q, symbol, last)
                q = last
            j += 1
        wildtree.addOutput(q)
    # create FAILURE
    queue = deque()
    for i, state in enumerate(wildtree.goto(0)):
        # if state is None:
        #     wildtree.addGoto(0, i, 0)
        # elif state != 0:
        if None is not state is not 0:
            queue.append(state)
            # wildtree.setFailure(state, 0)
    while len(queue):
        r = queue.popleft()
        aster = wildtree.output(r).aster
        for symbol, state in enumerate(wildtree.goto(r)):
            if state is not None:
                queue.append(state)
                if aster is Asterisk and symbol != '/' or\
                        aster is DoubleAsterisk:
                # if aster is None or aster is Asterisk and symbol == '/':
                #     q = wildtree.failure(r)
                #     while wildtree.goto(q, symbol) is None:
                #         q = wildtree.failure(q)
                #     wildtree.setFailure(state, wildtree.goto(q, symbol))
                # else:
                    # ** and * children fails onto ** and *
                    wildtree.setFailure(state, r)
    return wildtree

CHAR_COUNT = 258


class Output:
    def __init__(self, final=False, aster=None):
        self.final = final
        self.aster = aster


class GrowList(list):
    def __init__(self, iterable=None, call=lambda: None):
        self.call = call
        sp = super(GrowList, self)
        if iterable:
            sp.__init__(iterable)
        else:
            sp.__init__()

    def __setitem__(self, index, value):
        self.grow(index)
        return super(GrowList, self).__setitem__(index, value)

    def __getitem__(self, index):
        self.grow(index)
        return super(GrowList, self).__getitem__(index)

    def grow(self, top):
        lenght = len(self)
        if lenght <= top:
            for _ in xrange(top - lenght + 1):
                self.append(self.call())
            return True
        return False


class Wildcard:
    def __init__(self):
        self.gotof = GrowList(call=lambda: [None for _ in xrange(CHAR_COUNT)])
        self.failuref = GrowList()
        self.outputf = GrowList(call=Output)
        self.mmode = False

    def addGoto(self, src, symbol, dest):
        # self.gotof.append([None for _ in xrange(CHAR_COUNT)])

        index = symbol if isinstance(symbol, int) else ord(symbol)
        self.gotof[src][index] = dest

    def addOutput(self, state, value=True):
        self.outputf[state] = Output()
        if value is True:
            self.outputf[state].final = True
        else:
            self.failuref[state] = state
            self.outputf[state].aster = value

    def setFailure(self, src, dest):
        self.failuref[src] = dest

    def goto(self, state, symbol=None):
        if symbol is None:
            return iter(self.gotof[state])
        # return new state or test if the state contains ** or *
        aster = self.outputf[state].aster
        loop = state
        if aster is None or aster is Asterisk and symbol == '/':
            loop = None
        symbol = symbol if isinstance(symbol, int) else ord(symbol)
        trans = self.gotof[state][symbol]
        return trans if trans == 0 or not self.mmode else trans or loop

    def failure(self, state):
        return self.failuref[state]

    def output(self, state):
        return self.outputf[state]

    def match(self, cad):
        self.mmode = True
        q = 0
        c = 0
        ret = False
        for symbol in cad:
            while self.goto(q, symbol) is None:
                q = self.failuref[q]
                if q is None:
                    ret = False
                    break
            q = self.goto(q, symbol)
            if q:
                c += 1
            ret = self.outputf[q].final
        self.mmode = False
        return ret, c
