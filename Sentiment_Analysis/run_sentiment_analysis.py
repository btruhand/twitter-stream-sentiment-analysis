from sentiment import sentiment_score

import sys

#reload(sys)
#sys.setdefaultencoding('utf8')


#def main(message):
def main():
    #message = "happiness is what"
    #print (sentiment_score(message))
    print (sentiment_score(u"I love you"))

if __name__ == '__main__':
    #message = sys.argv[1]
    #main(message)
    main()

