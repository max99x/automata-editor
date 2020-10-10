from os import popen
from pickle import dumps as serialize, loads as unserialize
from math import sqrt

# Exceptions


class AutomataError(Exception):
    pass

# Single Attributes Get/Set


def genGetMethod(attr):
    def getMethod(self):
        return getattr(self, attr)
    return getMethod


def genSetMethod(attr, validType):
    if type(validType) is type:
        def setMethod(self, val):
            if type(val) == validType:
                setattr(self, attr, val)
            else:
                raise AutomataError('%s must be a %s, not %s.' % (
                    attr.strip('_'), validType.__name__, type(val).__name__))
    else:
        def setMethod(self, val):
            if validType(val):
                setattr(self, attr, val)
            else:
                raise AutomataError(
                    'Attempted to set an invalid %s.' % attr.strip('_'))
    return setMethod


# List Attributes Get/Set
def genCollGetMethod(attr):
    def getMethod(self):
        return tuple(getattr(self, attr))
    return getMethod


def genCollSetMethod(attr, validType, colltype=None):
    if colltype:
        def setMethod(self, val):
            if all([type(i) == validType for i in val]):
                setattr(self, attr, colltype(val))
            else:
                raise AutomataError('%s must contain only items of type: %s.' % (
                    attr.strip('_'), validType.__name__))
    else:
        def setMethod(self, val):
            if colltype and all([type(i) == validType for i in val]):
                setattr(self, attr, val)
            else:
                raise AutomataError('%s must contain only items of type: %s.' % (
                    attr.strip('_'), validType.__name__))

    return setMethod


def genAddMethod(attr, validType):
    if type(validType) is type:
        def addMethod(self, item):
            if type(item) is validType:
                getattr(self, attr).add(item)
            else:
                raise AutomataError('%s must contain only items of type: %s, not %s.' % (
                    attr.strip('_'), validType.__name__, type(item).__name__))
    else:
        def addMethod(self, item):
            if validType(item):
                getattr(self, attr).add(item)
            else:
                raise AutomataError(
                    'Attempted to set an invalid  %s.' % attr.strip('_'))
    return addMethod


def genRemMethod(attr, validType):
    def remItemMethod(self, which):
        try:
            if type(which) is validType:
                getattr(self, attr).remove(which)
            else:
                raise AutomataError('%s contains only items of type %s. Attempted to remove a %s' % (
                    attr.strip('_'), validType.__name__, type(val).__name__))
        except:
            raise AutomataError(
                'Attempted to remove a non-existant item from %s.' % attr.strip('_'))
    return remItemMethod

# High-level automata usage


def renderMachine(fa, outfile='temp.png', format='png', size=None):
    gvcode = fa.toGraphViz(size)

    f = popen(r'dot -T%s -o"%s"' % (format, outfile), 'w')
    try:
        f.write(gvcode)
    except:
        raise
    finally:
        f.close()


def loadMachine(filename):
    f = open(filename)
    try:
        s = f.read()
        fsm = unserialize(s)
    finally:
        f.close()

    return fsm


def saveMachine(fsm, filename):
    f = open(filename, 'w')
    try:
        s = serialize(fsm)
        f.write(s)
    finally:
        f.close()

# Label arrangement - quick hack


def arrangeLabel(string):
    pieces = string.split()
    count = len(pieces)
    delta = sqrt(count)
    cur = 1
    anchor = 0
    out = ''

    while anchor < count / 2:
        out += ' '.join(pieces[int(anchor):int(anchor+cur)]) + '\\n'
        anchor += cur

        cur += delta

    cur -= delta
    count -= anchor
    while count > 0:
        out += ' '.join(pieces[int(anchor):int(anchor+cur)]) + '\\n'
        anchor += cur
        count -= cur

        cur = (cur - delta) if (cur - delta) > 0 else 1

    out = out.strip().replace('\\n\\n', '\\n').replace('\\n\\n', '\\n')

    while out.startswith('\\n'):
        out = out[2:]

    while out.endswith('\\n'):
        out = out[:-2]

    return out
