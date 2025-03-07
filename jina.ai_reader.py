#!/usr/bin/env python3
# Get your Jina AI API key for free: https://jina.ai/?sui=apikey
# NOTE TO DEVELOPERS:
# All verbose or debug messages must go to standard error (stderr).
# Only the fetched output (i.e., the JSON response or extracted content from the Jina Reader API) 
# should be printed to standard output (stdout).

import sys
import os
import argparse
import requests
import json

def main():
    parser = argparse.ArgumentParser(
        description="A script for ArchLinux that fetches pages from the Jina AI Reader API (https://r.jina.ai/). "
                    "Optional flags allow passing certain 'X-' headers. If the environment variable "
                    "'JINA_API_KEY' is set, the script will use it. Otherwise, it will issue the request without authorization."
    )
    parser.add_argument("--url", required=True, help="The URL of the webpage to fetch.")
    parser.add_argument("--no-cache", action="store_true", help="If set, passes X-No-Cache: true.")
    parser.add_argument("--remove-selector", help="Comma-separated CSS selectors to exclude from the page.")
    parser.add_argument("--target-selector", help="Comma-separated CSS selectors to focus on.")
    parser.add_argument("--timeout", type=int, help="Specifies the maximum time (in seconds) to wait for the webpage to load.")
    parser.add_argument("--wait-for-selector", help="Comma-separated CSS selectors to wait for before returning.")
    parser.add_argument("--with-links-summary", action="store_true", help="If set, gather all links at the end of the response.")
    parser.add_argument("--with-images-summary", action="store_true", help="If set, gather all images at the end of the response.")
    parser.add_argument("--with-generated-alt", action="store_true", help="If set, generate alt text for images without captions.")
    parser.add_argument("--with-iframe", action="store_true", help="If set, include iframe content in the response.")
    parser.add_argument("--return-format", choices=["markdown", "html", "text", "screenshot", "pageshot"],
                        help="Sets the X-Return-Format header. Possible options: markdown, html, text, screenshot, pageshot.")
    parser.add_argument("--token-budget", type=int, help="Specifies the maximum number of tokens to use for the request.")
    parser.add_argument("--retain-images", choices=["none"], help="Use 'none' to remove images from the response.")
    
    args = parser.parse_args()

    # Base endpoint
    endpoint = "https://r.jina.ai/"
    
    # Always set Accept to application/json
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # If JINA_API_KEY is present in the environment, set Authorization
    jina_api_key = os.environ.get("JINA_API_KEY")
    if jina_api_key:
        headers["Authorization"] = f"Bearer {jina_api_key}"
        print("Using authorization header with JINA_API_KEY.", file=sys.stderr)
    else:
        print("JINA_API_KEY not found; proceeding without authorization.", file=sys.stderr)
    
    # Apply optional headers based on flags
    if args.no_cache:
        headers["X-No-Cache"] = "true"
    if args.remove_selector:
        headers["X-Remove-Selector"] = args.remove_selector
    if args.target_selector:
        headers["X-Target-Selector"] = args.target_selector
    if args.timeout is not None:
        headers["X-Timeout"] = str(args.timeout)
    if args.wait_for_selector:
        headers["X-Wait-For-Selector"] = args.wait_for_selector
    if args.with_links_summary:
        headers["X-With-Links-Summary"] = "true"
    if args.with_images_summary:
        headers["X-With-Images-Summary"] = "true"
    if args.with_generated_alt:
        headers["X-With-Generated-Alt"] = "true"
    if args.with_iframe:
        headers["X-With-Iframe"] = "true"
    if args.return_format:
        headers["X-Return-Format"] = args.return_format
    if args.token_budget is not None:
        headers["X-Token-Budget"] = str(args.token_budget)
    if args.retain_images:
        headers["X-Retain-Images"] = args.retain_images

    # Prepare the request body
    payload = {
        "url": args.url
    }

    # Perform the request
    try:
        print(f"Sending request to {endpoint} with provided parameters...", file=sys.stderr)
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        # Parse JSON
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error while making request to Jina AI Reader API: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing JSON response from Jina AI Reader API: {e}", file=sys.stderr)
        sys.exit(1)

    # Print only the JSON response to stdout
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

