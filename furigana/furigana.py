import os
import sys
import unicodedata

import fugashi
import jaconv


def is_kanji(ch):
    return "CJK UNIFIED IDEOGRAPH" in unicodedata.name(ch)


def is_hiragana(ch):
    return "HIRAGANA" in unicodedata.name(ch)


def is_katakana(ch):
    return "KATAKANA" in unicodedata.name(ch)


def is_japanese(text):
    for c in text:
        if is_kanji(c) or is_hiragana(c) or is_katakana(c):
            return True
    return False


def split_okurigana(text, hiragana):
    """ 送り仮名 processing
      tested:
         * 出会(であ)う
         * 明(あか)るい
         * 駆(か)け抜(ぬ)け
         * 言い(いー)
         * 口(くち)ぐせ
         * 暖(あたた)め
    """
    for i, char in enumerate(text):
        if is_kanji(char):
            yield text[:i]
            text = text[i:]
            hiragana = hiragana[i:]
            break

    for i, char in enumerate(text):
        for j, hira in enumerate(hiragana):
            if char == hira:
                if not hiragana[:j]:
                    continue
                yield text[:i], hiragana[:j]
                hiragana = hiragana[j:]
                yield hiragana
                return
    if text != hiragana:
        yield text, hiragana
    else:
        yield hiragana


def kata2hira(kata):
    return jaconv.kata2hira(kata or "")


def init_dictionary(tagger_params):
    from MeCab import Tagger as mTagger
    from fugashi import UnidicFeatures17, UnidicFeatures26, UnidicFeatures29
    n_features = len(mTagger(tagger_params).parse("日本").split(','))
    features = []
    if n_features == 17:
        features = UnidicFeatures17
    elif n_features == 26:
        features = UnidicFeatures26
    elif n_features == 29:
        features = UnidicFeatures29
    del mTagger, UnidicFeatures17, UnidicFeatures26, UnidicFeatures29
    return fugashi.GenericTagger(tagger_params, features)


class Furigana:
    def __init__(self, format="", dicdir=os.getenv("DICDIR"), exceptions={}):
        tagger_params = ""
        if format:
            tagger_params += f"-O{format}"
        if dicdir:
            tagger_params += f"-d {dicdir}"
        try:
            self.tagger = init_dictionary(tagger_params)
        except RuntimeError:
            self.tagger = fugashi.GenericTagger()
        self.exceptions = exceptions

    def split_furigana(self, text):
        """ MeCab has a problem if used inside a generator ( use yield instead of return  )
        The error message is:
        ```
        SystemError: <built-in function delete_Tagger> returned a result with an error set
        ```
        It seems like MeCab has bug in releasing resource
        """
        furi_split = []

        if not is_japanese(text):
            return [text]
        for t in self.tagger.parseToNodeList(text):
            if any(is_kanji(_) for _ in t.surface):
                pron = kata2hira(t.feature.pron) if t.surface not in self.exceptions else self.exceptions[t.surface]
                for o in split_okurigana(t.surface, pron):
                    furi_split.append(o)
            else:
                furi_split.append(t.surface)
        return furi_split

    def to_html(self, text):
        html = ""
        for pair in self.split_furigana(text):
            if type(pair) == tuple:
                kanji, hira = pair
                html += f'<span class="node"><ruby>{kanji}<rt>{hira}</rt></ruby></span>'
            else:
                html += f'<span class="node">{pair}</span>'
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
