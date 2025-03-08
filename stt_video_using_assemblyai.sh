#!/bin/bash

if ! command -v stt_assemblyai.py &> /dev/null
then
    echo 'The script stt_assemblyai.py is required to run this program. 
    It is not currently in your PATH. 
    Please ensure that it is available. 
    One way to do this is by cloning the repository
    https://github.com/CLIAI/handy_scripts 
    into a directory in your PATH.' >&2
    exit 1
fi

if [ $# -eq 0 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  echo "Usage: $0 video_file [expected_speakers [language code]]" >&2
  echo >&2
  echo "* video_file: The path to the video file you want to transcribe." >&2
  echo "* expected_speakers: The number of speakers in the video." >&2
  exit 1
fi

function extract_mp3() {
  local video="$1"
  local MP3="$2"
  if [ ! -f "$MP3" ]; then 
    set -x
    ffmpeg -i "$video" -vn -ab 128k -ar 44100 -y "$MP3"
    set +x
  else
    echo "File $MP3 already exists." >&2
  fi
}

function transcribe_with_diarization() {
  local expected_speakers="$1"
  local LANGUAGE="$2"
  local MP3="$3"
  local TXT="$4"
  
  # Always call stt_assemblyai.py - it will handle idempotence internally
  if [ "$expected_speakers" -eq 1 ]; then
    set -x
    stt_assemblyai.py -l "$LANGUAGE" -o "$TXT" "$MP3"
  elif [ "$expected_speakers" -ne 0 ]; then
    set -x
    stt_assemblyai.py -l "$LANGUAGE" -d -e "$expected_speakers" -o "$TXT" "$MP3"
  else
    set -x
    stt_assemblyai.py -l "$LANGUAGE" -d -o "$TXT" "$MP3"
  fi
  set +x
}

if [ $# -eq 0 ]; then
  echo "Usage: $0 video_file expected_speakers" >&2
  exit 0
fi

VIDEO="$1"
if [ ! -f "$VIDEO" ]; then
  echo "Video file $VIDEO does not exist." >&2
  exit 1
fi

expected_speakers="${2:-}"
if [ -z "$expected_speakers" ]; then
  read -p 'Expected speakers [0] (0==any):' expected_speakers
  expected_speakers="${expected_speakers:-2}"
fi

MP3="$VIDEO".mp3
TXT="$MP3".txt

LANGUAGE="${3:-}"
if [ -z "$LANGUAGE" ]; then
  read -p 'Language code [en]:' LANGUAGE
  LANGUAGE="${LANGUAGE:-en}"
fi

# Extract MP3 if needed
extract_mp3 "$VIDEO" "$MP3"

# Transcribe using AssemblyAI
# stt_assemblyai.py will handle idempotence - if transcript exists, it will display it
transcribe_with_diarization "$expected_speakers" "$LANGUAGE" "$MP3" "$TXT"

# Display a message indicating completion
if [ -f "$TXT" ]; then
  echo "Transcript is available at: $TXT" >&2
  
  # Only print the transcript if it wasn't already printed by stt_assemblyai.py
  # We can check if the transcript was just created by comparing timestamps
  if [ -s "$TXT" ] && [ "$TXT" -ot "$MP3" ]; then
    cat "$TXT"
  fi
fi
