#!/usr/bin/env python
import os
import requests
import time

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
        "speaker_labels": speaker_labels
    }
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
    api_token = os.environ["ASSEMBLYAI_API_KEY"]
    import sys
    if len(sys.argv) < 2:
        print("Error: No audio file provided.")
        sys.exit(1)
    audio_input = sys.argv[1]
    speaker_labels = False  # Set to False by default
    if len(sys.argv) > 2 and sys.argv[2] == '--diarisation':
        speaker_labels = True  # Set to True if --diarisation flag is provided

    try:
        upload_url = upload_file(api_token, audio_input)
        transcript = create_transcript(api_token, upload_url, speaker_labels)
        if speaker_labels:
            for utterance in transcript['utterances']:
                print(f"Speaker {utterance['speaker']}:", utterance['text'])
        else:
            print(transcript['text'])
    except Exception as e:
        print(f'Error: {e}')
