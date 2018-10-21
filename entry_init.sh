#!/bin/bash
# entrypoint pre-initialization
source /environment

# copy powerline-shell config
if [ ! -f $HOME/.powerline-shell.json ]; then
  cp /powerline-shell.json $HOME/.powerline-shell.json
fi

# run the user command
exec "$@"
