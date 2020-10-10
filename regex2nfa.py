from automata import *
import re
import random


def validate(regex, fsm, num=2, *tests):
    def gen_string(length, charset):
        return ''.join([random.choice(charset) for i in range(length)])

    regex = '^(' + regex.replace('+', '|') + ')$'
    regex = re.compile(regex)

    if not tests:
        tests = []
        for i in range(1, 10)*num:
            tests.append(gen_string(i, fsm.charset))

    for t in tests:
        if bool(regex.match(t)) != fsm.execute(t):
            if regex.match(t):
                print('%10s\tRegex Only' % t)
            else:
                print('%10s\tMachine Only' % t)
        else:
            if fsm.execute(t):
                print('%10s\tOK\tMatched' % t)
            else:
                print('%10s\tOK\tNot Matched' % t)


def regex2nfa(regex, rename=False, cleanup=True):
    stack = []
    sigma = set(regex) - set(['(', ')', '*', '+'])
    start = Node('q0')

    nfa = NFA()
    nfa.addNode(start)
    nfa.start = start
    nfa.charset = sigma

    last = Node('q1')
    nfa.addNode(last)
    nfa.addDelta(start, '', last)

    skipNext = False
    orphans = []
    branches = [[]]  # 0 -> Dummy

    for i in range(len(regex)):
        if skipNext:
            skipNext = False
            continue

        char = regex[i]
        nextChar = regex[i+1] if len(regex) - i > 1 else None
        lastChar = regex[i-1] if i > 0 else None

        if char in sigma:
            if nextChar is '*':
                nfa.addDelta(last, char, last)

                cur = Node('s%d' % len(nfa.nodes))
                nfa.addNode(cur)
                nfa.addDelta(last, '', cur)

                last = cur

                skipNext = True
            else:
                cur = Node('c%d' % len(nfa.nodes))
                nfa.addNode(cur)
                nfa.addDelta(last, char, cur)

                last = cur
        elif char is '(':
            cur = Node('<%d' % len(nfa.nodes))
            nfa.addNode(cur)
            nfa.addDelta(last, '', cur)
            stack.append(cur)
            branches.append([])

            last = cur
        elif char is ')':
            if branches[len(stack)]:
                cur = Node('>%d' % len(nfa.nodes))
                nfa.addNode(cur)
                for node in branches[len(stack)] + [last]:
                    nfa.addDelta(node, '', cur)

                last = cur
                branches.pop()

            if nextChar is '*':
                nfa.addDelta(last, '', stack[-1])
                nfa.addDelta(stack[-1], '', last)

                skipNext = True

            stack.pop()
        elif char is '*':
            raise AutomataError('Orphaned star found.')
        elif char is '+':
            if len(stack) is 0:  # Main branch
                orphans.append(last)

                last = Node('b%d' % len(nfa.nodes))
                nfa.addNode(last)
                nfa.addDelta(start, '', last)

            else:
                branches[len(stack)].append(last)
                last = stack[-1]

    # Connect main branches
    for node in orphans:
        nfa.addDelta(node, '', last)

    # Clean up lambdas
    if cleanup:
        nodeList = nfa.nodes
        for node in nodeList:
            if nfa.getDelta(node).keys() == [''] and len(nfa.getDelta(node)['']) == 1 and node not in nfa.terminals:
                # Useless node, equiv. to next
                next = list(nfa.getDelta(node)[''])[0]
                nfa.remNode(node)
                nfa.remDelta(node, '')

                if nfa.start == node:
                    nfa.start = next

                for src in nfa.nodes:
                    delta = nfa.getDelta(src)
                    for char in delta:
                        dest = delta[char]
                        if node in dest:
                            dest.remove(node)
                            dest.add(next)

    if rename:
        count = 0
        for i in nfa.nodes:
            i.label = 'q%d' % count
            count += 1

    nfa.addTerminal(last)

    return nfa
