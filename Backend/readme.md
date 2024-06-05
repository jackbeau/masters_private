brew install python-tk
brew install mosquitto


source .venv/bin/activate
pip install -r requirements.txt 



actual list


pip install -r requirements.txt

git clone https://github.com/KaiyangZhou/deep-person-reid.git
cd deep-person-reid/
python setup.py develop



also package.json for API

# Setup instructions

## Poetry setup

Poetry is used in this project for dependency management.

Install it via pip or pip x.

Set it to save virual environments form within the project folder with

`poetry config virtualenvs.in-project true`

You might need to also run

`poetry install` in the project folder

You can list all poetry virtual environments with

`poetry env list`

You can run a commmand through the environment with

`poetry run [COMMAND]`

Or install packages with

`poetry add [pip package]`

## Managing virtual envrionments

If the python executable is in the PATH, you can use it with

`poetry env use python3.7`

To use the default system behaviour

`poetry env use system`

Get environment information with

`poetry env info`

## Dependencies

OCRmyPDF - with only English language pack

`brew install ocrmypdf`

If this does not work in Python - figure out why - the below should now be part of the poetry project, check the above is not needed anymore (tesseract probably will still need installing via brew)

`brew update`

`brew install tesseract-lang`

`pip install --upgrade pip`

`pip install --user ocrmypdf`

Note:

On macOS and Linux, you will need to install
`brew install portaudio`

On NVIDIA you will also need to install
`cuBLAS for CUDA 11 and cuDNN 8 for CUDA 11`