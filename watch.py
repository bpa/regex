#! /usr/bin/env python

import os, sys
import yaml
import regex
from termcolor import colored, RESET
from sortedcontainers import SortedDict
import pyinotify

ident = lambda x: x
bg_colors = ['on_blue','on_white']
colors = ['green','cyan','yellow','red']
class Watcher(pyinotify.ProcessEvent):
    def check(self, spec, match):
        if bool(match) ^ spec['match']:
            return False

        if not match:
            return True

        if spec.has_key('groups'):
            return match.groups() == tuple(spec['groups'])

        return True

    def color(self, text, match):
        boundaries = SortedDict(ident)
        boundaries[0] = [0, len(text), 0, None]
        
        def ins(start, end, bg):
            if boundaries.has_key(start):
                before = boundaries[start]
                if before[1] == end:
                    before[3] = bg
                else:
                    boundaries[end] = [end, before[1], before[2], before[3]]
                    before[1] = end
                    before[2] = before[2] + 1
            else:
                k = boundaries.bisect_key_right(start)
                key = boundaries.iloc[k-1]
                before = boundaries[key]
                boundaries.setdefault(end, [end, before[1], before[2], before[3]])
                before[1] = start
                boundaries[start] = [start, end, before[2] + 1, bg]

        b_idx = 0
        bg = bg_colors[b_idx]
        b_idx = (b_idx + 1) % len(bg_colors)
        for g in range(len(match.groups())+1):
            ins(match.start(g), match.end(g), bg)

        for k, v in boundaries.items():
            if v[3] == None:
                sys.stdout.write(RESET)
                sys.stdout.write(text[v[0]:v[1]])
            else:
                fg = colors[v[2] % len(colors)]
                sys.stdout.write(colored(text[v[0]:v[1]], fg))
        print ""

    def process_IN_MODIFY(self, event):
        if event.name.endswith('.regex'):
            sys.stdout.write("\033c");
            with open(event.name.replace('.regex', '.yaml'), 'r') as y:
                docs = yaml.load_all(y)
                doc = docs.next()
                print doc['description']
                
                with open(event.name) as x:
                    try:
                        re = regex.compile(x.read().strip())
                    except Exception as e:
                        print colored(e, 'red')
                        return
                    
                for doc in docs:
                    match = re.search(doc['text'])
                    ok = self.check(doc, match)
                    if ok:
                        print colored("PASS", 'white', 'on_green'), ' ',
                    else:
                        if doc.has_key('hint'):
                            print colored("HINT:", 'blue', 'on_yellow'),
                            print ' ', doc['hint']
                        print colored("FAIL", 'white', 'on_red'), ' ',

                    if match:
                        self.color(doc['text'], match)
                    else:
                        print doc['text']

sys.stdout.write("\033c");
sys.stdout.flush();
for f in os.listdir('.'):
    if f.endswith('.yaml'):
        with open(f.replace(".yaml", ".regex"), 'w+') as f:
            f.write('.*')

watcher = Watcher()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, watcher)
wm.add_watch('.', pyinotify.IN_MODIFY)
notifier.loop()
