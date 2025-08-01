# from re import A
# from voice_recorder.infrastructure.audio_feedback import SystemAudioFeedback

# audio_feedback = SystemAudioFeedback()

# audio_feedback.play_basic_start_beep()

# audio_feedback.play_basic_stop_beep()

# audio_feedback.play_enhanced_start_beep()

# audio_feedback.play_enhanced_stop_beep()

# audio_feedback.play_start_beep()

# audio_feedback.play_stop_beep()



# from voice_recorder.api.app import create_app

# app = create_app()

# app.start()

from pyaudio import PyAudio, paInt16

PyAudio().open(
    format=paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024,
    stream_callback=lambda in_data, frame_count, time_info, status: (in_data, PyAudio.paContinue),
)