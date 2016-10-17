#! /usr/bin/env python

import os, sys
import yaml
import regex
from termcolor import colored
from sortedcontainers import SortedDict
import pyinotify

ident = lambda x: x
bg_colors = ['on_blue','on_white']
colors = ['green','cyan','yellow','red']
class Watcher(pyinotify.ProcessEvent):
    def check(self, spec, match):
        return True

    def color(self, text, matches):
        boundaries = SortedDict(ident)
        boundaries[0] = [0, len(text)-1, 'on_black']
        
        def ins(start, end, bg):
            if boundaries.has_key(start):
                before = boundaries[start]
                if before[1] == end:
                    before[2] = bg
                else:
                    before[1] = end+1
                    boundaries[start] = [start, end, bg]
            else:
                k = boundaries.bisect_key_right(start)
                key = boundaries.iloc[k-1]
                before = boundaries[key]
                boundaries[end+1] = [end+1, before[1], before[2]]
                before[1] = start - 1
                boundaries[start] = [start, end, bg]

        b_idx = 0
        for m in matches:
            bg = bg_colors[b_idx]
            b_idx = (b_idx + 1) % len(bg_colors)
            ins(m.start(0), m.end(0), bg)
            for g in range(1, len(m.groups())):
                ins(m.start(g), m.end(g), bg)

        for k, v in boundaries.items():
            print k,v

    def process_IN_MODIFY(self, event):
        if event.name.endswith('.regex'):
            sys.stdout.write("\033c");
            with open(event.name) as f:
                re = regex.compile(f.read().strip(), regex.X)
            with open(event.name.replace('.regex', '.yaml'), 'r') as y:
                docs = yaml.load_all(y)
                doc = docs.next()
                print doc['description']
                for doc in docs:
                    test = lambda m: self.check(doc, m)
                    matches = list(re.finditer(doc['text']))
                    if bool(filter(test,matches)) ^ bool(doc['match']):
                        print colored("FAIL ", 'red'),

                    if matches:
                        print self.color(doc['text'], matches)
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
wm.add_watch('.', pyinotify.ALL_EVENTS)
notifier.loop()
#wm.add_watch('.', pyinotify.IN_MODIFY)
