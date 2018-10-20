#!/bin/bash
# entrypoint pre-initialization
source /environment

# copy powerline-shell config
cp /home/.powerline-shell.json $HOME

# run the user command
exec "$@"
