#!/bin/bash

#source /home/gw-t490/.bashrc

#set -x

# Step 1: Open a new terminal window to record audio using xterm with a larger font
TEMP_AUDIO_FILE="/tmp/recording_$(date +%s).wav"
TEMP_MP3_FILE="/tmp/recording_$(date +%s).mp3"

# Start arecord in xterm with the larger font
echo "Recording..."
#xterm -fn '10x20' -e "arecord -f cd ${TEMP_AUDIO_FILE}" &
#arecord -f cd "${TEMP_AUDIO_FILE}"
arecord --quiet -f cd "${TEMP_AUDIO_FILE}"

# Give some time for the terminal to open and for arecord to start
#sleep 2

# Step 2: Wait for the audio recording to finish
#echo "waiting for arecord in separate window to finish..."
#while pgrep -x "arecord" > /dev/null; do
#    sleep 0.1
#done

# Once arecord stops, convert the WAV to MP3
echo "Converting to mp3..."
lame --quiet "${TEMP_AUDIO_FILE}" "${TEMP_MP3_FILE}"

# Transcribe the audio
function transcribe() {
    local P_INPUT_FILE="$1"
    openai_whisper_api='openai_whisper_transcription.sh'
    #openai_whisper_api='/home/gw-t490/github/CLIAI/handy_scripts/openai_whisper_transcription.sh'
    ${openai_whisper_api} -l en "${P_INPUT_FILE}"  # Removed the -o option
}

echo "Transcribing..."
transcribe "${TEMP_MP3_FILE}"

# Compute the path of the .txt output file
OUTPUT_TXT_FILE="${TEMP_MP3_FILE}.txt"

# Step 3: Copy the transcription to the clipboard
cat "${OUTPUT_TXT_FILE}" | xclip -sel clipboard

set +x

echo -e "\nTranscribed output copied to clipboard:\n"
cat "${OUTPUT_TXT_FILE}"

# Cleanup the temporary files
rm "${TEMP_AUDIO_FILE}" "${TEMP_MP3_FILE}" "${OUTPUT_TXT_FILE}"

echo -e "-\nTranscription complete and copied to clipboard."
sleep 5


