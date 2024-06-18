#!/usr/bin/env python3

'''
Name 
    genie - Receives a prompt and tries to answer it with the information of the DRE

SYNOPSIS
    -p <prompt> - a single prompt (quoted). if not specified, takes each line from stdin as a prompt
    -n <int> - number of texts to supply as context (defauls to 3)
    -r - show the texts considered for answering the question
    -s - show the score of each answer
    --help - Show this help message


DESCRIPTIONS
    Program to query the DRE
    
FILES:
    datasetsParsers/
    datasets/
    testes/
    parser.py
    Token.py
    Trie.py
    utils.py

'''

__version__ = "1.0.0"

from collections.abc import Iterable
from toogle import toogle
from chatPT import chatPT
from archivist import get_body, get_metadata

from jjcli import *
import itertools
import sys


cl = clfilter("srp:n:", doc=__doc__) ## Option values in cl.opt dictionary

#receives a str 
def enough_texts(src: Iterable[str]) -> Iterable[str]:
    l = 0
    for s in src:
        yield s
        l += len(s)
        if l > 300:
            return

def main():
    prompts = [cl.opt.get("-p")] if "-p" in cl.opt else sys.stdin

    context=""

    for p in prompts:
        src = (f"{get_metadata(id)}\n{get_body(id)}" for id,score in toogle(p))
        texts = list(itertools.islice(src, int(cl.opt.get("-n", 3)))) # if "-n" in cl.opt else enough_texts(src)

        for t in texts:
            print(t)
        exit()

        if "-r" in cl.opt:
            for t in texts:
                print("----------------------------------------")
                print(t)
                

        answer,score = chatPT("\n\n".join((*texts, context)), p)
        
        if "-r" in cl.opt:
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(answer)
        if "-s" in cl.opt:
            print(score)
        if "-r" in cl.opt:
            print("\n\n")

        context += f"{p}\n{answer}\n\n"

main()