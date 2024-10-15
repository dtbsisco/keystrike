## Features

- **Automatic Message Sending**: Sends a sequence of predefined messages at set intervals.
- **User-Friendly GUI**: A clean and intuitive interface using Tkinter for easy configuration and message input.
- **Hotkey Support**: Default hotkeys are set to F8 (start) and F9 (stop), which can be customized through the settings menu.
- **Settings Persistence**: Hotkey settings are saved in a `settings.ini` file, so you don’t have to reconfigure them each time.
- **Load Messages from File**: You can load message sequences from text files for ease of use.

## Installation

1. **Requirements**: To run the program, you’ll need Python 3.x and the following packages:
   - `keyboard`
   - `plyer`
   - `tkinter` (usually included with Python)
   - `configparser`
   - `requests`
   
   Install the required packages by running:

   ```bash
   pip install keyboard plyer requests
   ```
2. **Clone the Repository**: Download the source code by cloning the repository:

   ```bash
    git clone https://github.com/dtbsisco/Keystrike.git
    cd Keystrike

3. **Run Keystrike**: Start the program by executing the following command:

   ```bash
    python keystrike.py or .\keystrike.py
