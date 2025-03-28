# Hermine

<img src="img/logo.jpg" alt="Hermine" width="300" />

Hermine is a versatile assistant created to enhance your Linux experience. It provides a suite of powerful tools designed to automate your daily tasks.

## Installation

### Requirements
- Python
- virtualenv
- pip
- Linux-based operating system

### Setup
1. Clone the repository
    ```bash
    git clone git@github.com:melvinredondotanis/hermine.git
    ```
2. Launch the installation:
    ```bash
    cd hermine
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3. Export in your environment the OpenAI API key:
    ```bash
    export OPENAI_API_KEY=your-api-key
    ```
4. Run the application:
    ```bash
    python3 main.py
    ```

## Features
- [x] OpenAI GPT-4o-mini integration
- [X] OpenAI Whisper integration
- [X] OpenAI STT integration
- [X] Screen capture
- [X] Screen lock
- [X] File search
- [X] File creation

## Authors
- [Melvin Redondo--Tanis]('mailto:melvin@redondotanis.com')
