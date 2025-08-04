# from pyaudio import paInt16, PyAudio


# stream = PyAudio().open(
#     format=paInt16,
#     channels=1,
#     rate=16000,
#     input=True,
#     frames_per_buffer=1024,
#     stream_callback=lambda in_data, frame_count, time_info, status: (in_data, PyAudio.paContinue),
# )

# stream.start_stream()



# from voice_recorder.infrastructure.audio_recorder import PyAudioRecorder
# from voice_recorder.domain.models import AudioConfig

# config = AudioConfig()

# recorder = PyAudioRecorder()
# recorder.start_recording(config=config)

# recorder.play_start_beep()





from voice_recorder.api.app import create_app

app = create_app()

app.start() 