#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import furigana


def main():
    for pair in furigana.furigana(sys.argv[1]):
        if len(pair) == 2:
            kanji, hira = pair
            print(f"{kanji}({hira})")
        else:
            print(pair[0])


VERSION = "0.0.8"
