#!/bin/bash
# entrypoint pre-initialization
source /environment

# make symlink to powerline-shell config
ln -sf /powerline-shell.json $HOME/.powerline-shell.json

# run the user command
exec "$@"
