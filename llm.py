#!/usr/bin/env python3

# Important Note to Keep:
# This script imports several libraries in try blocks by design.
# This allows the script to failover to other implementations if certain dependencies are not present in the system.

import os
import sys
import json
import requests
import argparse

def INFO(message):
    print(message)

def DEBUG(message, verbose):
    if verbose:
        print(message)

# Main system message, prompt, model, and temperature
SYSTEM_MESSAGE = "You are a helpful AI assistant."
PROMPT = "Please provide a information dense (maximise information per words) answer to advanced sophisticated reader the following question: "
MODEL = "gpt-4o"
TEMPERATURE = 0.7

# Get API key from environment variable
API_KEY = os.environ.get("OPENAI_API_KEY")

if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit(1)

def get_ell_response(user_input, model):
    try:
        import ell
        @ell.simple(model=model)
        def ell_response(user_input: str):
            """{SYSTEM_MESSAGE}"""
            return user_input
        return ell_response(user_input)
    except ImportError:
        return None

def get_openai_response(prompt: str, model):
    try:
        import openai
        openai.api_key = API_KEY
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content
    except ImportError:
        return None

def get_rest_response(user_input, model):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_input}
        ],
        "temperature": TEMPERATURE
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_response(message, args):
    if args.implementation == 'ell':
        return get_ell_response(message, model)
    elif args.implementation == 'openai library':
        return get_openai_response(message, model)
    elif args.implementation == 'openai rest':
        return get_rest_response(message, model)
    else:
        DEBUG("No implementation specified. Trying all...", args.verbose)
        DEBUG("Trying ell...", args.verbose)
        response = get_ell_response(message, model)
        if response is not None:
            DEBUG("ell succeeded.", args.verbose)
            return response
        DEBUG("ell failed. Trying OpenAI library...", args.verbose)
        response = get_openai_response(message, model)
        if response is not None:
            DEBUG("OpenAI library succeeded.", args.verbose)
            return response
        DEBUG("OpenAI library failed. Trying OpenAI REST...", args.verbose)
        response = get_rest_response(message, model)
        if response is not None:
            DEBUG("OpenAI REST succeeded.", args.verbose)
        else:
            DEBUG("OpenAI REST failed.", args.verbose)
    return response

def parse_args():
    parser = argparse.ArgumentParser(description='Process user input with failover between ELL, OpenAI, and REST.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display verbose output.')
    parser.add_argument('-s', '--sysmsg', type=str, help='Set system message.')
    parser.add_argument('-p', '--prompt', type=str, help='Set prompt.')
    parser.add_argument('-i', '--implementation', type=str, choices=['ell', 'openai library', 'openai rest'], help='Enforce using one of the available implementations.')
    parser.add_argument('-t', '--temperature', type=float, help='Set temperature.')
    parser.add_argument('-m', '--model', type=str, help='Set model.')
    return parser.parse_args()

def main():
    args = parse_args()
    model = args.model if args.model else MODEL
    DEBUG(f"MODEL: {model}", args.verbose)
    DEBUG(f"SYSTEM_MESSAGE: {SYSTEM_MESSAGE}", args.verbose)
    DEBUG(f"PROMPT: {PROMPT}", args.verbose)
    temperature = args.temperature if args.temperature else TEMPERATURE
    DEBUG(f"TEMPERATURE: {temperature}", args.verbose)
    user_input = args.prompt if args.prompt else sys.stdin.read().strip()
    full_message = f"{args.sysmsg if args.sysmsg else SYSTEM_MESSAGE}{user_input}"
    response = get_response(full_message, args)
    if response:
        DEBUG("RESPONSE:", args.verbose)
        print(response)
    else:
        print("Failed to get a response from the AI.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
