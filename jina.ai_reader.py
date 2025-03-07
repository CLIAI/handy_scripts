#!/usr/bin/env python3
# Get your Jina AI API key for free: https://jina.ai/?sui=apikey
# NOTE TO DEVELOPERS:
# All verbose or debug messages must go to standard error (stderr).
# Only the fetched output (i.e., the JSON response or extracted content from the Jina Reader API) 
# should be printed to standard output (stdout).
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
    parser.add_argument("-q", "--quiet", action="store_true", help="Set verbosity level to 0, suppressing all output except errors.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity level. Can be used multiple times.")
    parser.add_argument("-u", "--url", required=True, help="The URL of the webpage to fetch.")
    parser.add_argument("--no-cache", action="store_true", help="If set, passes X-No-Cache: true.")
    parser.add_argument("-x", "--remove-selector", help="Comma-separated CSS selectors to exclude from the page.")
    parser.add_argument("-s", "--target-selector", help="Comma-separated CSS selectors to focus on.")
    parser.add_argument("-t", "--timeout", type=int, help="Specifies the maximum time (in seconds) to wait for the webpage to load.")
    parser.add_argument("--wait-for-selector", help="Comma-separated CSS selectors to wait for before returning.")
    parser.add_argument("-l", "--with-links-summary", action="store_true", help="If set, gather all links at the end of the response.")
    parser.add_argument("-i", "--with-images-summary", action="store_true", help="If set, gather all images at the end of the response.")
    parser.add_argument("-a", "--with-generated-alt", action="store_true", help="If set, generate alt text for images without captions.")
    parser.add_argument("-I", "--with-iframe", action="store_true", help="If set, include iframe content in the response.")
    parser.add_argument("-F", "--return-format", choices=["m", "h", "t", "s", "p", "markdown", "html", "text", "screenshot", "pageshot"],
                        help="Sets the X-Return-Format header. Possible options: m (markdown), h (html), t (text), s (screenshot), p (pageshot).")
    parser.add_argument("--token-budget", type=int, help="Specifies the maximum number of tokens to use for the request.")
    parser.add_argument("-N", "--retain-images", choices=["none"], help="Use 'none' to remove images from the response.")
    parser.add_argument("-f", "--field", choices=["content", "links", "images", "title", "description"],
                        help="Specify a field to print its raw value instead of the whole JSON.")
    parser.add_argument("-c", "--content", action="store_true", help="Equivalent to --field content.")
    parser.add_argument("-d", "--description", action="store_true", help="Equivalent to --field description.")
    
    args = parser.parse_args()

    # Determine verbosity level
    verbosity = 1  # Default verbosity level
    if args.quiet:
        verbosity = 0
    else:
        verbosity += args.verbose
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
        if verbosity > 0:
            print("Using authorization header with JINA_API_KEY.", file=sys.stderr)
    else:
        if verbosity > 0:
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
        format_map = {
            "m": "markdown",
            "h": "html",
            "t": "text",
            "s": "screenshot",
            "p": "pageshot"
        }
        normalized_rf = format_map.get(args.return_format, args.return_format)
        headers["X-Return-Format"] = normalized_rf
    else:
        normalized_rf = None
    if args.token_budget is not None:
        headers["X-Token-Budget"] = str(args.token_budget)
    if args.retain_images:
        headers["X-Retain-Images"] = args.retain_images

    # Prepare the request body
    payload = {
        "url": args.url
    }

    # Handle field shortcuts
    if args.content:
        args.field = "content"
    elif args.description:
        args.field = "description"

    # Perform the request
    try:
        if verbosity > 0:
            print(f"Sending request to {endpoint} with provided parameters...", file=sys.stderr)
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        # Parse JSON
        data = response.json()
    except requests.exceptions.RequestException as e:
        if verbosity > 0:
            print(f"Error while making request to Jina AI Reader API: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        if verbosity > 0:
            print(f"Error parsing JSON response from Jina AI Reader API: {e}", file=sys.stderr)
        sys.exit(1)

    # Print the specified field or the whole JSON
    if args.field:
        # Check for special case: --return-format text and --field content
        if normalized_rf == "text" and args.field == "content":
            text_value = data.get("data", {}).get("text")
            if text_value is not None:
                print(text_value)
            else:
                print("Field 'text' not found in the response.", file=sys.stderr)
                sys.exit(1)
        else:
            field_value = data.get("data", {}).get(args.field)
            if field_value is not None:
                print(field_value)
            else:
                print(f"Field '{args.field}' not found in the response.", file=sys.stderr)
                sys.exit(1)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

