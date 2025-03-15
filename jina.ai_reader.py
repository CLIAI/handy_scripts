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
import re

def url_to_filename(url, verbosity=0):
    """
    Convert a URL to a safe filename.
    
    Args:
        url (str): The URL to convert
        verbosity (int): Verbosity level
        
    Returns:
        str: A filename-safe string derived from the URL
    """
    # First, try to match against special patterns
    # (This is a placeholder for future special case handlers)
    
    # If no special case matched, use the generic handler
    return generic_url_to_filename(url, verbosity)

def generic_url_to_filename(url, verbosity=0):
    """
    Generic function to convert any URL to a safe filename.
    
    Args:
        url (str): The URL to convert
        verbosity (int): Verbosity level
        
    Returns:
        str: A filename-safe string derived from the URL
    """
    if verbosity > 1:
        print(f"Converting URL to filename: {url}", file=sys.stderr)
        
    # Remove protocol (http://, https://)
    clean_url = re.sub(r'^https?://', '', url)
    
    # Remove trailing slashes
    clean_url = clean_url.rstrip('/')
    
    # Replace all characters that aren't alphanumeric, underscore, or hyphen
    # This ensures the result fits [a-zA-Z0-9_-]
    clean_url = re.sub(r'[^a-zA-Z0-9_-]', '_', clean_url)
    
    # Collapse multiple underscores into one
    clean_url = re.sub(r'_+', '_', clean_url)
    
    # Limit length to avoid excessively long filenames
    if len(clean_url) > 100:
        clean_url = clean_url[:100]
    
    if verbosity > 1:
        print(f"Generated filename: {clean_url}", file=sys.stderr)
        
    return clean_url

def main():
    parser = argparse.ArgumentParser(
        description="A script that fetches pages from the Jina AI Reader API (https://r.jina.ai/)."
                    "Optional flags allow passing certain 'X-' headers. If the environment variable "
                    "'JINA_API_KEY' is set, the script will use it. Otherwise, it will issue the request without authorization."
    )
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Set verbosity level to 0, suppressing all output except errors.")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity level. Can be used multiple times.")
    parser.add_argument("-u", "--url", required=True,
                        help="The URL of the webpage to fetch.")
    parser.add_argument("--no-cache", action="store_true",
                        help="If set, passes X-No-Cache: true.")
    parser.add_argument("-x", "--remove-selector",
                        help="Comma-separated CSS selectors to exclude from the page.")
    parser.add_argument("-s", "--target-selector",
                        help="Comma-separated CSS selectors to focus on.")
    parser.add_argument("-t", "--timeout", type=int,
                        help="Specifies the maximum time (in seconds) to wait for the webpage to load.")
    parser.add_argument("--wait-for-selector",
                        help="Comma-separated CSS selectors to wait for before returning.")
    parser.add_argument("-l", "--with-links-summary", action="store_true",
                        help="If set, gather all links at the end of the response.")
    parser.add_argument("-i", "--with-images-summary", action="store_true",
                        help="If set, gather all images at the end of the response.")
    parser.add_argument("-a", "--with-generated-alt", action="store_true",
                        help="If set, generate alt text for images without captions.")
    parser.add_argument("-I", "--with-iframe", action="store_true",
                        help="If set, include iframe content in the response.")
    parser.add_argument("-F", "--return-format",
                        choices=["m", "h", "t", "s", "p", "markdown", "html", "text", "screenshot", "pageshot"],
                        help="Sets the X-Return-Format header: "
                             "m (markdown), h (html), t (text), s (screenshot), p (pageshot).")
    parser.add_argument("--token-budget", type=int,
                        help="Specifies the maximum number of tokens to use for the request.")
    parser.add_argument("-N", "--retain-images", choices=["none"],
                        help="Use 'none' to remove images from the response.")
    parser.add_argument("-f", "--field",
                        choices=["content", "links", "images", "title", "description"],
                        help="Specify a field to print its raw value instead of the whole JSON.")
    parser.add_argument("-c", "--content", action="store_true",
                        help="Equivalent to --field content.")
    parser.add_argument("-d", "--description", action="store_true",
                        help="Equivalent to --field description.")

    # New flags:
    parser.add_argument("-o", "--output",
                        help="Path or filename for the single output file, or prefix for multiple outputs if used with --save-all. "
                             "Use 'auto' to automatically generate filename based on URL.")
    parser.add_argument("--save-all", "-A",
                        help="Comma-separated list of items or 'all' to produce multiple files from a single request. "
                             "Possible items include 'json', 'content', 'title', 'description', 'links', 'images', "
                             "'text', 'markdown', 'html'. "
                             "Use 'all' to export all recognized fields plus 'json' (if available).")

    args = parser.parse_args()

    # Determine verbosity level
    verbosity = 1  # Default verbosity
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

    normalized_rf = None
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

    if args.token_budget is not None:
        headers["X-Token-Budget"] = str(args.token_budget)
    if args.retain_images:
        headers["X-Retain-Images"] = args.retain_images

    # Shortcut flags
    if args.content:
        args.field = "content"
    elif args.description:
        args.field = "description"

    payload = {
        "url": args.url
    }

    # Perform the request (only once)
    try:
        if verbosity > 0:
            print(f"Sending request to {endpoint} with provided parameters...", file=sys.stderr)
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        if verbosity > 0:
            print(f"Error while making request to Jina AI Reader API: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        if verbosity > 0:
            print(f"Error parsing JSON response from Jina AI Reader API: {e}", file=sys.stderr)
        sys.exit(1)

    # =========================================================
    # Logic for new flags --output / --save-all
    # =========================================================

    def get_data_string(item, full_data):
        """
        Return the string content for a requested 'item'.
        'item' can be:
          - 'json': the entire JSON string
          - 'text' / 'markdown' / 'html' / 'screenshot' / 'pageshot'
          - recognized field among 'content', 'title', 'description', 'links', 'images'
        """
        # Return entire JSON
        if item == "json":
            return json.dumps(full_data, indent=2, ensure_ascii=False)

        # For these, read from data["data"].(item) if present
        if item in ["text", "markdown", "html", "screenshot", "pageshot"]:
            return full_data.get("data", {}).get(item, "")

        # For known fields: content, title, description, links, images
        return full_data.get("data", {}).get(item, "")

    def detect_extension(r_format, item):
        """
        Choose file extension based on return format or item.
        """
        # 'json' => .json
        if item == "json":
            return ".json"

        # If there's a recognized format, pick extension
        if r_format == "markdown":
            return ".md"
        elif r_format == "html":
            return ".html"
        elif r_format == "text":
            return ".txt"
        elif r_format == "screenshot":
            return ".png"
        elif r_format == "pageshot":
            return ".png"

        # Fallback
        return ".txt"

    def set_extended_attribute(filename, url_val):
        """
        Attempt to store the original url in extended attribute: user.xdg.origin.url
        If it fails, ignore unless verbosity > 0, then show a warning.
        """
        try:
            os.setxattr(filename, "user.xdg.origin.url", url_val.encode('utf-8'))
        except OSError as e:
            if verbosity > 0:
                print(f"Warning: could not set xattr user.xdg.origin.url on {filename}: {e}", file=sys.stderr)

    # If --save-all is used, we produce multiple output files
    if args.save_all:
        if not args.output:
            # Must have an -o prefix if we're saving multiple outputs
            print("Error: --save-all requires --output as a filename prefix.", file=sys.stderr)
            sys.exit(1)
        
        # Handle 'auto' special value for --output
        if args.output.lower() == 'auto':
            args.output = url_to_filename(args.url, verbosity)
            if verbosity > 0:
                print(f"Auto-generated filename prefix: {args.output}", file=sys.stderr)

        # Build the list of items we want to generate
        items_to_export = []

        # If user specified a return format, produce the "main" version
        # (like entire text or entire markdown) unless that is already
        # going to appear in the user list. If no format is specified,
        # produce "json" as the main form.
        if normalized_rf:
            main_item = normalized_rf
        else:
            main_item = "json"

        # parse comma separated items
        raw_list = [x.strip() for x in args.save_all.split(",") if x.strip()]

        # Expand "all" if present
        # We'll define "all" as: json, content, title, description, links, images, text, markdown, html
        # We won't forcibly produce screenshot/pageshot unless user specifically asks, to limit confusion
        def all_list():
            return ["json", "content", "title", "description", "links", "images", "text", "markdown", "html"]

        expanded_items = []
        for token in raw_list:
            if token == "all":
                expanded_items.extend(all_list())
            else:
                expanded_items.append(token)

        # Ensure we add the main_item at the front if not present
        all_seen = set()
        if main_item not in expanded_items:
            items_to_export.append(main_item)
            all_seen.add(main_item)

        # Add expansions
        for it in expanded_items:
            if it not in all_seen:
                items_to_export.append(it)
                all_seen.add(it)

        # Now produce each item in items_to_export
        for item in items_to_export:
            out_str = get_data_string(item, data)
            if out_str is None:
                out_str = ""

            # Deduce extension
            ext = detect_extension(normalized_rf, item)

            # For the 'main_item', we don't want a .markdown.md scenario, so skip appending the item if it matches
            # Example: if user typed -F markdown, main_item=markdown => file.md
            if item == main_item:
                out_filename = f"{args.output}{ext}"
            else:
                out_filename = f"{args.output}.{item}{ext}"

            try:
                with open(out_filename, "w", encoding="utf-8") as f_out:
                    f_out.write(str(out_str))
            except OSError as e:
                if verbosity > 0:
                    print(f"Error writing to {out_filename}: {e}", file=sys.stderr)
                sys.exit(1)

            # Attempt to store extended attribute for the original URL
            set_extended_attribute(out_filename, args.url)

        # Done with multi-output mode
        sys.exit(0)
    else:
        # Legacy single-output path:
        # We either print to stdout or write exactly one file if --output is used.

        # Decide what the single run's output should be
        def produce_single_output():
            """Return a string representing what we would normally print to stdout."""
            # If user explicitly asked for a field
            if args.field:
                # Check for special case: --return-format text and --field content
                # The code below does something similar in original logic.
                if normalized_rf == "text" and args.field == "content":
                    text_value = data.get("data", {}).get("text")
                    if text_value is not None:
                        return text_value
                    else:
                        # "Field 'text' not found"
                        return ""
                else:
                    field_value = data.get("data", {}).get(args.field)
                    if field_value is not None:
                        return str(field_value)
                    else:
                        return ""

            # If no field is specified but we have a return format
            if normalized_rf == "text":
                return data.get("data", {}).get("text", "")
            elif normalized_rf == "markdown":
                return data.get("data", {}).get("markdown", "")
            elif normalized_rf == "html":
                return data.get("data", {}).get("html", "")
            elif normalized_rf == "screenshot":
                return data.get("data", {}).get("screenshot", "")
            elif normalized_rf == "pageshot":
                return data.get("data", {}).get("pageshot", "")

            # Otherwise, just return the entire JSON
            return json.dumps(data, indent=2, ensure_ascii=False)

        single_output_str = produce_single_output()
        if args.output:
            output_filename = args.output
            # Handle 'auto' special value for --output
            if args.output.lower() == 'auto':
                output_filename = url_to_filename(args.url, verbosity)
                if verbosity > 0:
                    print(f"Auto-generated filename: {output_filename}", file=sys.stderr)
            
            try:
                with open(output_filename, "w", encoding="utf-8") as f_out:
                    f_out.write(single_output_str)
            except OSError as e:
                if verbosity > 0:
                    print(f"Error writing to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)

            # Attempt to store extended attribute for the original URL
            set_extended_attribute(output_filename, args.url)
        else:
            # Print to stdout as before
            print(single_output_str)


if __name__ == "__main__":
    main()
