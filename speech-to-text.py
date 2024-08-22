import vosk
import sounddevice as sd
import queue
import json
import os

# Update this path to where you extracted the model
model_path = "./vosk-model-en-us-0.22"

if not os.path.exists(model_path):
    print(f"Error: Model path '{model_path}' does not exist.")
    print("Please update the 'model_path' variable with the correct path to your Vosk model.")
    exit(1)

try:
    model = vosk.Model(model_path)
    device = sd.default.device
    samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])

    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0], dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        print("Starting transcription. Speak into your microphone. Press Ctrl+C to stop.")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print(result['text'])
            else:
                partial = json.loads(rec.PartialResult())
                print(partial['partial'], end='\r')

except Exception as e:
    print(f"An error occurred: {str(e)}")
    print("Make sure you have installed the required packages (vosk, sounddevice) and downloaded a Vosk model.")