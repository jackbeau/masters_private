from audio_recorder import AudioToTextRecorder

import os

if __name__ == '__main__':

    print("Initializing RealtimeSTT test...")

    full_sentences = []
    displayed_text = ""

    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    def text_detected(text):
        global displayed_text
        sentences_with_style = [
            f"{sentence + "" + sentence} "
            for i, sentence in enumerate(full_sentences)
        ]
        new_text = "".join(sentences_with_style).strip() + " " + text if len(sentences_with_style) > 0 else text

        if new_text != displayed_text:
            displayed_text = new_text
            clear_console()
            print(displayed_text, end="", flush=True)

    # def text_detected(text):
    #     global displayed_text
    #     clear_console()
    #     print(text)
        # sentences_with_style = [
        #     f"{Fore.YELLOW + sentence + Style.RESET_ALL if i % 2 == 0 else Fore.CYAN + sentence + Style.RESET_ALL} "
        #     for i, sentence in enumerate(full_sentences)
        # ]
        # new_text = "".join(sentences_with_style).strip() + " " + text if len(sentences_with_style) > 0 else text

        # if new_text != displayed_text:
        #     displayed_text = new_text
        #     clear_console()
        #     print(displayed_text, end="", flush=True)

    def process_text(text):
        print("2")
        print(text)
        # full_sentences.append(text)
        # text_detected("")

    recorder_config = {
        'model': 'tiny.en',
        'language': 'en',
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.4,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,
        "ensure_sentence_starting_uppercase": False,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.2,
        'realtime_model_type': 'tiny.en',
        'on_realtime_transcription_update': text_detected, 
        "input_device_index":1,
        "compute_type": "int8_float32",
        "beam_size_realtime": 5
        #'on_realtime_transcription_stabilized': text_detected,
    }

    recorder = AudioToTextRecorder(**recorder_config)

    clear_console()
    print("Say something...", end="", flush=True)

    while True:
        print("1")
        recorder.text(process_text)