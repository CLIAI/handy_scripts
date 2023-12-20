#!/bin/bash

prev=""
while [ 1 ]; do
curr="$(xclip -selection clipboard -o)"
if [[ "$curr" != "$prev" ]]; then
    #if [[ !  "$curr" =~ ^http ]]; then
	echo "$curr"
    #fi
fi
prev="$curr"
sleep 0.2
done
