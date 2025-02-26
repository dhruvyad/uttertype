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
For macOS, the hotkey is automatically set to the globe key by default (&#127760; bottom left key). For Windows and Linux, you can configure the hotkey by setting the `UTTERTYPE_RECORD_HOTKEYS` environment variable in `.env`:
```env
UTTERTYPE_RECORD_HOTKEYS="<ctrl>+<alt>+v"
```

For more context, view the [pynput documentation for using HotKeys](https://pynput.readthedocs.io/en/latest/keyboard.html#global-hotkeys) (HoldHotKey is extended from this class).

### 3. Install Dependencies
Choose one of the following methods to install the required dependencies:

#### Option A: Using uv (Recommended)
First, install uv if you haven't already:
```shell
pip install uv
```

Then, create a virtual environment and install dependencies:
```shell
uv sync
```

This will:
- Create a virtual environment in `.venv`
- Install all dependencies specified in pyproject.toml
- Install the uttertype package in development mode

Activate the virtual environment:
```shell
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate     # On Windows
```

#### Option B: Using pip
```shell
pip install -e .
```


If during/after installation on Linux you see error similar to:
```
ImportError: /home/soul/anaconda3/lib/libstdc++.so.6: version `GLIBCXX_3.4.32' not found (required by /lib/x86_64-linux-gnu/libjack.so.0)
```
Check out [StackOverflow](https://stackoverflow.com/questions/72540359/glibcxx-3-4-30-not-found-for-librosa-in-conda-virtual-environment-after-tryin) and [Berkley](https://bcourses.berkeley.edu/courses/1478831/pages/glibcxx-missing)


### 4. Configure OpenAI Settings

You can configure uttertype to work with either OpenAI's official API or a local Whisper server. There are two ways to set this up:

#### Option A: Using a .env file (Recommended)
Create a `.env` file in the project directory with these settings:

```env
# 1. Required: Your API key
OPENAI_API_KEY="sk-your-key-here"

# 2. Optional: Choose your API endpoint
# For OpenAI's official API (default):
OPENAI_BASE_URL="https://api.openai.com/v1"
# OR for a local [Faster Whisper server](https://github.com/fedirz/faster-whisper-server):
OPENAI_BASE_URL="http://localhost:7000/v1"

# 3. Optional: Select your preferred model
# For OpenAI's official API:
OPENAI_MODEL_NAME="whisper-1"
# OR for local Whisper server, some options include:
OPENAI_MODEL_NAME="Systran/faster-whisper-small"
OPENAI_MODEL_NAME="Systran/faster-distil-whisper-large-v3"
OPENAI_MODEL_NAME="deepdml/faster-whisper-large-v3-turbo-ct2"
```

#### Option B: Using Environment Variables
You can also set these values directly in your terminal:

For Linux/macOS:
```shell
export OPENAI_API_KEY="sk-your-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1" # optional
export OPENAI_MODEL_NAME="whisper-1" # optional
```

For Windows:
```shell
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"  # optional
$env:OPENAI_MODEL_NAME = "whisper-1"  # optional
```

See [`.sample_env`](.sample_env) in the repository for example configurations.

#### Using a Local Whisper Server
For faster and cheaper transcription, you can set up a local [faster-whisper-server](https://github.com/fedirz/faster-whisper-server). When using a local server:

1. Set `OPENAI_BASE_URL` to your server's address (e.g., `http://localhost:7000/v1`)
2. Choose from supported local models like:
   - `Systran/faster-whisper-small` (fastest)
   - `Systran/faster-distil-whisper-large-v3` (most accurate)
   - `deepdml/faster-whisper-large-v3-turbo-ct2` (almost as good, but faster)

### 5. Final run and permissions
Finally, run the application using one of these methods:

```shell
# Method 1: Run directly from project root
python -m uttertype.main

# Method 2: Run the wrapper script (simplest)
python main.py

# Method 3: Run the installed command (after activating virtual environment)
uttertype

# Method 4: Run with tmux (starts in background, auto-creates uv environment)
./start_uttertype.sh
```

When the program first runs, you will likely need to give it sufficient permissions. On macOS, this will include adding terminal to accessibility under `Privacy and Security > Accessibility`, giving it permission to monitor the keyboard, and finally giving it permission to record using the microphone.

## Usage
To start transcription, press and hold the registered hotkey to start recording. To stop the recording, lift your registered hotkey. On macOS, the registered hotkey is the globe icon by default. For other operating systems, this will have to by manually configured in `main.py` as described earlier.
