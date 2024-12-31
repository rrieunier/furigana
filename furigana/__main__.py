#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# $ python -m hello

import sys

from furigana.furigana import Furigana


def main():
    text = sys.argv[1]
    Furigana().print_plaintext(text)


if __name__ == "__main__":
    main()
