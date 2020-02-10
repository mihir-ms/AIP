from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import requests
from bs4 import BeautifulSoup
import lxml
from googleapiclient import discovery
from googleapiclient.discovery import build
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
from candidate.algorithms.scoring import scoring
import speech_recognition as sr 
import moviepy.editor as mp
import time
import os
from django.conf import settings
import subprocess

#nltk.download('punkt')
LANGUAGE = "english"
SENTENCES_COUNT = 10
relevant_answers = []

def summarized_data_from_url(url):
  parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
  stemmer = Stemmer(LANGUAGE)
  summarizer = Summarizer(stemmer)
  summarizer.stop_words = get_stop_words(LANGUAGE)
  temp_ans =[]
  for sentence in summarizer(parser.document, SENTENCES_COUNT):
      #print(sentence)
      temp_ans.append(str(sentence))
  relevant_answers.append("".join(temp_ans))

headers_Get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def general_question_answer(candidate,job,ids,que,video_path):
    a = time.time()
    print("from answer ",candidate,job,ids,que,video_path)
    # download frm firestorage
    r = requests.get(video_path)
    inp = ids+'.webm'
    print(inp)
    with open(inp,"wb") as f:
        f.write(r.content)
    print("writing video in file")
    time.sleep(3)
    # Video to Audio 
    op = ids+'.mp4'
    cmds = ['ffmpeg', '-i', inp, op]
    subprocess.Popen(cmds)
    clip = mp.VideoFileClip(op) #.mp4 path
    video_wav = ids+'.wav'
    clip.audio.write_audiofile(video_wav) #.wav path

    # # Audio to Text

    AUDIO_FILE = (video_wav) #.wav path  
    r = sr.Recognizer() 
        
    with sr.AudioFile(AUDIO_FILE) as source: 
        audio = r.record(source)   
        
    try: 
        temp = r.recognize_google(audio,language="en-US")
        print(temp)
        my_answer = temp

    except sr.UnknownValueError: 
        print("Google Speech Recognition could not understand audio")
        exit()
        
    except sr.RequestError as e: 
        print("Could not request results from Google Speech  Recognition service; {0}".format(e)) 
        exit()

    s = requests.Session()
    q = '+'.join(que.split())
    url = 'https://www.google.com/search?q=' + q + '&ie=utf-8&oe=utf-8'
    r = s.get(url, headers=headers_Get)

    soup = BeautifulSoup(r.text, "html.parser")
    output = []
    for searchWrapper in soup.find_all('div', {'class':'r'}): 
        url = searchWrapper.find('a')["href"] 
        output.append(url)
    #print(output,"\n")
    for i in output:
      summarized_data_from_url(i)
    
    print(scoring(relevant_answers,my_answer))
    b = time.time()
    print("Answer Processing time : ",(b-a))

#question = "What do you mean by DevOps"
#my_answer = 'DevOps (development and operations) is an enterprise software development phrase used to mean a type of agile relationship between development and IT operations. The goal of DevOps is to change and improve the relationship by advocating better communication and collaboration between these two business units.'
#general_question_answer(question)
#print(scoring(relevant_answers,my_answer))