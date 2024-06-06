# Stage Assistant Backend

This directory contains the code for the backend of the Stage Assistant application.

## Directory Structure

- `/broker` contains the MQTT broker.
- `/GUI` contains the backend configuration UI. Please note that parts of the UI may be slow to load.
- `/server` contains the REST API, WebSockets, and MicroServices located inside `/server/grpc`.

### Additional Directories

- `/server/storage` contains the PDF texts, cues, and transcriptions.
- `settings.json` contains all the backend settings.
- `.env` should be provided with the IP and PORT for the MQTT BROKER:
  ```bash
  export HIVEMQ_PORT=1883
  export HIVEMQ_IP=0.0.0.0
    ```
## Setup Instructions

### Virtual Environment

It is recommended to create a virtual environment in this directory with Python 3.12. To activate the virtual environment you created, run:
```bash source .venv/bin/activate ```

### Dependencies

You can install all the Python dependencies with:
```bash pip install -r requirements.txt ```

Additionally, you will need to install `python-tk` and `mosquitto`.

On macOS, this can be done with:
```bash 
brew install python-tk
brew install mosquitto
```

On macOS and Linux, you will need to install:
```bash brew install portaudio ```

On NVIDIA systems, you will also need to install:
- `cuBLAS for CUDA 11`
- `cuDNN 8 for CUDA 11`

To use the performer tracker, you will also need to install `deep-person-reid`:
```bash git clone https://github.com/KaiyangZhou/deep-person-reid.git 
 cd deep-person-reid/ 
 python setup.py develop
 ``` 

To run the backend server, you will need to install `npm` and `nodejs`. Please follow the instructions applicable for your system.

Once installed, you will need to install the node packages:
```bash npm install ```

You will also need to install a Java Runtime Environment on your system to run HiveMQTT.

Finally, you will need to download `osnet_x1_0` from the torchreid model zoo and place it inside `/models`:
[osnet_x1_0 Model](https://kaiyangzhou.github.io/deep-person-reid/MODEL_ZOO)
