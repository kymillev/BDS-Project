import json
import re

from flair.models import TextClassifier
from flair.data import Sentence

classifier = TextClassifier.load('en-sentiment')

tweets = json.load(open('tweets.json','r'))['tweets']
counter = 0
results = []
for t in tweets:
    counter += 1
    if counter == 50:
        break

    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", t['text']).split())
    text = text.replace('#', ' ').replace('  ', ' ').strip()
    sentence = Sentence(text)
    classifier.predict(sentence)
    # print sentence with predicted labels
    print(text)
    print('Sentence above is: ', sentence.labels)
    results.append(str(sentence.labels[0]))
    print()

json.dump({'flair':results},open('results_flair.json','w'))
