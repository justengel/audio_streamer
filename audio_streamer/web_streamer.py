import asyncio
import threading

import websockets
import pyaudio
import math

from queue import Queue, Empty


def nearest_pow2(value):
    return int(2 ** (math.ceil(math.log(value, 2))))


class AudioStreamer(object):
    def __init__(self, sample_rate=44100, channels=1, fmt=pyaudio.paFloat32):
        self.pa = None
        self.stream = None

        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk = nearest_pow2(math.ceil(sample_rate / 30))
        self.fmt = fmt

    def start(self, callback=None):
        if self.pa is None:
            self.pa = pyaudio.PyAudio()

        self.stream = self.pa.open(format=self.fmt,
                                   channels=self.channels,
                                   rate=int(self.sample_rate),
                                   input=True,
                                   frames_per_buffer=self.chunk,
                                   stream_callback=callback)

    def stream_callback(self, in_data, frame_count, time_info, status):
        return in_data, pyaudio.paContinue

    def read(self, amount=None):
        if amount is None:
            amount = self.chunk
        return self.stream.read(amount)

    def close(self):
        try:
            self.stream.stop_stream()
        except:
            pass
        try:
            self.stream.close()
        except:
            pass
        try:
            self.pa.terminate()
        except:
            pass


def run_server(address='127.0.0.1', port=8222):
    lock = threading.RLock()
    clients = []

    # Create the Audio stream
    def que_data(in_data, frame_count, time_info, status):
        with lock:
            for i in reversed(range(len(clients))):
                try:
                    clients[i].put(in_data)
                except:
                    clients.pop(i)

        return in_data, pyaudio.paContinue

    audio = AudioStreamer(44100, 1)
    audio.start(callback=que_data)

    # Start the web socket server
    async def async_server(websocket, path):
        que = Queue()
        with lock:
            clients.append(que)

        while True:
            try:
                data = que.get(timeout=2)
                await websocket.send(data)
            except Empty:
                pass
            except:
                break

        with lock:
            clients.remove(que)

    start_server = websockets.serve(async_server, address, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    audio.close()


if __name__ == '__main__':
    run_server('127.0.0.1', 8222)