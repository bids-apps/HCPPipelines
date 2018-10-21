#!/bin/bash
# entrypoint pre-initialization
source /environment

# make symlink to powerline-shell config
ln -sf /powerline-shell.json $HOME/.powerline-shell.json

# welcom message
echo "Welcome to the BIRC's container for the Human Connectome Project (HCP) pipelines! "

# run the user command
exec "$@"
