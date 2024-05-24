import pyaudio
import logging
import traceback

@staticmethod
def audio_data_worker(audio_queue,
                        sample_rate,
                        buffer_size,
                        input_device_index,
                        shutdown_event,
                        interrupt_stop_event,
                        use_microphone):
    """
    Worker method that handles the audio recording process.

    This method runs in a separate process and is responsible for:
    - Setting up the audio input stream for recording.
    - Continuously reading audio data from the input stream
        and placing it in a queue.
    - Handling errors during the recording process, including
        input overflow.
    - Gracefully terminating the recording process when a shutdown
        event is set.

    Args:
        audio_queue (queue.Queue): A queue where recorded audio
            data is placed.
        sample_rate (int): The sample rate of the audio input stream.
        buffer_size (int): The size of the buffer used in the audio
            input stream.
        input_device_index (int): The index of the audio input device
        shutdown_event (threading.Event): An event that, when set, signals
            this worker method to terminate.

    Raises:
        Exception: If there is an error while initializing the audio
            recording.
    """
    try:
        audio_interface = pyaudio.PyAudio()
        stream = audio_interface.open(
            rate=sample_rate,
            format=pyaudio.paInt16,
            channels=1,
            input=True,
            frames_per_buffer=buffer_size,
            input_device_index=input_device_index,
            )

    except Exception as e:
        logging.exception("Error initializing pyaudio "
                            f"audio recording: {e}"
                            )
        raise

    logging.debug("Audio recording (pyAudio input "
                    "stream) initialized successfully"
                    )

    try:
        while not shutdown_event.is_set():
            try:
                data = stream.read(buffer_size)

            except OSError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    logging.warning("Input overflowed. Frame dropped.")
                else:
                    logging.error(f"Error during recording: {e}")
                tb_str = traceback.format_exc()
                print(f"Traceback: {tb_str}")
                print(f"Error: {e}")
                continue

            except Exception as e:
                logging.error(f"Error during recording: {e}")
                tb_str = traceback.format_exc()
                print(f"Traceback: {tb_str}")
                print(f"Error: {e}")
                continue

            if use_microphone.value:
                audio_queue.put(data)

    except KeyboardInterrupt:
        interrupt_stop_event.set()
        logging.debug("Audio data worker process "
                        "finished due to KeyboardInterrupt"
                        )
    finally:
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()