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

See the [uv installation documentation](https://docs.astral.sh/uv/getting-started/installation/).

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


### 4. Configure Speech Recognition Settings

You can configure uttertype to work with either OpenAI's Whisper API, Google's Gemini API, or a local Whisper server. 

#### Choose Speech Recognition Provider

Select the provider you want to use by setting the `UTTERTYPE_PROVIDER` environment variable:

```env
# OpenAI Whisper (default)
UTTERTYPE_PROVIDER="openai"

# Google Gemini
UTTERTYPE_PROVIDER="google"
```

#### Option A: Using a .env file (Recommended)
Create a `.env` file in the project directory with the settings for your chosen provider:

```env
# For OpenAI Whisper:
OPENAI_API_KEY="sk-your-key-here"
OPENAI_BASE_URL="https://api.openai.com/v1"  # optional
OPENAI_MODEL_NAME="whisper-1"  # optional

# For Google Gemini:
GEMINI_API_KEY="your-api-key-here"  # For Gemini developer API
GEMINI_MODEL_NAME="gemini-2.0-flash"  # optional

# For Google Vertex AI (enterprise):
GEMINI_USE_VERTEX="true"
GEMINI_PROJECT_ID="your-gcp-project-id"
GEMINI_LOCATION="us-central1"  # optional
# Note: Authentication with gcloud is required for Vertex AI
```

#### Option B: Using Environment Variables
You can also set these values directly in your terminal:

For OpenAI (Linux/macOS):
```shell
export UTTERTYPE_PROVIDER="openai"
export OPENAI_API_KEY="sk-your-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # optional
export OPENAI_MODEL_NAME="whisper-1"  # optional
```

For Gemini (Linux/macOS):
```shell
export UTTERTYPE_PROVIDER="google"
export GEMINI_API_KEY="your-api-key-here"
# or for Vertex AI
export GEMINI_USE_VERTEX="true"
export GEMINI_PROJECT_ID="your-gcp-project-id"
```

For Windows, use `$env:` instead of `export`.

See [`.sample_env`](.sample_env) in the repository for example configurations.

#### Using Google Vertex AI
When using Google Vertex AI, you need to authenticate with gcloud:

1. Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. Authenticate using `gcloud auth application-default login`
3. Make sure your account has the necessary permissions for Vertex AI

For more information, see the [Vertex AI Authentication documentation](https://cloud.google.com/vertex-ai/docs/authentication).

#### Using a Local Whisper Server
For faster and cheaper transcription, you can set up a local [faster-whisper-server](https://github.com/fedirz/faster-whisper-server). When using a local server:

1. Set `UTTERTYPE_PROVIDER="openai"` to use the OpenAI compatible interface
2. Set `OPENAI_BASE_URL` to your server's address (e.g., `http://localhost:7000/v1`)
3. Choose from supported local models like:
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
