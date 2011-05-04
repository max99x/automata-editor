from util import AutomataError, arrangeLabel
from base import *
from copy import deepcopy as copy
from StringIO import StringIO

class DFA(AutomataBase):
  def __init__(self, charset=(), nodes=(), start=None, terminals=()):
    AutomataBase.__init__(self, charset, nodes, start, terminals)

    self._deltas = {}

  def getDelta(self, node):
    if type(node) is Node:
      if self._deltas.has_key(node):
        return self._deltas[node]
      else:
        return {}
    else:
      raise AutomataError, 'Delta source must be a Node, not %s' % type(node).__name__

  def addDelta(self, node, input, dest):
    if input not in self._charset:
      raise AutomataError, '%s not in charset.' % input

    if type(node) is Node and type(dest) is Node:
      if self._deltas.has_key(node):
        self._deltas[node][input] = dest
      else:
        self._deltas[node] = {input: dest}
    else:
      raise AutomataError, 'Delta source and destination must be Nodes.'

  def remDelta(self, node, input):
    if input not in self._charset:
      raise AutomataError, '%s not in charset.' % input

    if type(node) is Node:
      if self._deltas.has_key(node) and self._deltas[node].has_key(input):
        self._deltas[node].pop(input)
        if len(self._deltas[node]) == 0:
          del self._deltas[node]
    else:
      raise AutomataError, 'Delta source must be a Node, not %s' % type(node).__name__

  def isValid(self):
    if len(self._charset) == 0:
      return False
    if len(self._nodes) == 0:
      return False
    if self._start not in self._nodes:
      return False

    for i in self._terminals:
      if i not in self._nodes:
        return False

    if set(self._deltas.keys()) != self._nodes:
      return False
    else:
      charCount = len(self._charset)
      for key in self._deltas:
        if len(self._deltas[key]) != charCount:
          return False

    return True

  def minimize(self):
    #NOTE: Algorithm not optimal (and messy). Should be refactored later.

    if not self.isValid():
      raise AutomataError, 'Machine is not in a valid state.'

    nodes = sorted(list(self._nodes), key=Node._getLabel)
    count = len(nodes)
    table = [[False for j in range(count)] for i in range(count)]
    unresolved = 0

    #Initial Table
    for i in range(1, count):
      for j in range(i):
        if len(set([nodes[i], nodes[j]]).intersection(self._terminals)) == 1:
          table[i][j] = True
        else:
          unresolved += 1
          table[i][j] = []
          for char in self._charset:
            m = nodes.index(self.apply([char], nodes[i]))
            n = nodes.index(self.apply([char], nodes[j]))

            if n > m:
              t = n
              n = m
              m = t

            if m != n: table[i][j].append((m, n))

    #Resolve all unresolved table cells
    while unresolved > 0:
      for i in range(1, count):
        for j in range(0, i):
          if table[i][j] == []:
            table[i][j] = False
            unresolved -= 1
          elif type(table[i][j]) is list:
            for c in range(len(table[i][j])):
              if c > len(table[i][j]) - 1: #ugly patch
                break

              m = table[i][j][c][0]
              n = table[i][j][c][1]
              if table[m][n] is True:
                table[i][j] = True
                unresolved -= 1
                break
              elif table[m][n] is False or table[m][n] == []:
                table[i][j].pop(c)
              elif type(table[m][n]) is list:
                table[i][j].pop(c)
                table[i][j] += table[m][n]

    #Remove equivalent states
    for i in range(1, count):
      for j in range(0, i):
        if table[i][j] == False:
          if self._start == nodes[i]:
            t = j
            j = i
            i = t

          if nodes[i] in self._nodes:
            self._nodes.remove(nodes[i])
            del self._deltas[nodes[i]]

            if nodes[i] in self._terminals:
              self._terminals.remove(nodes[i])

          for src in self._deltas:
            for char in self._deltas[src]:
              if self._deltas[src][char] == nodes[i]:
                self._deltas[src][char] = nodes[j]

    return table

  def apply(self, input, start):
    if not self.isValid():
      raise AutomataError, 'Machine is not in a valid state.'

    curState = start
    while len(input):
      curSymbol = input[0]
      input = input[1:]

      if curSymbol not in self._charset:
        raise AutomataError, 'Invalid symbol in input: %s.' % curSymbol

      curState = self._deltas[curState][curSymbol]

    return curState

  def execute(self, input, start=None):
    state = self.apply(input, start or self._start)

    if state in self._terminals:
      return True
    else:
      return False

  def toGraphViz(self, size=None):
    if not self.isValid():
      raise AutomataError, 'Machine is not in a valid state.'
    if size and type(size) is not tuple:
      raise AutomataError, 'Size must be a tuple of x,y.'

    nodes = list(self._nodes)
    start = nodes.index(self._start)

    out = StringIO()

    out.write('digraph DFA {\n')
    out.write('   rankdir = LR;\n')
    out.write('   root = %s;\n' % start)
    if size:
      out.write('   size = "%s,%s";\n' % size)
    out.write('\n')

    out.write('   node [shape = circle fontname = "Lucida Console"];\n')
    out.write('   edge [fontname = "Lucida Console" arrowhead=vee];\n')
    out.write('\n')

    for i in range(len(nodes)):
      if nodes[i] in self._terminals:
        out.write('   %d [shape = doublecircle label ="%s"];\n' % (i, arrangeLabel(nodes[i].label)))
      else:
        out.write('   %d [label = "%s"];\n' % (i, arrangeLabel(nodes[i].label)))
    out.write('\n')

    out.write('   "" [style = invis width = 0 height = 0];\n')
    out.write('\n')

    out.write('   "" -> %d [arrowsize = 1.5 penwidth = 0];\n' % start)
    out.write('\n')

    for nodeFrom in self._deltas:
      for char in self._deltas[nodeFrom]:
        src = nodes.index(nodeFrom)
        nodeTo = self._deltas[nodeFrom][char]
        dest = nodes.index(nodeTo)
        if (nodeFrom in self._terminals and nodeFrom != self._start) or nodeTo == self._start:
          out.write('   %d -> %d [label = "%s" constraint = false];\n' % (src, dest, char))
        else:
          out.write('   %d -> %d [label = "%s"];\n' % (src, dest, char))
    out.write('\n')

    out.write('}\n')

    return out.getvalue()

  def __repr__(self):
    ret  = '<DFA>\n'
    ret += '  Charset: {%s}\n' % ','.join(self._charset)
    ret += '  Nodes: {%s}\n' % ','.join([i.label for i in self._nodes])
    ret += 'Terminals: {%s}\n' % ','.join([i.label for i in self._terminals])
    ret += '  Start: %s\n' % (self._start and self._start.label)
    ret += '  Delta: '
    if len(self._deltas):
      for qFrom in self._deltas:
        for input in self._deltas[qFrom]:
          ret += 'D(%s, %s) -> %s\n       ' % (qFrom.label, input, self._deltas[qFrom][input].label)
      ret = ret.rstrip() + '\n'
    else:
      ret += 'None\n'
    ret += '  Valid: %s\n' % ('Yes' if self.isValid() else 'No')
    ret += '</DFA>'

    return ret


class NFA(AutomataBase):
  def __init__(self, charset=(), nodes=(), start=None, terminals=()):
    AutomataBase.__init__(self, charset, nodes, start, terminals)

    self._deltas = {}

    self._charset = set([''])

  def _getCharset(self):
    temp = copy(self._charset)
    temp.remove('')
    return tuple(temp)

  def _setCharset(self, val):
    AutomataBase._setCharset(self, val)
    self._charset.add('')

  charset   = property(_getCharset, _setCharset)

  def getDelta(self, node):
    if type(node) is Node:
      if self._deltas.has_key(node):
        return self._deltas[node]
      else:
        return {}
    else:
      raise AutomataError, 'Delta source must be a Node, not %s' % type(node).__name__

  def addDelta(self, node, input, dest):
    if input not in self._charset:
      raise AutomataError, '%s not in charset.' % input

    if type(node) is Node:
      if type(dest) is set and all([type(i) is Node for i in dest]):
        if len(dest):
          if node in self._deltas:
            if input in self._deltas[node]:
              self._deltas[node][input] = self._deltas[node][input].union(dest)
            else:
              self._deltas[node][input] = dest
          else:
            self._deltas[node] = {input: dest}
      elif type(dest) is Node:
        if self._deltas.has_key(node):
          if self._deltas[node].has_key(input):
            self._deltas[node][input].add(dest)
          else:
            self._deltas[node][input] = set([dest])
        else:
          self._deltas[node] = {input: set([dest])}
      else:
        raise AutomataError, 'Delta destination must be a Node or a set of nodes, not %s.' % type(dest).__name__
    else:
      raise AutomataError, 'Delta source must be Node, not %s.' % type(node).__name__

  def remDelta(self, node, input):
    if input not in self._charset:
      raise AutomataError, '%s not in charset.' % input

    if type(node) is Node:
      if self._deltas.has_key(node) and self._deltas[node].has_key(input):
        self._deltas[node].pop(input)
        if len(self._deltas[node]) == 0:
          del self._deltas[node]
    else:
      raise AutomataError, 'Delta source must be a Node, not %s' % type(node).__name__

  def isValid(self):
    if len(self._nodes) == 0:
      return False
    if self._start not in self._nodes:
      return False

    for i in self._terminals:
      if i not in self._nodes:
        return False

    if not set(self._deltas.keys()).issubset(self._nodes):
      return False

    for key in self._deltas:
      for char in self._deltas[key]:
        if char not in self._charset:
          return False

    return True

  def apply(self, input, start):
    if not self.isValid():
      raise AutomataError, 'Machine is not in a valid state.'
    if not (type(start) is set and all([type(i) is Node for i in start])):
      raise AutomataError, 'NFA execution must start from a set of states.'

    if len(start) == 0:
      return set()

    curStates = start
    input += '\x00' #Extra lambda transition

    while len(input): #For each symbol
      #Apply lambda transitions
      lastCount = 0

      while len(curStates) != lastCount:
        lastCount = len(curStates)
        for state in tuple(curStates): #copy, curState modified in the loop
          if self._deltas.has_key(state) and self._deltas[state].has_key(''):
            curStates = curStates.union(self._deltas[state][''])

      #Load symbol
      nextStates = set()
      curSymbol = input[0]
      input = input[1:]

      #Parse symbol
      if curSymbol != '\x00':
        if curSymbol not in self._charset:
          raise AutomataError, 'Invalid symbol in input: %s.' % curSymbol
        for state in curStates:
          if self._deltas.has_key(state) and self._deltas[state].has_key(curSymbol):
            nextStates = nextStates.union(self._deltas[state][curSymbol])

        curStates = nextStates

    return curStates

  def execute(self, input, start=None):
    if type(start) is set:
      states = self.apply(input, start)
    else:
      states = self.apply(input, set([start or self._start]))

    if states.intersection(self._terminals):
      return True
    else:
      return False

  def toGraphViz(self, size=None):
    if not self.isValid():
      raise AutomataError, 'Machine is not in a valid state.'
    if size and type(size) is not tuple:
      raise AutomataError, 'Size must be a tuple of x,y.'

    nodes = list(self._nodes)
    start = nodes.index(self._start)

    out = StringIO()

    out.write('digraph NFA {\n')
    out.write('   rankdir = LR;\n')
    out.write('   root = %s;\n' % start)
    if size:
      out.write('   size = "%s,%s";\n' % size)
    out.write('\n')

    out.write('   node [shape = circle fontname = "Lucida Console"];\n')
    out.write('   edge [fontname = "Lucida Console" arrowhead = vee];\n')
    out.write('\n')

    for i in range(len(nodes)):
      if nodes[i] in self._terminals:
        out.write('   %d [shape = doublecircle label ="%s"];\n' % (i, nodes[i].label))
      else:
        out.write('   %d [label = "%s"];\n' % (i, nodes[i].label))
    out.write('\n')

    out.write('   "" [style = invis width = 0 height = 0];\n')
    out.write('\n')

    out.write('   "" -> %d [arrowsize = 1.5 penwidth = 0];\n' % start)
    out.write('\n')

    for nodeFrom in self._deltas:
      for char in self._deltas[nodeFrom]:
        for nodeTo in self._deltas[nodeFrom][char]:
          src = nodes.index(nodeFrom)
          dest = nodes.index(nodeTo)
          char = char or u'\u03bb'.encode('utf8') #Lambda
          if (nodeFrom in self._terminals and nodeFrom != self._start) or nodeTo == self._start:
            out.write('   %d -> %d [label = "%s" constraint = false];\n' % (src, dest, char))
          else:
            out.write('   %d -> %d [label = "%s"];\n' % (src, dest, char))
    out.write('\n')

    out.write('}\n')

    return out.getvalue()

  def __repr__(self):
    ret  = '<NFA>\n'
    ret += '  Charset: {%s}\n' % ','.join(filter(None, self._charset))
    ret += '  Nodes: {%s}\n' % ','.join([i.label for i in self._nodes])
    ret += 'Terminals: {%s}\n' % ','.join([i.label for i in self._terminals])
    ret += '  Start: %s\n' % (self._start and self._start.label)
    ret += '  Delta: '
    if len(self._deltas):
      for qFrom in self._deltas:
        for input in self._deltas[qFrom]:
          ret += 'D(%s, %s) -> {%s}\n       ' % (qFrom.label, input or 'lambda', ','.join([i.label for i in self._deltas[qFrom][input]]))
      ret = ret.rstrip() + '\n'
    else:
      ret += 'None\n'
    ret += '  Valid: %s\n' % ('Yes' if self.isValid() else 'No')
    ret += '</NFA>'

    return ret
