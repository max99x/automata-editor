#!/usr/bin/python2

################################################################
#                          LIBRARIES                           #
################################################################

from copy import deepcopy as copy

import Tkinter as tk

from base import Node
from automata import NFA, DFA
from nfa2dfa import nfa2dfa
from regex2nfa import regex2nfa
from nfa2regex import nfa2regex, DEBUG
from util import saveMachine, loadMachine, renderMachine

from dialogs import *
from preview import PreviewWindow

################################################################
#                          MAIN WINDOW                         #
################################################################

class Application(object):
  WIDTH  = 750
  HEIGHT = 365
  TITLE  = 'Automata Editor'

  def __init__(self):
    #Set Main Automata
    self.fsm = NFA()
    self.deltasCache = []

    #Configure Main Window
    self.root = tk.Tk()
    self.root.title(self.TITLE)
    self.root.resizable(True, False)

    screen_w = self.root.winfo_screenwidth()
    screen_h = self.root.winfo_screenheight()

    x = (screen_w - self.WIDTH) / 2
    y = screen_h / 2 - (screen_h - self.HEIGHT) / 2

    self.root.geometry('%dx%d+%d+%d' % (self.WIDTH, self.HEIGHT, x, y))

    #Configure grid
    for i in range(1,10):
      self.root.grid_rowconfigure(i, pad=8)

    for i in range(1,8):
      self.root.grid_columnconfigure(i, pad=10)

    self.root.grid_columnconfigure(4, weight=2)
    self.root.configure(padx=10)

    self.root.propagate(True)

    #Create Widgets
    self.lblChars = tk.Label(self.root, text='Symbols:')
    self.lblNodes = tk.Label(self.root, text='States:')
    self.lblStart = tk.Label(self.root, text='Initial:')
    self.lblFinal = tk.Label(self.root, text='Finals:')
    self.lblDelta = tk.Label(self.root, text='Delta:')
    self.lblType  = tk.Label(self.root, text='Type:')
    self.lblValid = tk.Label(self.root, text='Valid:')

    self.entChars = tk.Label(self.root)
    self.entNodes = tk.Label(self.root)
    self.entStart = tk.Label(self.root)
    self.entFinal = tk.Label(self.root)
    self.entType  = tk.Label(self.root)
    self.entValid = tk.Label(self.root)

    self.btnAddChar  = tk.Button(self.root, text='Add Symbol', command=self.addChar)
    self.btnRemChar  = tk.Button(self.root, text='Remove Symbol', command=self.remChar)
    self.btnAddNode  = tk.Button(self.root, text='Add State', command=self.addNode)
    self.btnRemNode  = tk.Button(self.root, text='Remove State', command=self.remNode)
    self.btnSetStart = tk.Button(self.root, text='Set Initial', command=self.setStart)
    self.btnSetFinal = tk.Button(self.root, text='Set Finals', command=self.setFinal)
    self.btnAddDelta = tk.Button(self.root, text='Add Delta', command=self.addDelta)
    self.btnRemDelta = tk.Button(self.root, text='Remove Delta', command=self.remDelta)
    self.btnReset    = tk.Button(self.root, text='New Machine', command=self.reset)
    self.btnSave     = tk.Button(self.root, text='Save Machine', command=self.save)
    self.btnLoad     = tk.Button(self.root, text='Load Machine', command=self.load)
    self.btnConvert  = tk.Button(self.root, text='Determinize', command=self.convert)
    self.btnMinimize = tk.Button(self.root, text='Minimize', command=self.minimize)
    self.btnApply    = tk.Button(self.root, text='Parse String', command=self.apply)
    self.btnExtract  = tk.Button(self.root, text='Construct Regex', command=self.extract)
    self.btnBuild    = tk.Button(self.root, text='Parse Regex', command=self.build)
    self.btnRender   = tk.Button(self.root, text='Render to File', command=self.render)

    #Deltas Listbox/Scroll configuration
    self.lstDeltas   = tk.Listbox(self.root)
    self.lstDeltas.scroll = tk.Scrollbar(self.lstDeltas, command = self.lstDeltas.yview)
    self.lstDeltas.scroll.pack(side = 'right', fill = 'y')
    self.lstDeltas.configure(yscrollcommand = self.lstDeltas.scroll.set, selectmode=tk.EXTENDED)
    self.root.bind('<MouseWheel>', lambda e: self.lstDeltas.yview(
        tk.SCROLL, -1*(1 if e.delta>0 else -1), tk.UNITS))

    #Place Widgets
    self.lblChars.grid(column=1, row=1, sticky=tk.E)
    self.lblNodes.grid(column=1, row=2, sticky=tk.E)
    self.lblStart.grid(column=1, row=3, sticky=tk.E)
    self.lblFinal.grid(column=3, row=3, sticky=tk.E)
    self.lblDelta.grid(column=1, row=5, sticky=tk.W)
    self.lblType.grid( column=6, row=10, sticky=tk.W)
    self.lblValid.grid(column=7, row=10, sticky=tk.W)

    self.entChars.grid(column=2, row=1, sticky=tk.W, columnspan=3)
    self.entNodes.grid(column=2, row=2, sticky=tk.W, columnspan=3)
    self.entStart.grid(column=2, row=3, sticky=tk.W)
    self.entFinal.grid(column=4, row=3, sticky=tk.W)
    self.entType.grid( column=6, row=10, sticky=tk.E, padx=15)
    self.entValid.grid(column=7, row=10, sticky=tk.E, padx=25)

    self.btnAddChar.grid( column=6, row=1, sticky=tk.EW)
    self.btnRemChar.grid( column=7, row=1, sticky=tk.EW)
    self.btnAddNode.grid( column=6, row=2, sticky=tk.EW)
    self.btnRemNode.grid( column=7, row=2, sticky=tk.EW)
    self.btnSetStart.grid(column=6, row=3, sticky=tk.EW)
    self.btnSetFinal.grid(column=7, row=3, sticky=tk.EW)
    self.btnAddDelta.grid(column=4, row=5, sticky=tk.W, ipadx=10)
    self.btnRemDelta.grid(column=4, row=5, sticky=tk.E, ipadx=10)
    self.btnReset.grid(   column=6, row=5, sticky=tk.EW)
    self.btnSave.grid(    column=7, row=6, sticky=tk.EW)
    self.btnLoad.grid(    column=7, row=5, sticky=tk.EW)
    self.btnConvert.grid( column=6, row=7, sticky=tk.EW)
    self.btnMinimize.grid(column=7, row=7, sticky=tk.EW)
    self.btnApply.grid(   column=6, row=9, sticky=tk.EW, columnspan=2)
    self.btnExtract.grid( column=6, row=8, sticky=tk.EW)
    self.btnBuild.grid(   column=7, row=8, sticky=tk.EW)
    self.btnRender.grid(  column=6, row=6, sticky=tk.EW)

    self.lstDeltas.grid(column=1, row=6, sticky=tk.NSEW, columnspan=4, rowspan=5)

    #Create Dividers
    self.lblDivider1 = tk.Label(self.root)
    self.lblDivider2 = tk.Label(self.root, text='   ')
    self.lblDivider1.grid(column=1, row=4, sticky=tk.NSEW, columnspan=6)
    self.lblDivider2.grid(column=5, row=1, sticky=tk.NSEW, rowspan=8)

    #Create Preview
    self.preview = PreviewWindow(self.root, self.fsm, showrefresh=False)
    self.preview.reposition(y + self.HEIGHT + 28)

    #Run
    self.root.after(100, self.update)
    self.root.mainloop()

  def addChar(self):
    char = askForString(self.root, self.TITLE, 'Type in a symbol:')
    if char:
      self.fsm.addChar(char)
      self.update()

  def remChar(self):
    if len(self.fsm.charset):
      target = askForChoice(self.root, self.TITLE, 'Select a symbol:', self.fsm.charset)
      if target is not None:
        self.fsm.remChar(target)
        self.update()
    else:
      messageBox(self.root, self.TITLE, 'No symbols to remove.')

  def addNode(self):
    label = askForString(self.root, self.TITLE, 'Type in a label for the node:')
    if label:
      self.fsm.addNode(Node(label))
      self.update()

  def remNode(self):
    if len(self.fsm.nodes):
      target = askForChoice(self.root, self.TITLE, 'Select a state:', self.fsm.nodes)
      if target is not None:
        for src in self.fsm.nodes:
          delta = self.fsm.getDelta(src)
          keys = delta.keys() #copy
          for char in keys:
            if src == target:
              self.fsm.remDelta(src, char)
            elif type(self.fsm) is DFA and delta[char] == target:
              self.fsm.remDelta(src, char)
            elif type(self.fsm) is NFA and target in delta[char]:
              delta[char].discard(target)
              if len(delta[char]) == 0:
                del delta[char]

        self.fsm.remNode(target)

        if self.fsm.start == target:
          self.fsm._start = None

        self.update()
    else:
      messageBox(self.root, self.TITLE, 'No states to remove.')

  def setStart(self):
    if len(self.fsm.nodes):
      nodes = list(self.fsm.nodes)
      if self.fsm.start:
        selected = nodes.index(self.fsm.start)
      else:
        selected = 0
      target = askForChoice(self.root, self.TITLE, 'Select an initial state:', nodes, selected)
      if target is not None:
        self.fsm.start = target
        self.update()
    else:
      messageBox(self.root, self.TITLE, 'No states to select an initial from.')

  def setFinal(self):
    if len(self.fsm.nodes):
      nodes = sorted(self.fsm.nodes, key=lambda x:x.label)
      finals = [i for i in range(len(nodes)) if nodes[i] in self.fsm.terminals]
      targets = askForSelect(self.root, self.TITLE, 'Select final states:', nodes, finals)

      if targets:
        self.fsm.terminals = targets
        self.update()
    else:
      messageBox(self.root, self.TITLE, 'No states to select finals from.')

  def addDelta(self):
    if len(self.fsm.nodes):
      src = askForChoice(self.root, self.TITLE, 'Select a "from" state:', self.fsm.nodes)

      if src:
        if type(self.fsm) is DFA:
          allowedChars = list(set(self.fsm.charset).difference(self.fsm.getDelta(src).keys()))
        else:
          allowedChars = self.fsm.charset + (u'\u03bb',)

        if len(allowedChars) == 0:
          messageBox(self.root, self.TITLE, 'Selected state already has connections for all inputs.')
          return

        char = askForChoice(self.root, self.TITLE, 'Select an input symbol:', allowedChars)

        if char is None:
          return
        if char == u'\u03bb':
          char = ''

        dest = askForChoice(self.root, self.TITLE, 'Select a "to" state:', self.fsm.nodes)
        if dest is None:
          return

        self.fsm.addDelta(src, char, dest)

        self.update()
    else:
      messageBox(self.root, self.TITLE, 'No states to connect.')

  def remDelta(self):
    selected = [int(i) for i in self.lstDeltas.curselection()]
    for i in selected:
      (src, char, dest) = self.deltasCache[i]
      if type(self.fsm) is DFA:
        self.fsm.remDelta(src, char)
      else:
        delta = self.fsm.getDelta(src) #reference
        delta[char].discard(dest)
        if len(delta[char]) == 0:
          del delta[char]
    self.update()

  def reset(self):
    check = askYesNo(self.root, self.TITLE, 'Are you sure you want to create a new automata?\nAll unsaved work will be lost.')
    if check:
      self.fsm = NFA()
      self.update()

  def save(self):
    filename = askForSave(self.root, 'Select a filename...')
    if filename:
      try:
        saveMachine(self.fsm, filename)
      except:
        messageBox(self.root, self.TITLE, 'Could not save to selected file.')

  def load(self):
    filename = askForOpen(self.root, 'Select a machine...')
    if filename:
      try:
        temp_fsm = self.fsm
        self.fsm = loadMachine(filename)
      except:
        self.fsm = temp_fsm
        messageBox(self.root, self.TITLE, 'Could not load selected file.')
      self.update()

  def convert(self):
    if self.fsm.isValid():
      self.fsm = nfa2dfa(self.fsm)#, rename=True)
      self.update()
    else:
      messageBox(self.root, self.TITLE, 'Machine is incomplete.')

  def minimize(self):
    if self.fsm.isValid():
      self.fsm.minimize()
      self.update()
    else:
      messageBox(self.root, self.TITLE, 'Machine is incomplete.')

  def render(self):
    if self.fsm.isValid():
      filename = askForSave(self.root, 'Select a filename...', type=('PNG Image', '*.png'))
      if filename:
        try:
          renderMachine(self.fsm, filename)
        except:
          messageBox(self.root, self.TITLE, 'Could not render to selected file.')
    else:
      messageBox(self.root, self.TITLE, 'Machine is incomplete.')


  def apply(self):
    if self.fsm.isValid():
      string = askForString(self.root, self.TITLE, 'Enter string to parse:')

      if type(string) is str: #not None/False
        #Check if symbol set is valid multi-character strings
        breakString = False
        for c in self.fsm.charset:
          if len(c) > 1:
            breakString = True
            break

        if breakString and string.count(' ') and ' ' not in self.fsm.charset:
          string = string.split() #by whitespace
        elif breakString:
          #Break string
          string_orig = string
          symbols = sorted(self.fsm.charset, lambda x,y: len(y)-len(x))
          stringList = []

          while len(string) > 0:
            foundSymbol = False
            for s in symbols:
              if string.startswith(s):
                string = string[len(s):]
                stringList.append(s)
                foundSymbol = True
                break
            print string
            print stringList
            if not foundSymbol:
              errorString  = string_orig[:len(string_orig)-len(string)] + '  ' + string + '\n'
              errorString += ('_' * (len(string_orig)-len(string))) + '/' + (' ' * len(string))
              messageBox(self.root, self.TITLE, 'No symbol could be matched at:\n%s' % errorString)
              return
          string = stringList
        else:
          charset = self.fsm.charset
          for i in range(len(string)):
            if string[i] not in charset:
              errorString  = string[:i] + '  ' + string[i:] + '\n'
              errorString += ('_' * i) + '/' + (' ' * (len(string)-i))
              messageBox(self.root, self.TITLE, 'No symbol could be matched at:\n%s' % errorString)
              return

        result = self.fsm.execute(string)

        if result:
          messageBox(self.root, self.TITLE, 'String accepted.', icon='info')
        else:
          messageBox(self.root, self.TITLE, 'String rejected.')

        #Parse
    else:
      messageBox(self.root, self.TITLE, 'Machine is incomplete.')

  def build(self):
    string = askForString(self.root, self.TITLE, 'Enter regex to parse:')
    if string is not None:
      try:
        self.fsm = regex2nfa(string)
        self.update()
      except:
        messageBox(self.root, self.TITLE, 'Could not parse regex.')

  def extract(self):
    if self.fsm.isValid():
      if type(self.fsm) is NFA:
        try:
          regex = nfa2regex(self.fsm)
          messageBox(self.root, self.TITLE, 'The regex is:  ' + regex, icon='info')
        except:
          messageBox(self.root, self.TITLE, 'Could not construct regex.')
      else:
        messageBox(self.root, self.TITLE, 'Can only extract regex from NFAs.')
    else:
      messageBox(self.root, self.TITLE, 'Machine is incomplete.')

  def update(self):
    #Update type & validity
    if type(self.fsm) is DFA:
      self.entType['text'] = 'DFA'
      self.btnMinimize['state'] = 'normal'
      self.btnConvert['state'] = 'disabled'
      self.btnExtract['state'] = 'disabled'
    else:
      self.entType['text'] = 'NFA'
      self.btnMinimize['state'] = 'disabled'
      self.btnConvert['state'] = 'normal'
      self.btnExtract['state'] = 'normal'

    if self.fsm.isValid():
      self.entValid['text'] = 'Yes'
    else:
      self.entValid['text'] = 'No'

    #Update chars / symbols and nodes / states
    self.entChars['text'] = '{%s}' % ', '.join(self.fsm.charset)
    self.entNodes['text'] = '{%s}' % ', '.join([i.label for i in self.fsm.nodes])

    #Update initial / start and finals / terminals
    if self.fsm.start:
      self.entStart['text'] = self.fsm.start.label
    else:
      self.entStart['text'] = ''
    self.entFinal['text'] = '{%s}' % ', '.join([i.label for i in self.fsm.terminals])

    #Update deltas
    self.deltasCache = []
    self.lstDeltas.delete(0, tk.END)
    for src in sorted(self.fsm.nodes, key=lambda x: x.label):
      delta = self.fsm.getDelta(src)
      for char in sorted(delta.keys()):
        if type(self.fsm) is DFA:
          dests = [delta[char]]
        else:
          dests = sorted(delta[char], key=lambda x: x.label)

        for dest in dests:
          self.deltasCache.append((src,char,dest))
          string = u'(%s, %s) \u2192 %s' % (src.label, 
                                            char or u'\u03bb',
                                            dest.label)
          self.lstDeltas.insert(tk.END, string)

    #Update Preview
    try:
      self.preview._window.state() #If closed, error here
      self.preview.refresh(self.fsm)
    except:
      pass


################################################################
#                            START                             #
################################################################

if __name__ == '__main__':
  Application()
