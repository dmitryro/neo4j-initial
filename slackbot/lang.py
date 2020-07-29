import logging
import difflib
import nltk
from nltk.tag import pos_tag, map_tag

nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('punkt')

def is_question(q):
        text = nltk.word_tokenize(q)
        posTagged = pos_tag(text)
        simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
        onlytags=[]

        for lc in range(0,len(simplifiedTags)):
            onlytags.append(simplifiedTags[lc][1])
            logging.debug("computing done")
        sqp=[["pron","verb","noun"],["pron","verb","det","noun"]]
        res=False

        for m in sqp:
            qm=difflib.SequenceMatcher(None, str(onlytags)[1:].lower(), str(m).lower())
            r=qm.real_quick_ratio()*100
            if r>97:
                res=True
                break
            else:
                res=False
        return res

