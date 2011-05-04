from automata import *

class MetaNode(object):
  def __init__(self, label='', sourceNodes=()):
    self._node = Node(label)

    self._setLabel(label)

    self._sourceNodes = set()
    for n in sourceNodes:
      self.addSourceNode(n)

  def _setLabel(self, val):
    if type(val) is str:
      self._label = val
      self._node.label = val
    else:
      raise AutomataError, 'label must be a str, not %s.' % type(val).__name__
  _getLabel = genGetMethod('_label')
  label   = property(_getLabel, _setLabel)

  _getSourceNodes = genCollGetMethod('_sourceNodes')
  _setSourceNodes = genCollSetMethod('_sourceNodes', Node)
  addSourceNode = genAddMethod('_sourceNodes', Node)
  remSourceNode = genRemMethod('_sourceNodes', Node)
  sourceNodes = property(_getSourceNodes, _setSourceNodes)

  def _getNode(self):
    return self._node
  node = property(_getNode)

  def __repr__(self):
    if len(self._sourceNodes):
      return '<MetaNode "%s" aka {%s}>' % (self._label, ','.join([i.label for i in self._sourceNodes]))
    else:
      return '<MetaNode "%s">' % self._label


def nfa2dfa(nfa, minimize=False, rename=False):
  def lookupNode(nodes, sources):
    for i in nodes:
      if set(i.sourceNodes) == sources:
        return i
    return None

  if not nfa.isValid():
    raise AutomataError, 'NFA is not in a valid state.'

  #Initialize
  dfa = DFA()
  dfa.charset = nfa.charset
  pending = []
  done = []

  #Create a starting node
  closure = nfa.apply('', set([nfa.start]))
  if rename:
    label = 'q%d' % len(dfa.nodes)
  else:
    label = '{%s}' % ', '.join([i.label for i in closure])
  pending.append(MetaNode(label = label, sourceNodes = closure))
  dfa.addNode(pending[0].node)
  dfa.start = pending[0].node

  #Create other nodes
  while len(pending):
    for c in dfa.charset:
      curState = pending[0]
      nextStates = nfa.apply([c], set(curState.sourceNodes))
      s = lookupNode(pending + done, nextStates)

      if s is None:
        if rename:
          label = 'q%d' % len(dfa.nodes)
        else:
          label = '{%s}' % ', '.join([i.label for i in nextStates])
        pending.append(MetaNode(label = label, sourceNodes = nextStates))
        dfa.addNode(pending[-1].node)
        s = pending[-1]

      dfa.addDelta(curState.node, c, s.node)

    done.append(pending.pop(0))

  #Set terminal nodes
  for n in done:
    if set(n.sourceNodes).intersection(nfa.terminals):
      dfa.addTerminal(n.node)

  #Check for lambda-acceptance
  if nfa.execute(''):
    dfa.addTerminal(dfa.start)

  if minimize:
    dfa.minimize()

  return dfa
