#!/bin/bash
# entrypoint pre-initialization
source /environment

# run the user command
exec "$@"
