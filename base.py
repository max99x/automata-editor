from util import *

class Node(object):
  def __init__(self, label=''):
    self._setLabel(label)

  _getLabel = genGetMethod('_label')
  _setLabel = genSetMethod('_label', str)
  label = property(_getLabel, _setLabel)

  def __repr__(self):
    return '<Node "%s">' % self._label


class AutomataBase(object):
  def __init__(self, charset=(), nodes=(), start=None, terminals=()):
    if start:
      self._setStart(start)
    else:
      self._start = None

    self._charset = set()
    for i in charset:
      self.addChar(i)

    self._nodes = set()
    for i in nodes:
      self.addNode(i)

    self._terminals = set()
    for i in terminals:
      self.addTerminal(i)

  _getStart = genGetMethod('_start')
  _setStart = genSetMethod('_start', Node)
  start = property(_getStart, _setStart)

  _getNodes = genCollGetMethod('_nodes')
  _setNodes = genCollSetMethod('_nodes', Node, set)
  addNode = genAddMethod('_nodes', Node)
  remNode = genRemMethod('_nodes', Node)
  nodes = property(_getNodes, _setNodes)

  _getCharset = genCollGetMethod('_charset')
  _setCharset = genCollSetMethod('_charset', str, set)
  addChar = genAddMethod('_charset', lambda x: type(x) is str and len(x) > 0)
  remChar = genRemMethod('_charset', str)
  charset = property(_getCharset, _setCharset)

  _getTerminals = genCollGetMethod('_terminals')
  _setTerminals = genCollSetMethod('_terminals', Node, set)
  addTerminal = genAddMethod('_terminals', Node)
  remTerminal = genRemMethod('_terminals', Node)
  terminals = property(_getTerminals, _setTerminals)

  def __repr__(self):
    ret = '<AutomataBase>\n'
    ret += '  Charset: {%s}\n' % ','.join(self._charset)
    ret += '  Nodes: {%s}\n' % ','.join([i.label for i in self._nodes])
    ret += 'Terminals: {%s}\n' % ','.join([i.label for i in self._terminals])
    ret += '  Start: %s\n' % (self._start and self._start.label)
    ret += '</AutomataBase>'
    return ret
