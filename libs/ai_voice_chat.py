import asyncio
import websockets
import pyaudio
import numpy as np
import base64
import json
import logging
import continuous_recorder as cr

class AiVoiceChat:
    # audio settings
    RATE = 24000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    O_CHUNK = 1024
    disposing = False
    disposed = 0

    # WebSocket URL
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    interruptted = [False]

    async def record_audio(self, ws):

        recorder = cr.ContinuousRecorder(self.interruptted)
        recorder.start_recording()  
        print("Recording..")

        try:
            while self.disposing == False:
                await asyncio.sleep(0.01)
                data = recorder.get_audio()
                if len(data) == 0:
                    continue

                base64_audio = base64.b64encode(data).decode('utf-8')
                # send event
                event = {
                    "type": "input_audio_buffer.append",
                    "audio": base64_audio,
                }
                await ws.send(json.dumps(event))
                #self.audio_delta.append(base64_audio)
                #self.play_audio([base64_audio])
        except Exception as e:
            logging.error(e, exc_info=True)
            self.dispose() 

        recorder.stop_recording()
        self.disposed += 1

    async def receive_audio(self, ws):

        loggedTypes = [
            "error",
            # "response.audio_transcript.done",
            "response.done",
            "rate_limits.updated"
        ]

        self.audio_delta = []
        self.audio_data = b''
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.O_CHUNK,
            stream_callback=self.pa_callback 
        )
        await asyncio.sleep(0.1)
        stream.start_stream()

        try:
            async for message in ws:
                response = json.loads(message)
                if response["type"] in loggedTypes:
                    print(response)

                if response["type"] == "error":
                    self.dispose()
                    break
                    
                elif response["type"] == "response.audio.delta":
                    self.callback(response["delta"])
                    print("Responsing..")

                elif response["type"] == "response.done":
                    self.callback(None)
                    print("Response completed")
        
        except Exception as e:
            logging.error(e, exc_info=True)
            self.dispose()

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.disposed += 1


    def pa_callback(self, in_data, frame_count, time_info, status):
        base64_audios = self.audio_delta
        self.audio_delta = []
        audio_array = [base64.b64decode(base64_audio) for base64_audio in base64_audios]
        audio_data = self.audio_data + b''.join(audio_array)
        
        frame_data = None
        required_count = self.O_CHUNK * 2

        # 再生するデータを指定したフレーム数だけ取り出す
        if len(audio_data) < required_count:
            # 最後の部分でデータが足りない場合は余白をゼロで埋める
            frame_data = audio_data[:]
            frame_data += b'\x00' * (required_count - len(audio_data)) 
            self.audio_data = b''
        else:
            frame_data = audio_data[0:required_count]
            self.audio_data = audio_data[required_count:]

        frame_data = np.frombuffer(frame_data, dtype=np.int16)
        return (frame_data, pyaudio.paContinue)


    def play_audio(self, base64_audios):
        audio_array = [base64.b64decode(base64_audio) for base64_audio in base64_audios]
        audio_data = b''.join(audio_array)

        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, output=True)
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    async def websocket_client(self):
        async with websockets.connect(self.url, extra_headers={"Authorization": self.auth_token, "OpenAI-Beta": "realtime=v1"}) as ws:
            print("Realtime API Session Created")

            # update session
            session_event = {
                "type": "session.update",
                "session": {
                    "instructions": self.init_prompt,
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.4,
                        "prefix_padding_ms": 20,
                        "silence_duration_ms": 700,
                    }
                }
            }
            await ws.send(json.dumps(session_event))
            
            record_task = asyncio.create_task(self.record_audio(ws))
            receive_task = asyncio.create_task(self.receive_audio(ws))
            
            while self.disposing == False:
                await asyncio.sleep(0.01)

            if ws.closed == False:
                await ws.close()

            self.disposed += 1


    # def signal_handler(sig, frame):
    #     global interruptted
    #     interruptted[0] = True

    # signal.signal(signal.SIGINT, signal_handler)

    def __init__(self, callback, oai_api_key, init_prompt):
        self.callback = callback
        self.auth_token = "Bearer " + oai_api_key
        self.init_prompt = init_prompt

    async def start(self):
        await self.websocket_client()
        
        print("Realtime API Session Closed")

    def dispose(self):
        self.disposing = True

    def is_disposed(self):
        return self.disposed == 3
