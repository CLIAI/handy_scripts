---
author: OpenAI GPT-4
date: 2023-05-19
filename: README.md
---


# OpenAI Whisper Transcript Generator

This is a Bash script that uses the OpenAI Whisper API to transcribe audio files. It supports various input file formats, includes file chunking for larger inputs, and provides detailed error logging.

## Requirements

* ffmpeg
* curl
* jq (for parsing JSON responses)

You can install these with the following command (for Arch Linux):

`sudo pacman -S ffmpeg curl jq` 

## Features

- Environment variable for OpenAI token (`OPENAI_API_KEY`). If not defined, the script will notify the user.
- Support for different output modes: file output (`-o outputfile`) and standard output (`-stdout` or `-so`). If both are specified, the script will save to a file and output to stdout.
- Help message provided if no parameters are supplied or if "-h" or "--help" is used.
- Detection of input file format and conversion to a format accepted by Whisper (if necessary).
- Logging of billing information into a specific log file. The log file path can be specified by the environment variable `OPENAI_WHISPER_BILLING_LOG`. If not defined, the default log file will be `"${HOME}/.openai_whisper_billing.log"`.
- Optional flag `-p`/`--prompt` to specify a prompt to improve transcription quality.
- Optional flag `--promptfile` to specify a text file containing the prompt.
- Optional flag `-l`/`--lang`/`--language` to specify the language of the input audio.
- If interrupted with Ctrl-C, captures signal with a trap and removes temporary files.

## Usage

bashCopy code

`./whisper_transcript.sh -o outputfile inputfile` 

For detailed usage instructions, use the help command:

bashCopy code

`./whisper_transcript.sh -h` 

## Note

For input files larger than 25MB, the script will automatically split the file into chunks of 20MB each (at most) and generate separate output files for each chunk.
