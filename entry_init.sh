#!/bin/bash
# entrypoint pre-initialization
source /environment

# copy powerline-shell config
cp /powerline-shell.json $HOME/.config/powerline-shell/config.json

# run the user command
exec "$@"
