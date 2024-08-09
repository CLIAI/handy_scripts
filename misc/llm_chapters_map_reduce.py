#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

def verbose_print(message, verbose):
    if verbose:
        print(message, file=sys.stderr)

def backup_file(filename):
    n = 1
    while os.path.exists(f"{filename}.bak.{n}"):
        n += 1
    os.rename(filename, f"{filename}.bak.{n}")
    return f"{filename}.bak.{n}"

def safe_write(filename, content, verbose):
    if os.path.exists(filename):
        backup = backup_file(filename)
        verbose_print(f"Backed up existing file to {backup}", verbose)
    with open(filename, 'w') as f:
        f.write(content)
    verbose_print(f"Wrote content to {filename}", verbose)

def llm_as_str(input_filename, prompt_string, verbose):
    verbose_print(f"Executing LLM for: {prompt_string}", verbose)
    cmd = f"cat {input_filename} | mods -m gpt-4o"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def llm(input_filename, prompt_string, output_filename, verbose):
    content = llm_as_str(input_filename, prompt_string, verbose)
    safe_write(output_filename, content, verbose)

def main():
    parser = argparse.ArgumentParser(description="Generate book chapters using LLM")
    parser.add_argument("-o", "--output", metavar="prefix", default=None, help="Prefix for generated output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose information")
    parser.add_argument("input_file", help="Input filename")
    args = parser.parse_args()

    input_basename = os.path.splitext(os.path.basename(args.input_file))[0]
    prefix = args.output if args.output else f"{input_basename}-out"

    toc_fn = f"{prefix}-000-ToC.md"

    # TODO: Implement support for chunking the input file and processing chunks

    # Generate ToC
    llm(args.input_file, 'generate table of contents for mini book that will contain all data, insights, information, aspects, thoughts from input, as numbered list', toc_fn, args.verbose)

    # Use LLM to count chapters
    number_of_chapters = int(llm_as_str(toc_fn, 'return ONLY number with number of chapters', args.verbose))
    verbose_print(f"Number of chapters: {number_of_chapters}", args.verbose)

    for chapter_no in range(1, number_of_chapters + 1):
        about_chapter = llm_as_str(toc_fn, f"return information about chapter no {chapter_no}", args.verbose)
        chapter_fn = f"{prefix}-ch{chapter_no:03d}.md"
        llm(args.input_file, f"Generate chapter no {chapter_no} as Markdown that will be used in pandoc. Here what will be topic of chapter: {about_chapter}.", chapter_fn, args.verbose)

if __name__ == "__main__":
    main()
