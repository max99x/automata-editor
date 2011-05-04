from util import AutomataError
from automata import NFA
from base import Node
from copy import copy, deepcopy
from os.path  import commonprefix

DEBUG  = False

LAMBDA = u'\u03bb'
PHI = u'\u00d8'

def copyDeltas(src):
  out = dict()
  for k in src:
    out[k] = dict()
    for k2 in src[k]:
      out[k][k2] = copy(src[k][k2])

  return out

def replaceNode(nfa, old, new):
  if DEBUG: print 'R_Start(%s, %s) ---' % (old, new), nfa
  if old in nfa._deltas:
    for input in nfa._deltas[old]:
      nfa.addDelta(new, input, nfa._deltas[old][input])
    del nfa._deltas[old]
  if DEBUG: print 'R_SwitchedSource(%s, %s) ---' % (old, new), nfa

  deltas_temp = copyDeltas(nfa._deltas)
  for src in deltas_temp:
    for input in deltas_temp[src]:
      if old in deltas_temp[src][input]:
        nfa._deltas[src][input].remove(old)
        nfa._deltas[src][input].add(new)
  if DEBUG: print 'R_SwitchedDest(%s, %s) ---' % (old, new), nfa

def commonsuffix(seq):
  def reverse(s):
    out = ''
    for c in reversed(s):
      out += c
    return out

  seq = [reverse(i) for i in seq]
  return reverse(commonprefix(seq))

class NetworkNFA(NFA):
  def __init__(self, nfa):
    if type(nfa) is not NFA:
      raise AutomataError, 'Can create a NetworkNFA only from an NFA.'

    if all([len(i) == 1 for i in nfa.charset]):
      self._charset   = copy(nfa._charset)
    else:
      self._charset = set(['{%s}' % i for i in nfa._charset])

    self._nodes   = copy(nfa._nodes)
    self._deltas  = copyDeltas(nfa._deltas)
    self._start   = nfa._start
    self._terminals = copy(nfa._terminals)

  def addDelta(self, node, input, dest):
    if set(input) - (self._charset.union(set('()+*'))):
      raise AutomataError, '%s contains symbols not in charset.' % input

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
    if set(input) - (self._charset.union(set('()+*'))):
      raise AutomataError, '%s contains symbols not in charset.' % input

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
        if set(char) - (self._charset.union(set('()+*'))):
          return False

    return True

  def apply(self, input, start):
    raise AutomataError, 'NetworkNFA does not allow direct application.'

  def __repr__(self):
    ret  = '<NetworkNFA>\n'
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
    ret += '</NetworkNFA>'

    return ret


def nfa2regex(nfa):
  if not nfa.isValid():
    raise AutomataError, 'NFA must be in a valid state to be converted to a regex.'

  network = NetworkNFA(nfa)

  if DEBUG: print 'START', network

##  #Take care of multi-terminals
##  if len(network.terminals) > 1:
##    end = Node('qf')
##    network.addNode(end)
##    for i in copy(network.terminals):
##      network.addDelta(i, '', end)
##      network.remTerminal(i)
##    network.addTerminal(end)

  #Add a dummy start and end nodes
  start = Node('qs')
  network.addNode(start)
  network.addDelta(start, '', network.start)
  network.start = start

  end = Node('qf')
  network.addNode(end)
  for i in network.terminals:
    network.addDelta(i, '', end)
    network.remTerminal(i)
  network.addTerminal(end)
  if DEBUG: print 'Dummies added: ', network

  #Collapse connections
  for src in network.nodes:
    delta_temp = network.getDelta(src)
    for dest in network.nodes:
      chars = []
      for input in delta_temp:
        if input and dest in delta_temp[input]:
          chars.append(input)

      if len(chars):
        for c in chars:
          delta_temp[c].remove(dest)
          if len(delta_temp[c]) == 0:
            del delta_temp[c]

        if len(chars) > 1:
          chars = '(' + '+'.join(chars) + ')'
        else:
          chars = '+'.join(chars)
        network.addDelta(src, chars, dest)
  if DEBUG: print 'Collapsed: ', network

  #Collect pliable nodes
  pliableNodes = list(network.nodes)
  pliableNodes.remove(network.start)
  for n in network.terminals:
    pliableNodes.remove(n)

  #Build a distance-from-terminal table
  nodeFinalDist = {}
  maxDist = len(network.nodes) ** len(network.nodes) #Lazy
  for n in network.nodes:
    nodeFinalDist[n] = maxDist

  nodeFinalDist[network.terminals[0]] = 0
  toProcess = list(network.nodes)
  toProcess.remove(network.terminals[0])

  while len(toProcess):
    for node in toProcess:
      dests = network.getDelta(node).values()
      if len(dests) == 0:
        dests = set([])
      else:
        dests = reduce(set.union, network.getDelta(node).values())

      if len(dests) == 0:
        toProcess.remove(node)
      else:
        minDist = min([nodeFinalDist[i] for i in dests])
        if minDist != maxDist:
          nodeFinalDist[node] = minDist + 1
          toProcess.remove(node)


  #Sort pliable nodes by distance from terminal
  pliableNodes.sort(key=lambda x: nodeFinalDist[x], reverse=True)
  if DEBUG: print 'Pliables: ', pliableNodes

  for node in pliableNodes:
    #Remove Node
    network.remNode(node)

    #Save delta
    delta = copy(network.getDelta(node))

    #Convert loops to regex
    loops = []
    for input in delta:
      if node in delta[input]:
        if len(input):
          loops.append(input)
    loopRegex = '+'.join(loops)
    if len(loopRegex) > 1 and not (loopRegex[0] == '(' and loopRegex[-1] == ')'):
      loopRegex = '(' + loopRegex + ')*'
    elif len(loopRegex) >= 1:
      loopRegex = loopRegex + '*'

    #Remove loops
    for input in copy(delta):
      if delta[input] == set([node]):
        del delta[input]
      elif node in delta[input]:
        delta[input].remove(node)

    #Search lambda-closure equivalence
    if '' in delta and (len(delta) != 1 or len(delta['']) != 1):
      eligible = []
      for dest in delta['']:
        delta_temp = network.getDelta(dest)
        if '' in delta_temp and node in delta_temp['']:
          eligible.append(dest)

      if len(eligible):
        replaceNode(network, node, eligible[0])
        continue

    #Remove delta
    try:
      del network._deltas[node]
    except KeyError: #No deltas remaining, had only loops
      continue

    if DEBUG: print 'Working on connections: ', node, delta
    #Check all possible connections through this node
    deltas_temp = copyDeltas(network._deltas)
    for src in deltas_temp:
      for input in deltas_temp[src]:
        tempDeltaDest = network.getDelta(src)[input]
        if node in tempDeltaDest:
          tempDeltaDest.remove(node)
          if len(tempDeltaDest) == 0:
            network.remDelta(src, input)

          for input2 in delta:
            for dest in delta[input2]:
              if not (src == dest and (input + loopRegex + input2) == ''):
                network.addDelta(src, input + loopRegex + input2, dest)
                if DEBUG: print 'New Delta:', src, input, loopRegex, input2, dest, network

  #Extract common prefix/suffix
  branches = network.getDelta(network.start).keys()
  if len(branches) == 1:
    regex = branches[0]
  else:
    prefix = commonprefix(branches)
    suffix = commonsuffix(branches)
    branches = [i[len(prefix):-len(suffix)] if len(suffix) else i[len(prefix):]
          for i in branches]
    branches.sort(key=len)
    if len(prefix) or len(suffix):
      regex = prefix + '(' + '+'.join([i or LAMBDA for i in branches]) + ')' + suffix
    else:
      regex = '+'.join([i or LAMBDA for i in branches]) or PHI

  return regex
