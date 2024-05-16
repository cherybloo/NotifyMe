from playsound import playsound
import fakeyou

def quad():
    playsound('QUAD.mp3')

def rick():
    playsound('rick.mp3')

def text_to_speech(message):
    fy=fakeyou.FakeYou()
    fy.say(text=message,ttsModelToken="weight_qfz806d82b0qmxfn3vzgmtyme")
    playsound('fakeyou.wav')

text_to_speech("You bro, tell you what, there was a fire on my neighbor's balcony. That was pretty rad. Talk to you soon")
rick()