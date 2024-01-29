"""Segment text into sentences and larger chunks

"""
from itertools import accumulate

from stanza import Pipeline

def make_segments_mask_of_(text: str, max_words_in_segment: int, n_overlapping_sentences: int):
    """Split text into segments of max_words_in_segment words.

    """
    splitter = Pipeline(lang='sv', processors='tokenize')
    doc = splitter(text)

    n_tokens_per_sentence = [len(sentence.tokens) for sentence in doc.sentences]

    k_segment = 0
    mask = {}
    ind_base = 0
    ind_abs = 0
    ind = 0
    n_tokens_in_segment = 0
    mask_ = []
    while ind + ind_abs < len(doc.sentences):

        if n_tokens_in_segment + n_tokens_per_sentence[ind] >= max_words_in_segment:
            mask[k_segment] = mask_
            ind_base = max(1, ind - n_overlapping_sentences)
            n_tokens_per_sentence = n_tokens_per_sentence[ind_base:]
            k_segment += 1
            ind_abs += ind_base

            ind = 0
            n_tokens_in_segment = 0
            mask_ = []

        n_tokens_in_segment += n_tokens_per_sentence[ind]
        mask_.append(ind + ind_abs)
        ind += 1

    mask[k_segment] = mask_
    print (mask)


if __name__ == '__main__':
    make_segments_mask_of_('Hejsan på dig. Hur mås det? Jag är helt okej. Tack tack, får man säga. Men hemskt vad galet vädret är. Kors i taket säger jag!', 14, 1)