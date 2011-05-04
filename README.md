# Automata Editor

Automata Editor is a simple toolkit for working with deterministic and
non-deterministic finite automata, as well as (classic) regular expressions.

Screenshots available at:
  http://max99x.com/school/automata-editor

## Features

* Create and edit DFA and NFA, programmatically or using a (crude) GUI.
* Convert from NFA to DFA.
* Optimize DFA to the minimum number of states.
* Evaluate automata on sample strings.
* Convert from (classic) regular expressions to automata.
* Construct the equivalent regular expression from any NFA.
* Save and load automata definitions and graphs.
* View the created automata as a graph in real time as you edit.

## Usage

If you're using the Windows binary distribution, run Automata Editor.exe. If
you're using the source distribution, you can run gui.pyw to access the GUI or
import any of the modules in Python to access the interface programmatically.
There are no documents detailing the interface right now, but it's fairly simple
so a skim through the source should be enough to get started.

For graph drawing to work, the `dot` program from GraphViz must be in your path.

Sample machines and regexes can be found in the samples folder. The regex
language used is the classic one, whose special characters are limited to the
Kleene star (`*`) for matching zero or more characters, the alternation (`+`)
for matching either everything on the left side or everything on the right side,
and parentheses (`(` and `)`) for grouping and limiting alterations.

## Implementation

The program is written in Python 2, using TkInter for the interface and Graphviz
for drawing graphs. Graphviz is called directly as a separate process, rather
than using a wrapper library, a choice that may not have been the best, in
retrospect.

## Requirements

The compiled Windows distribution is standalone. The source distribtuion
requires:

* Python 2.x
* The Python Imaging Library
* Graphviz
* If you want to build it on Windows using build.py, you will also need py2exe.

## License

This code is licensed under the MIT license.
