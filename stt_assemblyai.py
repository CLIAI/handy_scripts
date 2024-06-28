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
    headers = {'authorization': api_token}
    with open(audio_input, 'rb') as f:
        response = requests.post(url, headers=headers, files={'file': f})
    try:
        response.raise_for_status()
        return response.json()['upload_url']
    except Exception as e:
        raise Exception(f"Error in upload_file: {e}, REST RESPONSE: {response.json()}") from e

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
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.json()}")
        response.raise_for_status()
    transcript_id = response.json()['id']
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    while True:
        response = requests.get(polling_endpoint, headers=headers)
        try:
            response.raise_for_status()
            transcription_result = response.json()
            if transcription_result['status'] == "completed":
                return transcription_result
            elif transcription_result['status'] == "error":
                raise Exception(f"Transcription failed: {transcription_result['error']}")
        except Exception as e:
            raise Exception(f"Error in create_transcript: {e}, REST RESPONSE: {response.json()}") from e
        else:
            time.sleep(3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio file using AssemblyAI API.')
    parser.add_argument('audio_input', type=str, help='The path to the audio file to transcribe.')
    parser.add_argument('-d', '--diarisation', action='store_true', help='Enable speaker diarisation. This will label each speaker in the transcription.')
    parser.add_argument('-o', '--output', type=str, default='', help='The path to the output file to store the result. If not provided, the result will be printed to standard output.')
    parser.add_argument('-e', '--expected-speakers', type=int, default=-1, help='The expected number of speakers for diarisation. This helps improve the accuracy of speaker labelling.')
    parser.add_argument('-l', '--language', type=str, default='auto', help='The dominant language in the audio file. Example codes: en, en_au, en_uk, en_us, es, fr, de, it, pt, nl, hi, ja, zh, fi, ko, pl, ru. Default is "auto" for automatic language detection.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging. This will print detailed logs during the execution of the script.')
    args = parser.parse_args()

    api_token = os.environ["ASSEMBLYAI_API_KEY"]
    audio_input = args.audio_input
    speaker_labels = args.diarisation

    response = None
    try:
        if args.verbose:
            print("Uploading file...")
        response = upload_file(api_token, audio_input)
        upload_url = response
        if args.verbose:
            print("File uploaded. Creating transcript...")
        response = create_transcript(api_token, upload_url, speaker_labels)
        transcript = response
        if args.verbose:
            print("Transcript created. Writing output...")
        output = args.output
        if output:
            with open(output, 'w') as f:
                if speaker_labels:
                    for utterance in transcript['utterances']:
                        f.write(f"Speaker {utterance['speaker']}:" + utterance['text'] + '\n')
                else:
                    f.write(transcript['text'] + '\n')
        else:
            if speaker_labels:
                for utterance in transcript['utterances']:
                    print(f"Speaker {utterance['speaker']}:", utterance['text'])
            else:
                print(transcript['text'])
        if args.verbose:
            print("Done.")
    except Exception as e:
        if response is not None:
            if isinstance(response, str):
                print(f'> REST RESPONSE: {response}', file=sys.stderr)
            else:
                print(f'> REST RESPONSE: {response.json()}', file=sys.stderr)
        print(f'Error: {e}')
