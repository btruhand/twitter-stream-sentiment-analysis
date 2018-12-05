from sentiment import sentiment_score

import sys
import re

from textblob import TextBlob 

def main():
    filepath = 'example_tweets.txt'  
    with open(filepath) as fp:  
        line = fp.readline()
        cnt = 1
        while line:
            line = fp.readline()
            if line == '':
                continue
            print('original message: ' + line.strip())
            clean_message = (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", line).split()))
            clean_message2 = (' '.join(re.sub("(@[A-Za-z0-9]+)", " ", line).split()))
            clean_message3 = (' '.join(re.sub("(@[A-Za-z0-9]+)"," ", line).split()))
            clean_message4 = (' '.join(re.sub("(\w+:\/\/\S+)", " ", line).split()))
            clean_message5 = (' '.join(re.sub("(#.+)", " ", line).split()))
            clean_message6 = (' '.join(re.sub("(#.*$)", " ", line).split()))
            clean_message7 = (' '.join(re.sub("(#.*)", " ", line).split()))
            clean_message8 = (' '.join(re.sub("(#\w+)", " ", line).split()))
            clean_message9 = (' '.join(re.sub("(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", line).split()))



            #clean_message3 = (' '.join(re.sub((#text;"#\\w*")"," ", line).splsit())
            print('cleaned message: ' + clean_message)
            print('cleaned message2: ' + clean_message2)
            print('cleaned message3: ' + clean_message3)
            print('cleaned message4: ' + clean_message4)
            print('cleaned message5: ' + clean_message5)
            print('cleaned message6: ' + clean_message6)
            print('cleaned message7: ' + clean_message7)
            print('cleaned message8: ' + clean_message8)
            print('cleaned message9: ' + clean_message9)
            print('original sentiment score: ' + str(sentiment_score(line)))
            print('cleaned sentiment score: ' + str(sentiment_score(clean_message)))
            analysis = TextBlob(clean_message)
            print('cleaned TextBlob sentiment score: ' + str(analysis.sentiment.polarity))
            #print(analysis.sentiment.polarity)
            #print('cleaned TextBlob sentiment score: ' + (TextBlob(clean_message.sentiment.polarity))) 
            print('\n')            
            cnt += 1    

if __name__ == '__main__':
    main()

