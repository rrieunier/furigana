#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import unicodedata

import fugashi
import jaconv


def is_kanji(ch):
    return "CJK UNIFIED IDEOGRAPH" in unicodedata.name(ch)


def is_hiragana(ch):
    return "HIRAGANA" in unicodedata.name(ch)


class Furigana:
    def __init__(self, format="", dicdir=""):
        tagger_params = ""
        if format:
            tagger_params += f"-O{format}"
        if dicdir:
            tagger_params += f"-d {dicdir}"
        try:
            self.tagger = fugashi.Tagger(tagger_params)
        except RuntimeError:
            self.tagger = fugashi.Tagger()

    def split_furigana(self, text):
        """ MeCab has a problem if used inside a generator ( use yield instead of return  )
        The error message is:
        ```
        SystemError: <built-in function delete_Tagger> returned a result with an error set
        ```
        It seems like MeCab has bug in releasing resource
        """
        return [c if is_hiragana(c) else (c, jaconv.kata2hira(c.feature.pron)) for c in self.tagger(text)]

    def to_html(self, text):
        html = ""
        for pair in self.split_furigana(text):
            if len(pair) == 2:
                kanji, hira = pair
                html += f"<ruby>{kanji}<rt>{hira}</rt></ruby>"
            else:
                html += pair
        return html

    def print_html(self, text):
        print(self.to_html(text))

    def to_plaintext(self, text):
        plain = ""
        for pair in self.split_furigana(text):
            if len(pair) == 2:
                kanji, hira = pair
                plain += f"{kanji}({hira})"
            else:
                plain += pair
        return plain

    def print_plaintext(self, text):
        print(self.to_plaintext(text))


def main():
    text = sys.argv[1]
    Furigana().print_html(text)


if __name__ == "__main__":
    main()
