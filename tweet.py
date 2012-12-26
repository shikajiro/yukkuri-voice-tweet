# -*- coding: utf-8 -*-
import os
import tweepy
import urllib2
import re
import webbrowser
import datetime
from xml.etree import ElementTree
from tweepy.streaming import StreamListener

CONSUMER_KEY = "di7fFCE7dMhxg9ii2zZNtg"
CONSUMER_SECRET = "sWNw6RweHGGKQrmJwB2Fdl0BY2JbgtNP82YPlxk1Ew"
i = 0


def Kanji2Hiragana(message):
    t = re.sub('(?![ぁ-ヶ亜-黑、。！？]).', '', message.encode('utf-8'))
    t = re.sub('\n', '', t)
    urlbase = "http://jlp.yahooapis.jp/FuriganaService/V1/furigana?appid=74tpjyixg642KBYE45iAsqcgRdfcMEYURUhP7NKdYd6E9zvxBOcUWCgRmAU24iju&grade=1&sentence='{}'"
    url = urlbase.format(t)
    xml = urllib2.urlopen(url).read()
    elem = ElementTree.fromstring(xml)
    text = ''
    for w in elem.findall(".//{urn:yahoo:jp:jlp:FuriganaService}Word"):
        furi = w.findtext('.//{urn:yahoo:jp:jlp:FuriganaService}Furigana')
        if furi is None:
            furi = w.findtext('.//{urn:yahoo:jp:jlp:FuriganaService}Surface')
        text = text + furi
    return text


class AbstractedlyListener(StreamListener):
    """ Let's stare abstractedly at the User Streams ! """
    def on_status(self, status):
        name = Kanji2Hiragana(status.user.name)
        text = Kanji2Hiragana(status.text)
        if text != "''":
            if name == "''":
                name = u"だれかさん"
            print 'name {}'.format(name.encode('utf-8'))
            print 'text {}'.format(text.encode('utf-8'))
            os.system('SayKana -o output{}.aiff {}のつぶやき。'.format(datetime.datetime.today().time(), name.encode('utf-8')))
            os.system('SayKana -o output{}.aiff {}'.format(datetime.datetime.today().time(), text.encode('utf-8')))

key = ''
secret = ''
try:
    with open('token.txt', 'r') as f:
        key = f.readline().replace('\n', '')
        secret = f.readline()
except IOError:
    #ファイルがない場合はなにもしない
    pass

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
if not key or not secret:
    #保存されたトークンがない場合は取得処理を行う
    webbrowser.open(auth.get_authorization_url())
    pin = raw_input('Verification pin number from twitter.com: ').strip()
    token = auth.get_access_token(verifier=pin)
    key = token.key
    secret = token.secret

    #トークンをファイルに保存する
    with open('token.txt', 'w') as f:
        f.write(key)
        f.write('\n')
        f.write(secret)
        print 'key {} secret {} write to token.txt.'.format(token.key, token.secret)

# 認証処理後、ユーザーストリームを監視
auth.set_access_token(key, secret)
stream = tweepy.Stream(auth, AbstractedlyListener(), secure=True)
print 'tweet start.'
stream.userstream()
print 'tweet end'
