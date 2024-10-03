#!/bin/bash

function vtt2txt() {
    sed -e 's/<[^>]*>//g'  | sed '/^WEBVTT$/d' | sed -n '/-->/!p' | sed '/^\ *$/d'|uniq
}

function usage() {
    echo "Usage: $0 [file ...]"
    echo "Converts VTT files to TXT. If no files are provided, reads from standard input."
}

if [[ $1 == "-h" || $1 == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -eq 0 ]]; then
    vtt2txt
else
    for file in "$@"; do
        vtt2txt < "$file"
    done
fi
