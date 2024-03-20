# uttertype

<img src="./assets/sample_terminal.png" alt="alt text" style="width: 500px;"/>

## Setup
After cloning the repository, install requirements using
```shell
pip install -r requirements.txt
```
Then, make sure that your OpenAI API key is available in the environment either by directly exporting it as follows
```shell
export OPENAI_API_KEY=<your_openai_api_key>
```
or creating a `.env` file in the directory with the following content
```env
OPENAI_API_KEY=<your_openai_api_key>
```
Finally, run main.py
```shell
python main.py
```

### Custom Hotkey
If you'd like to set up a custom hotkey for triggering recording, edit the `hotkey` variable in `main.py`:
```python
from key_listener import HoldHotKey
...
hotkey = HoldHotKey(
      HoldHotKey.parse("<ctrl>+<alt>+v")
      on_activate=transcriber.start_recording,
      on_deactivate=transcriber.stop_recording,
  )
```
For more context, view the [pynput documentation for using HotKeys](https://pynput.readthedocs.io/en/latest/keyboard.html#global-hotkeys) (HoldHotKey is extended from this class).
