# handy_scripts

Collection of handy CLI AI scripts, experiments with AI (Dialogs)
to make them, and reasearchy notes.

If you like scripts so much, you can always add to PATH (e.g. .bashrc),
to have them always at hand in termianl :).

Maybe in future will update list of contents automatically,
now I hope that names will be self descriptive,
and script inside having enough descriptions.

Let me mention some:

* 2023-05-19 LLms🤖 nad Literate  Programming (🙏Donald Knuth) - 🤝Synergy Potential,
  as similar to Chain-of-Thought:
    * [Literate Style Co-programming with GPT-4 as a Copilot: An Experiment and Study](pdfs/23/LLM_and_Literate_Programming/Literate_Programming_Experiment_with_GPT4.pdf) or  [markdown](openai_whisper_transcription.dialog.md),
    * [Produced Script](openai_whisper_transcription.sh) and produced [README.md](openai_whisper_transcription-README.md),
      - hopefully also handy e.g. to convert your brainstorming voice notes,
        or audio from video lectures for later LLM processing.

# `openai_tts_cli.py`

Use Openai TTS to record and output to : stdout, file or clipboard (Linux).

Of course requires `OPENAI_API_KEY` environment variable.

```
github/CLIAI/handy_scripts$ openai_stt_cli.py -h
usage: openai_stt_cli.py [-h] [-s] [-o OUTPUT] [-a APPEND] [-c]

OpenAI STT/ASR CLI (Voice to Text)

options:
  -h, --help            show this help message and exit
  -s, --silent          Run in silent mode without prompt
  -o OUTPUT, --output OUTPUT
                        Specify output file for transcript
  -a APPEND, --append APPEND
                        Specify output file to append transcript
  -c, --clipboard       Copy result to clipboard using xclip

```
## Repository Contents Overview

This repository contains a collection of scripts, tools, and documentation related to speech-to-text (STT), text-to-speech (TTS), and other language processing utilities using OpenAI's APIs.

### Scripts and Tools

- `deepl`: A directory containing scripts for DeepL translation services.
- `download_cool_models.sh`: A script to download models for language processing.
- `monitor_clipboard_and_translate.sh`: A script that monitors the clipboard for text to translate.
- `openai_docs_samples`: A directory with examples and sample inputs for TTS.
- `openai_stt_cli.py`: A command-line interface for OpenAI's speech-to-text service.
- `openai_tts_from_file.py`: A script to convert text from a file to speech using OpenAI's TTS.
- `openai_whisper_transcription.sh`: A script to transcribe audio files using OpenAI's Whisper model.
- `record_and_transcribe_using_openai_whisper_api.sh`: A script to record audio and transcribe it using OpenAI's Whisper API.
- `stt_assemblyai.py`: A script to transcribe audio files using AssemblyAI's STT service.

### Documentation

- `openai_whisper_transcription-README.md`: Documentation for the OpenAI Whisper transcription script.

### PDFs and Documentation

- `pdfs/23/LLM_and_Literate_Programming`: A directory containing PDFs and Markdown files related to literate programming experiments with GPT-4.

### Miscellaneous

- `.gitignore`: A file specifying untracked files to ignore.
- `LICENSE`: The license file for the repository.
- `test`: A directory for test scripts and data.
- `test`: A directory for test scripts and data used for verifying the functionality of the scripts.

For more detailed information on each item, please refer to the respective files and directories.
