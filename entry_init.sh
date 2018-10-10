#!/bin/bash
# entrypoint pre-initialization
source /environment

# bash prompt
## \u user name
## \h host name
## BIDS_HCP_BIRC project name, colored in cyan
## \w working directory
export PS1="\u@\h \[\e[1;36m\]BIDS_HCP_BIRC\[\e[m\] \w\$ "

# run the user command
exec "$@"
