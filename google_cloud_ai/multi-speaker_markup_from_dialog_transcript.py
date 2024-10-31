#!/usr/bin/env python3

# Generate dialogue with multiple speakers
# https://cloud.google.com/text-to-speech/docs/create-dialogue-with-multispeakers

import argparse
import sys
import os
from google.cloud import texttospeech

def log_verbose(message):
    if args.verbose:
        print(message, file=sys.stderr)

def parse_input(input_file):
    speakers = {}
    turns = []
    last_speaker = None

    for line in input_file:
        line = line.strip()
        if line:
            if ':' in line:
                speaker, text = line.split(':', 1)
                speaker = speaker.strip()
                text = text.strip()

                if speaker not in speakers:
                    if len(speakers) >= len(args.speakers):
                        raise ValueError("More than {} speakers detected in the input.".format(len(args.speakers)))
                    speakers[speaker] = args.speakers[len(speakers)]
                    if args.verbose:
                        print('DEB:SPEAKER[{}]="{}"'.format(speaker, speakers[speaker]), file=sys.stderr)
            else:
                text = line
                speaker = last_speaker

            turn = texttospeech.MultiSpeakerMarkup.Turn()
            turn.text = text
            turn.speaker = speakers[speaker]
            turns.append(turn)
            last_speaker = speaker

            if args.verbose > 1:
                print('APPEND:[{} as "{}"]:{}'.format(speaker, speakers[speaker], text), file=sys.stderr)

    return turns

def generate_audio(turns):
    client = texttospeech.TextToSpeechClient()
    
    multi_speaker_markup = texttospeech.MultiSpeakerMarkup()
    multi_speaker_markup.turns.extend(turns)
    
    synthesis_input = texttospeech.SynthesisInput(multi_speaker_markup=multi_speaker_markup)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Studio-MultiSpeaker"
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    return response.audio_content

def main():
    global args
    parser = argparse.ArgumentParser(description="Generate multi-speaker audio from input text.")
    parser.add_argument("-i", "--input", required=True, help="Input file (use '-' for stdin)")
    parser.add_argument("-s", "--speakers", default="R,S,T,U", help="Speaker mapping (comma-separated)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Enable verbose logging")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Run the script without generating or writing audio")
    args = parser.parse_args()

    args.speakers = args.speakers.split(',')

    if args.input == '-':
        input_file = sys.stdin
        output_file = "output.mp3"
    else:
        input_file = open(args.input, 'r')
        output_file = args.input + ".mp3"

    if os.path.exists(output_file):
        print(f"SKIPPING:ALREADY_EXISTS:{output_file}")
        sys.exit(1)

    log_verbose(f"Processing input from {args.input}")
    turns = parse_input(input_file)
    
    if not args.dry_run:
        log_verbose("Generating audio")
        audio_content = generate_audio(turns)

        log_verbose(f"Writing audio to {output_file}")
        with open(output_file, "wb") as out:
            out.write(audio_content)

        print(f'Audio content written to file "{output_file}"')
    else:
        print("Dry run completed. No audio generated or written.")

if __name__ == "__main__":
    main()

# This script does the following:
# 
# 1. It uses argparse to handle command-line arguments, including -i/--input, --speakers, -v/--verbose, and -n/--dry-run.
# 2. It reads the input file (or stdin if '-' is specified) and parses it into a list of turns.
# 3. It maps the first four encountered speakers to the specified speaker names (default R,S,T,U).
# 4. It generates the audio using the Google Cloud Text-to-Speech API.
# 5. It checks if the output file already exists before writing, and exits with an error if it does.
# 6. It writes the generated audio to the output file.
# 7. It includes verbose logging when the -v flag is used.
# 8. It includes a dry-run mode that runs the script without generating or writing audio when the -n flag is used.
# 
# To use this script, you would run it like this:
# 
# ```
# python3 script.py -i input.txt
# ```
# 
# Or with custom speakers, verbose logging, and dry-run mode:
# 
# ```
# python3 script.py -i input.txt --speakers A,B,C,D -v -n
# ```
# 
# Make sure you have the Google Cloud Text-to-Speech client library installed (`pip install google-cloud-texttospeech`) and that you have set up your Google Cloud credentials before running the script.
# 
