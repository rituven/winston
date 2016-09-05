import requests
from core import BaseApp, ServiceCommunicationError, getMessenger, \
                Listener, Events, HandlerTuple
import os
import threading
import time
import threading
import alsaaudio
import re
import json
import creds
from monotonic import monotonic

ACCESS_EXPIRY_TIME = 3570
DEVICE = 'plughw:1'
MEDIA_PATH = os.path.join(os.getcwd(), 'alexa/media')
HELLO_MP3 = os.path.join(MEDIA_PATH, 'hello.mp3')
ONE_SEC_MP3 = os.path.join(MEDIA_PATH, '1sec.mp3')
RECORDING_WAV = os.path.join(MEDIA_PATH, 'recording.wav')
RESPONSE_MP3 = os.path.join(MEDIA_PATH, 'response.mp3')
BEEP_WAV = os.path.join(MEDIA_PATH, 'beep.wav')

class AlexaService(BaseApp):
    def __init__(self):
        self.checkInternetConn()
        btnClickedHandler = HandlerTuple(self.btnClicked, None, None)
        evtDict = { Events.UI_BTN_CLICKED: btnClickedHandler}
        self.listener = Listener(evtDict)
        self.messenger = getMessenger()
        self.accessTokenTimeStamp = 0
        self.accessToken = None
        self.messenger.subscribe(self.listener)
        self.__captureEvent = threading.Event()
        self.__captureStop = threading.Event()
        print('Alexa Initialized')
        os.system('mpg123 -q {}'.format(HELLO_MP3))

    def checkInternetConn(self):
        """
        Check if there is internet communication
        """
        try:
            r =requests.get('https://api.amazon.com/auth/o2/token')
        except:
            raise ServiceCommunicationError('Could not connect to Amazon')

    def btnPressed(self, data):
        if not self.__captureEvent.is_set():
            self.__captureEvent.set()
            self.captureThread = threading.Thread(target=self.capture)
            os.system('aplay {}'.format(BEEP_WAV))
            self.captureThread.start()

    def btnReleased(self, data):
        if self.__captureEvent.is_set():
            self.__captureEvent.clear()
            os.system('aplay {}'.format(BEEP_WAV))
            if self.captureThread:
               self.captureThread.join()
               self.captureThread = None

    def btnClicked(self, data):
        os.system('aplay {}'.format(BEEP_WAV))
        if self.__captureEvent.is_set():
            self.__captureEvent.clear()
            self.captureThread.join()
            self.captureThread = None
        else:
            self.__captureEvent.set()
            self.captureThread = threading.Thread(target=self.capture)
            self.captureThread.start()

    def gettoken(self):
        if self.accessToken and \
            (monotonic() - self.accessTokenTimeStamp) < ACCESS_EXPIRY_TIME:
            return self.accessToken
        elif creds.refreshToken:
            payload = {"client_id" : creds.clientID,
                            "client_secret" : creds.clientSecret,
                            "refresh_token" : creds.refreshToken,
                            "grant_type" : "refresh_token", }
            url = "https://api.amazon.com/auth/o2/token"
            r = requests.post(url, data = payload)
            resp = json.loads(r.text)
            self.accessTokenTimeStamp = monotonic()
            self.accessToken = resp['access_token']
            return resp['access_token']
        else:
            return False

    def alexaSend(self):
        url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
        headers = {'Authorization' : 'Bearer ' + self.gettoken()}
        d = {
           "messageHeader": {
               "deviceContext": [
                       {
                           "name": "playbackState",
                           "namespace": "AudioPlayer",
                           "payload": {
                               "streamId": "",
                               "offsetInMilliseconds": "0",
                               "playerActivity": "IDLE"
                           }
                       }
                   ]
            },
               "messageBody": {
                   "profile": "alexa-close-talk",
                   "locale": "en-us",
                   "format": "audio/L16; rate=16000; channels=1"
               }
        }
        with open(RECORDING_WAV) as inf:
            files = [
                    ('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
                    ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
                    ]
            r = requests.post(url, headers=headers, files=files)
        if r.status_code == 200:
            for v in r.headers['content-type'].split(";"):
                if re.match('.*boundary.*', v):
                    boundary =  v.split("=")[1]
            data = r.content.split(boundary)
            for d in data:
                if (len(d) >= 1024):
                    audio = d.split('\r\n\r\n')[1].rstrip('--')
            with open(RESPONSE_MP3, 'wb') as f:
                f.write(audio)

            os.system('mpg123 -q {} {} {}'.format(ONE_SEC_MP3,
                                                    RESPONSE_MP3,
                                                    ONE_SEC_MP3))
        else:
            raise ServiceCommunicationError('Got error from server: {}'.format(r.status_code))

    def capture(self):
        mic = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, DEVICE)
        mic.setchannels(1)
        mic.setrate(16000)
        mic.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        mic.setperiodsize(500)
        audio = ''
        while self.__captureEvent.is_set():
            length, data = mic.read()
            if length:
                audio += data
        with open(RECORDING_WAV, 'w') as rf:
            rf.write(audio)
        self.alexaSend()
