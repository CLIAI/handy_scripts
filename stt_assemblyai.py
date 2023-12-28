#!/usr/bin/env python
import os
import requests
import time
import argparse

def upload_file(api_token, audio_input):
    if audio_input.startswith('http://') or audio_input.startswith('https://'):
        return audio_input
    url = 'https://api.assemblyai.com/v2/upload'
    headers = {'authorization': api_token}
    with open(audio_input, 'rb') as f:
        response = requests.post(url, headers=headers, files={'file': f})
    response.raise_for_status()
    return response.json()['upload_url']

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
    response.raise_for_status()
    transcript_id = response.json()['id']
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    while True:
        response = requests.get(polling_endpoint, headers=headers)
        response.raise_for_status()
        transcription_result = response.json()
        if transcription_result['status'] == "completed":
            return transcription_result
        elif transcription_result['status'] == "error":
            raise Exception(f"Transcription failed: {transcription_result['error']}")
        else:
            time.sleep(3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio file using AssemblyAI API.')
    parser.add_argument('audio_input', type=str, help='The audio file to transcribe.')
    parser.add_argument('-d', '--diarisation', action='store_true', help='Enable speaker diarisation.')
    parser.add_argument('-o', '--output', type=str, default='', help='Output file to store the result. If not provided, result will be printed to standard output.')
    parser.add_argument('--expected-speakers', type=int, default=-1, help='Expected number of speakers for diarisation.')
    parser.add_argument('-l', '--language', type=str, default='auto', help='Dominant language in the audio file. Example codes: en, en_au, en_uk, en_us, es, fr, de, it, pt, nl, hi, ja, zh, fi, ko, pl, ru. Default is "auto" for automatic language detection.')
    args = parser.parse_args()

    api_token = os.environ["ASSEMBLYAI_API_KEY"]
    audio_input = args.audio_input
    speaker_labels = args.diarisation

    try:
        upload_url = upload_file(api_token, audio_input)
        transcript = create_transcript(api_token, upload_url, speaker_labels)
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
    except Exception as e:
        print(f'Error: {e}')
