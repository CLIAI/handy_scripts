#!/usr/bin/env python
import os
import requests
import time
import argparse
import sys

import subprocess

def upload_file(api_token, audio_input):
    if audio_input.startswith('http://') or audio_input.startswith('https://'):
        return audio_input
    url = 'https://api.assemblyai.com/v2/upload'
    headers = {
        'authorization': api_token,
        'content-type': 'application/octet-stream'
    }
    try:
        with open(audio_input, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        response.raise_for_status()
        upload_url = response.json()['upload_url']
        if args.verbose:
            print(f"File uploaded. URL: {upload_url}")
        return upload_url
    except Exception as e:
        print(f"Error in upload_file: {e}")
        if response:
            print(f"REST RESPONSE: {response.text}")
        raise

def create_transcript(api_token, audio_url, speaker_labels):
    url = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "authorization": api_token,
        "content-type": "application/json"
    }
    data = {
        "audio_url": audio_url,
        "speaker_labels": speaker_labels,
    }
    if args.language != 'auto':
        data["language_code"] = args.language
    if args.expected_speakers != -1:
        data["speakers_expected"] = args.expected_speakers
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        transcript_id = response.json()['id']
        if args.verbose:
            print(f"Transcript ID: {transcript_id}")
        
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        while True:
            response = requests.get(polling_endpoint, headers=headers)
            response.raise_for_status()
            transcription_result = response.json()
            status = transcription_result['status']
            if args.verbose:
                print(f"Current status: {status}")
            if status == "completed":
                return transcription_result
            elif status == "error":
                raise Exception(f"Transcription failed: {transcription_result['error']}")
            elif status in ["queued", "processing"]:
                time.sleep(5)
            else:
                raise Exception(f"Unknown status: {status}")
    except Exception as e:
        print(f"Error in create_transcript: {e}")
        if response:
            print(f"REST RESPONSE: {response.text}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio file using AssemblyAI API.')
    parser.add_argument('audio_input', type=str, help='The path to the audio file or URL to transcribe.')
    parser.add_argument('-d', '--diarisation', action='store_true', help='Enable speaker diarisation. This will label each speaker in the transcription.')
    parser.add_argument('-o', '--output', type=str, default=None, help='The path to the output file to store the result. If not provided, the result will be saved to a file with the same name as the input file but with a .txt extension. If "-" is provided, the result will be printed to standard output.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress all output to standard output. If an output file is specified, the result will still be saved to that file.')
    parser.add_argument('-e', '--expected-speakers', type=int, default=-1, help='The expected number of speakers for diarisation. This helps improve the accuracy of speaker labelling.')
    parser.add_argument('-l', '--language', type=str, default='auto', help='The dominant language in the audio file. Example codes: en, en_au, en_uk, en_us, es, fr, de, it, pt, nl, hi, ja, zh, fi, ko, pl, ru. Default is "auto" for automatic language detection.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging. This will print detailed logs during the execution of the script.')
    args = parser.parse_args()

    api_token = os.environ["ASSEMBLYAI_API_KEY"]
    audio_input = args.audio_input
    speaker_labels = args.diarisation

    try:
        if args.verbose:
            print("Processing audio input...")
        upload_url = upload_file(api_token, audio_input)
        if args.verbose:
            print("Creating transcript...")
        transcript = create_transcript(api_token, upload_url, speaker_labels)
        if args.verbose:
            print("Transcript created. Writing output...")
        output = args.output if args.output is not None else os.path.splitext(audio_input)[0] + '.txt'
        if output != '-':
            if os.path.exists(output):
                if not args.quiet:
                    sys.stderr.write(f'SKIPPING: transcription of {audio_input} as {output} already exists\n')
                sys.exit(0)
            with open(output, 'w') as f:
                if speaker_labels:
                    for utterance in transcript['utterances']:
                        f.write(f"Speaker {utterance['speaker']}:" + utterance['text'] + '\n')
                else:
                    f.write(transcript['text'] + '\n')
            if args.verbose and not args.quiet:
                print(f"Output written to {output}")
        if output == '-' or not args.quiet:
            if speaker_labels:
                for utterance in transcript['utterances']:
                    print(f"Speaker {utterance['speaker']}:", utterance['text'])
            else:
                print(transcript['text'])
        if args.verbose:
            print("Done.")
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
