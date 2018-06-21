#!/bin/sh
# script for execution of deployed applications
#
# Sets up the MCR environment for the current $ARCH and executes 
# the specified command.
#
exe_name=$0
exe_dir=`dirname "$0"`
echo "------------------------------------------"
if [ "x$1" = "x" ]; then
  echo Usage:
  echo    $0 \<deployedMCRroot\> args
else
  echo Setting up environment variables
  MCRROOT="$1"
  echo ---
  MCRJRE=${MCRROOT}/sys/java/jre/glnxa64/jre/lib/amd64 ;
  LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/lib64:/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}:.:${MCRROOT}/runtime/glnxa64:${MCRROOT}/bin/glnxa64:${MCRROOT}/sys/os/glnxa64:${LD_LIBRARY_PATH}:${MCRJRE}/native_threads:${MCRJRE}/native_threads:${MCRJRE}/client:${MCRJRE}  
  XAPPLRESDIR=${MCRROOT}/X11/app-defaults ;
  export LD_LIBRARY_PATH;
  export XAPPLRESDIR;
  echo LD_LIBRARY_PATH is ${LD_LIBRARY_PATH};
  shift 1
  args=
  while [ $# -gt 0 ]; do
      token=$1
      args="${args} \"${token}\"" 
      shift
  done
  eval "\"${exe_dir}/RestingStateStats\"" $args
fi
exit

