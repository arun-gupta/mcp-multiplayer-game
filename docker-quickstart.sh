#!/bin/bash

docker run \
	   -v $(pwd):/gupta -v $(which ollama):/usr/local/bin/ollama -v /usr/share/ollama/:/usr/share/ollama -v $HOME/.ollama:/root/.ollama \
	   -e OPENAI_API_KEY=$OPENAI_API_KEY -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
	   -p 8501:8501 -p 8000:8000 \
	   -d gupta-runner /gupta/quickstart.sh $@
