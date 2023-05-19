#!/bin/bash

# Script made as experiment analysing how Literate Programming
# by Donald Knuth, can be turned into Chain-of-Thought Prompting
# when co-programming with GPT-4.

# This script transcribes audio files using the OpenAI Whisper API. It supports various audio formats,
# handles large files by chunking them, and provides detailed error and billing logging.

# We use getopts to parse command-line options.
# The options are:
#   -o: Specify the output file. If not provided, the script will print the help message.
#   -so or -stdout: Print the transcription to the standard output.
#   -p or --prompt: Specify a prompt to improve the transcription quality.
#   -l or --lang or --language: Specify the language of the input audio.
#   -h or --help: Print the help message.

print_help() {
  echo "Usage: ./whisper_transcript.sh [-o outputfile] [-so | --stdout] [-p prompt | --promptfile promptfile] [-l lang | --lang lang | --language lang] inputfile"
  echo
  echo "Transcribes an audio file using the OpenAI Whisper API."
  echo
  echo "Options:"
  echo "  -o, --output        Specify the output file. Required unless -so or --stdout is used."
  echo "  -so, --stdout       Print the transcription to the standard output."
  echo "  -p, --prompt        Specify a prompt to improve the transcription quality."
  echo "  --promptfile        Specify a text file containing the prompt."
  echo "  -l, --lang, --language  Specify the language of the input audio."
  echo "  -h, --help          Print this help message."
  echo
  echo "If the OPENAI_API_KEY environment variable is not defined, the script will fail with an error message."
  echo "Billing information is logged to the file specified by the OPENAI_WHISPER_BILLING_LOG environment variable,"
  echo "or to '${HOME}/.openai_whisper_billing.log' if the variable is not defined."
}

# Check if the OPENAI_API_KEY environment variable is defined. If not, print an error message and exit.
if [ -z "${OPENAI_API_KEY}" ]; then
  echo "ERROR: The OPENAI_API_KEY environment variable is not defined. Please set it to your OpenAI API key." >&2
  exit 1
fi

# Parse options.
OUTPUT_FILE=""
PRINT_TO_STDOUT=0
PROMPT=""
PROMPT_FILE=""
LANGUAGE=""

while getopts "o:sp:l:h-:" opt; do
  case ${opt} in
    o)
      OUTPUT_FILE="${OPTARG}"
      ;;
    s)
      PRINT_TO_STDOUT=1
      ;;
    p)
      PROMPT="${OPTARG}"
      ;;
    l)
      LANGUAGE="${OPTARG}"
      ;;
    h)
      print_help
      exit 0
      ;;
    -)
      case "${OPTARG}" in
        output)
          OUTPUT_FILE="${!OPTIND}"; OPTIND=$(( OPTIND + 1 ))
          ;;
        stdout)
          PRINT_TO_STDOUT=1
          ;;
        prompt)
          PROMPT="${!OPTIND}"; OPTIND=$(( OPTIND + 1 ))
          ;;
        promptfile)
          PROMPT_FILE="${!OPTIND}"; OPTIND=$(( OPTIND + 1 ))
          ;;
        lang|language)
          LANGUAGE="${!OPTIND}"; OPTIND=$(( OPTIND + 1 ))
          ;;
        help)
          print_help
          exit 0
          ;;
        *)
          echo "ERROR: Invalid option --${OPTARG}" >&2
          print_help
          exit 1
          ;;
      esac
      ;;
    \?)
      echo "ERROR: Invalid option -${OPTARG}" >&2
      print_help
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

# Check if an input file was provided. If not, print an error message and exit.
if [ $# -eq 0 ]; then
  echo "ERROR: No input file provided." >&2
  print_help
  exit 1
fi

INPUT_FILE="$1"

# Set default output files if not provided
OUTPUT_FILE="${OUTPUT_FILE:-${INPUT_FILE}.json}"
SINGLE_OUTPUT_FILE="${SINGLE_OUTPUT_FILE:-${INPUT_FILE}.txt}"

# Check if the input file exists. If not, print an error message and exit.
if [ ! -f "${INPUT_FILE}" ]; then
  echo "ERROR: The input file '${INPUT_FILE}' does not exist." >&2
  exit 1
fi

# If the user specified a prompt file, check if it exists. If not, print an error message and exit.
if [ -n "${PROMPT_FILE}" ]; then
  if [ ! -f "${PROMPT_FILE}" ]; then
    echo "ERROR: The prompt file '${PROMPT_FILE}' does not exist." >&2
    exit 1
  fi
fi


# Define the path to the directory where we'll store the temporary files.
TMP_DIR="/tmp/whisper_transcript_${RANDOM}"

# Create a temporary directory for the audio chunks.
TMP_DIR=$(mktemp -d)
echo "Using temporary directory ${TMP_DIR}"

# Set up a trap to clean up the temporary directory on Ctrl-C.
trap 'echo "Interrupted. Cleaning up..."; rm -rf "${TMP_DIR}"; exit 1' INT


# Convert the input file to WAV format and split it into chunks of 30 seconds each.
# We use the WAV format because it's a common, uncompressed audio format that should work with the Whisper API.
# We split the input file into chunks because the Whisper API has a maximum length limit for audio inputs.
#ffmpeg -i "${INPUT_FILE}" -f segment -segment_time 30 -acodec pcm_s16le -ar 16000 -ac 1 -vn "${TMP_DIR}/input-%03d.wav" > /dev/null 2>&1
ffmpeg -i "${INPUT_FILE}" -f segment -segment_time 600 -b:a 128k -vn -map 0:a "${TMP_DIR}/input-%03d.mp3"


if [ $? -ne 0 ]; then
  echo "ERROR: Failed to convert and split the input file." >&2
  exit 1
fi


check_if_mp3_chunks_are_present() {
  local mp3_files_count=$(ls ${TMP_DIR}/*.mp3 2> /dev/null | wc -l)
  
  if (( mp3_files_count == 0 )); then
    echo "ERROR: No MP3 files found in the temporary directory. Please check the input file and splitting process." >&2
    echo "Contents of the temporary directory:" >&2
    ls -l ${TMP_DIR} >&2
    exit 1
  fi
}

transcribe_chunk() {
    local chunkno="${1}"
    local chunkfile="${TMP_DIR}/input-${chunkno}.mp3"
    local chunksize=$(du -k "${chunkfile}" | cut -f1)
    local chunkduration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${chunkfile}")

    # Round the duration to the nearest whole number
    encoded_seconds=$(printf "%.0f" "$chunkduration")

    local resultfile="${OUTPUT_FILE%.json}-${chunkno}.json"
    local resultfiletxt="${OUTPUT_FILE%.json}-${chunkno}.txt"

    # Check if output files for this chunk already exist
    if [[ -e "${resultfile}" ]]; then
        echo "INFO: The output JSON file ${resultfile} for chunk ${chunkno} already exists. Skipping this chunk." >&2
        return 0
    fi

    if [[ -e "${resultfiletxt}" ]]; then
        echo "INFO: The output text file ${resultfiletxt} for chunk ${chunkno} already exists. Skipping this chunk." >&2
        return 0
    fi

    echo "DEBUG: chunkno = ${chunkno}, chunkfile = ${chunkfile}, resultfile = ${resultfile}" >&2

    curl -X POST "https://api.openai.com/v1/audio/transcriptions" \
        -H "Authorization: Bearer ${OPENAI_API_KEY}" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@${chunkfile}" \
        -F "model=whisper-1" \
        -o "${resultfile}"

    local status=$?
    if [ $status -ne 0 ]; then
        echo "ERROR: Failed to transcribe chunk ${chunkno}. Status: ${status}"
        return $status
    fi

    jq -r .text < "${resultfile}" > "${resultfiletxt}"

    # Add the billing logging here.
    local iso8601_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "${iso8601_timestamp}, ${encoded_seconds}, ${INPUT_FILE}" >> "${OPENAI_WHISPER_BILLING_LOG:-${HOME}/.openai_whisper_billing.log}"
}


# Get number of chunks
chunks=$(ls ${TMP_DIR}/input-*.mp3 | wc -l)

# Sanity check
check_if_mp3_chunks_are_present

# Transcribe each chunk
echo "DEBUG: OUTPUT_FILE = ${OUTPUT_FILE}" >&2
for (( i=0; i<$chunks; i++ )); do
  transcribe_chunk $(printf "%03d" $i) $PROMPT_FILE $LANG_FLAG
done



# Clean up the temporary directory.
rm -rf "${TMP_DIR}"


# Print a success message and exit.
echo "Successfully transcribed the audio file."
exit 0

