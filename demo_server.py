import argparse
import falcon
from hparams import hparams, hparams_debug_string
import os
from synthesizer import Synthesizer
import time
from pydub import AudioSegment
import io
import re

html_body = '''<html><head><title>Demo</title>
<meta charset="utf-8">
<script src="js/numberwork.js"></script>
<style>
body {padding: 16px; font-family: sans-serif; font-size: 14px; color: #444}
input {font-size: 14px; padding: 8px 12px; outline: none; border: 1px solid #ddd}
input:focus {box-shadow: 0 1px 2px rgba(0,0,0,.15)}
p {padding: 12px; text-align: center}
button {background: #28d; padding: 9px 14px; margin-left: 8px; border: none; outline: none;
        color: #fff; font-size: 14px; border-radius: 4px; cursor: pointer;}
button:hover {box-shadow: 0 1px 2px rgba(0,0,0,.15); opacity: 0.9;}
button:active {background: #29f;}
button[disabled] {opacity: 0.4; cursor: default}
img, textarea, message,  button, progress, audio, p{
            display: block;
            margin: 0 auto 32px;
        }
        img {
            height: 180px;
            margin-bottom: 0;
        }
        textarea{
            padding: 0;
            border: 1px solid #ccc;
            resize: vertical;
        }
        img, form{
            margin-bottom: 0;
        }
</style>
</head>
<body>
<img src="http://mamtil.kg/wp-content/uploads/2017/08/cropped-cropped-555-3.png">
<p id = "title" style="text-transform: uppercase; font-weight: bold;"></p>
<form>
 <textarea rows="10" cols="45" name="text" id="text"></textarea> 
  <button id="button" name="synthesize">Speak</button>
</form>
<p id="message"></p>
<audio id="audio" controls autoplay hidden></audio>
<script>
var el = document.getElementById("button");
el.firstChild.data = buttonValue;
document.getElementById("title").textContent = projectName;
function q(selector) {return document.querySelector(selector)}
q('#text').focus()
q('#button').addEventListener('click', function(e) {
  text = q('#text').value.trim()
  if (text) {
    text = make_numbers(text);
    var timeLeft = ApprTime(text);
    var StartTime = timeLeft;
    document.getElementById("progressBar").max =  timeLeft;
    document.getElementById("progressBar").style.display = "block";
    var downloadTimer = setInterval(function(){
        document.getElementById("progressBar").value = StartTime - --timeLeft;
	if(timeLeft <= 0) clearInterval(downloadTimer);},1000);
    q('#message').textContent = apprtimesubject + timeLeft + apprtimeseconds;

    q('#button').disabled = true
    q('#audio').hidden = true
    text = text.trim();
    synthesize(text)
  }
  e.preventDefault()
  return false
})
function synthesize(text) {
  fetch('/synthesize?text=' + encodeURIComponent(text), {cache: 'no-cache'})
    .then(function(res) {
      if (!res.ok) throw Error(res.statusText)
      return res.blob()
    }).then(function(blob) {
      document.getElementById("progressBar").style.display = "none";
      q('#message').textContent = ''
      q('#button').disabled = false
      q('#audio').src = URL.createObjectURL(blob)
      q('#audio').hidden = false
    }).catch(function(err) {
      q('#message').textContent = 'Error: ' + err.message
      q('#button').disabled = false
    })
}
</script>
<progress value="0" max="10" id="progressBar" style="display:none"></progress>
</body></html>
'''


class UIResource:
  def on_get(self, req, res):
    res.content_type = 'text/html'
    res.body = html_body

def get_final_array(full_text):
    final_array = []
    word_count  = len(full_text.split(' '))
    if word_count<8:
         final_array.append(full_text)
         return final_array
    if word_count>300:
         return final_array
    sentences = re.findall('.*?[:;.!\?]', full_text)
    if len(sentences)==0:
        sentences = full_text.split('.') 
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence)<2:
           continue
        words = sentence.split(' ')

        if len(words)>6:
           n=6

           text_array = [' '.join(words[i:i+n]) for i in range(0,len(words),n)]
           for text_6_words in text_array:
               if len(text_6_words.split())<3:
                   final_array[-1] += text_6_words 
               else:
                   final_array.append(text_6_words)
        else:
           final_array.append(sentence+".")
    return final_array

class NumberWorksJsResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/javascript'
        with open('static/numberwork.js', 'r') as f:
            resp.body = f.read()

class SynthesisResource:
  
  def on_get(self, req, res):
    if not req.params.get('text'):
      raise falcon.HTTPBadRequest()
    full_text = req.params.get('text')
    final_array = get_final_array(full_text)
    my_list = []
    start_1= time.time()
    for txt in final_array:
       my_list.append(synthesizer.synthesize(txt+"."))
       this_time = time.time()
       print(this_time - start_1)
       start_1 = time.time()
    result = AudioSegment.silent(duration=100)
    for audio in my_list:
        result += AudioSegment.from_file(io.BytesIO(audio), format="wav")
    buf = io.BytesIO()
    result.export(buf, format="mp3")
    resdata = buf.getvalue()
    res.data = resdata
    res.content_type = 'audio/wav'

synthesizer = Synthesizer()
api = falcon.API()
api.add_route('/synthesize', SynthesisResource())
api.add_route('/', UIResource())
api.add_route('/js/numberwork.js', NumberWorksJsResource())


if __name__ == '__main__':
  from wsgiref import simple_server
  parser = argparse.ArgumentParser()
  parser.add_argument('--checkpoint', required=True, help='Full path to model checkpoint')
  parser.add_argument('--port', type=int, default=9000)
  parser.add_argument('--hparams', default='',
    help='Hyperparameter overrides as a comma-separated list of name=value pairs')
  args = parser.parse_args()
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
  hparams.parse(args.hparams)
  print(hparams_debug_string())
  synthesizer.load(args.checkpoint)
  print('Serving on port %d' % args.port)
  simple_server.make_server('0.0.0.0', args.port, api).serve_forever()
else:
  synthesizer.load(os.environ['CHECKPOINT'])
