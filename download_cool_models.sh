#!/bin/bash

if [ -z "$dstdir" ]; then
    dstdir="$PWD"
    echo 'Assuming destination directory to be current working directory:'
    pwd
fi


function dwn_hf() {
    echo '--------------------------------------------'
    echo "Processing $1..."
    local url="$1"
    local regex="https://huggingface.co/([^/]+)/([^/]+)"

    if [[ $url =~ $regex ]]; then
        local username="${BASH_REMATCH[1]}"
        local project="${BASH_REMATCH[2]}"
        echo "Username: $username"
        echo "Project: $project"
        if [ -d "$dstdir/$username/$project" ]; then
            echo 'Directory exist. Assuming model was already downloaded'
            set -x
            cd "$dstdir/$username/$project"
            git pull
            git fetch --all
            set +x
        else
            set -x
            mkdir -p "$dstdir/$username"
            cd "$dstdir/$username"
            git lfs install
            git clone https://huggingface.co/"$username"/"$project"
            cd "$project"
            git fetch --all
            set +x
        fi
    else
        echo "Invalid URL"
    fi
}

dwn_hf https://huggingface.co/camenduru/potat1
dwn_hf https://huggingface.co/tiiuae/falcon-40b
dwn_hf https://huggingface.co/NousResearch/Nous-Hermes-13b
dwn_hf https://huggingface.co/ausboss/llama-13b-supercot
dwn_hf https://huggingface.co/ausboss/llama-30b-supercot
dwn_hf https://huggingface.co/ausboss/llama-30b-supercot-4bit
dwn_hf https://huggingface.co/ausboss/llama-30b-SuperHOT
dwn_hf https://huggingface.co/ausboss/llama-30b-SuperHOT-4bit
dwn_hf https://huggingface.co/ausboss/llama-30b-superhotcot-4bit
dwn_hf https://huggingface.co/ausboss/llama-30b-superhotcot.ggmlv3.q4_0
dwn_hf https://huggingface.co/ausboss/llama7b-pyg-lora
dwn_hf https://huggingface.co/ausboss/llama7b-wizardlm-unfiltered
dwn_hf https://huggingface.co/ausboss/llama7b-wizardlm-unfiltered-4bit-128g
dwn_hf https://huggingface.co/ausboss/llama7b-wizardlm-unfiltered-lora
dwn_hf https://huggingface.co/ausboss/llygma-13b-lora
dwn_hf https://huggingface.co/ausboss/llygmalion-13B
dwn_hf https://huggingface.co/ausboss/LunarLander
dwn_hf https://huggingface.co/ausboss/ppo-Huggy
dwn_hf https://huggingface.co/ausboss/wizardlm-13b-unbiased-lora
dwn_hf https://huggingface.co/ausboss/WizardLM-13B-Uncensored-4bit-128g
dwn_hf https://huggingface.co/ehartford/alpaca1337-13b-4bit
dwn_hf https://huggingface.co/ehartford/alpaca1337-7b-4bit
dwn_hf https://huggingface.co/ehartford/samantha-13b
dwn_hf https://huggingface.co/ehartford/samantha-33b
dwn_hf https://huggingface.co/ehartford/samantha-7b
dwn_hf https://huggingface.co/ehartford/samantha-falcon-7b
dwn_hf https://huggingface.co/ehartford/WizardLM-13B-Uncensored
dwn_hf https://huggingface.co/ehartford/WizardLM-30B-Uncensored
dwn_hf https://huggingface.co/ehartford/WizardLM-Uncensored-Falcon-40b
dwn_hf https://huggingface.co/ehartford/WizardLM-Uncensored-Falcon-7b
dwn_hf https://huggingface.co/ehartford/Wizard-Vicuna-13B-Uncensored
dwn_hf https://huggingface.co/ehartford/Wizard-Vicuna-30B-Uncensored
dwn_hf https://huggingface.co/ehartford/Wizard-Vicuna-7B-Uncensored
dwn_hf https://huggingface.co/mosaicml/mpt-7b-chat
dwn_hf https://huggingface.co/mosaicml/mpt-7b-instruct
dwn_hf https://huggingface.co/mosaicml/mpt-7b-storywriter
dwn_hf https://huggingface.co/PygmalionAI/metharme-13b
dwn_hf https://huggingface.co/PygmalionAI/pygmalion-13b
dwn_hf https://huggingface.co/PygmalionAI/pygmalion-7b
dwn_hf https://huggingface.co/TehVenom/WizardLM-13B-Uncensored-Q5_1-GGML
dwn_hf https://huggingface.co/google/flan-t5-xl
