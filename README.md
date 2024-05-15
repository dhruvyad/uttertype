# uttertype ([demo](https://www.youtube.com/watch?v=eSDYIFzU_fY))

<img src="./assets/sample_terminal.png" alt="alt text" style="width: 500px;"/>

## Setup

### 1. [Install PortAudio/PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
#### macOS
Installing portaudio on macOS can be somewhat tricky, especially on M1+ chips. In general, using conda seems to be the safest way to install portaudio
```
conda install portaudio
```
#### Windows
```
python -m pip install pyaudio
```
#### Linux
```
sudo apt-get install python3-pyaudio
```
### 2. Add a HotKey
For macOS, the hotkey is automatically set to the globe key by default (&#127760; bottom left key). For Windows and Linux, you will have to set up a custom hotkey for triggering recording, to do this edit the `hotkey` variable in `main.py`:
```python
from key_listener import HoldHotKey
...
hotkey = HoldHotKey(
      HoldHotKey.parse("<ctrl>+<alt>+v"),
      on_activate=transcriber.start_recording,
      on_deactivate=transcriber.stop_recording,
  )
```
For more context, view the [pynput documentation for using HotKeys](https://pynput.readthedocs.io/en/latest/keyboard.html#global-hotkeys) (HoldHotKey is extended from this class).

### 3. Install other dependencies
After cloning the repository, install requirements using
```shell
python -m pip install -r requirements.txt
```

### 4. Add OpenAI API key
Make sure that your OpenAI API key is available in the terminal environment either by directly exporting it as follows
```shell
export OPENAI_API_KEY=<your_openai_api_key>
```
or creating a `.env` file in the directory with the following content
```env
OPENAI_API_KEY=<your_openai_api_key>
```
### 5. Final run and permissions
Finally, run main.py
```shell
python main.py
```
When the program first runs, you will likely need to give it sufficient permissions. On macOS, this will include adding terminal to accessibility under `Privacy and Security > Accessibility`, giving it permission to monitor the keyboard, and finally giving it permission to record using the microphone.

## Usage
To start transcription, press and hold the registered hotkey to start recording. To stop the recording, lift your registered hotkey. On macOS, the registered hotkey is the globe icon by default. For other operating systems, this will have to by manually configured in `main.py` as described earlier.

### 3. Install other dependencies
After cloning the repository, install requirements using
```shell
python -m pip install -r requirements.txt
```

### 4. Add OpenAI API key
Make sure that your OpenAI API key is available in the terminal environment either by directly exporting it as follows for macOS/Linux
```shell
export OPENAI_API_KEY=<your_openai_api_key>
```
or as follows for Windows
```shell
$env:OPENAI_API_KEY = "<your_openai_api_key>"
```
or by creating a file named `.env` in the directory with the following text
```env
OPENAI_API_KEY=<your_openai_api_key>
```
### 5. Final run and permissions
Finally, run main.py
```shell
python main.py
```
When the program first runs, you will likely need to give it sufficient permissions. On macOS, this will include adding terminal to accessibility under `Privacy and Security > Accessibility`, giving it permission to monitor the keyboard, and finally giving it permission to record using the microphone.

## Usage
To start transcription, press and hold the registered hotkey to start recording. To stop the recording, lift your registered hotkey. On macOS, the registered hotkey is the globe icon by default. For other operating systems, this will have to by manually configured in `main.py` as described earlier.