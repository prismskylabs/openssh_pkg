#!/bin/bash

# This is for private toolchain

[ -f  ~/.edgerc ] &&  . ~/.edgerc

set -xu

[ -z "${PKG_PLATFORM:-}" ] && echo " PKG_PLATFORM not defined. Exiting. " && exit 1

if [[ $PKG_PLATFORM == "Linux"* ]] || [[ $PKG_PLATFORM == "linux"* ]]; then
  export OPENSSL_PERL=/usr/bin/perl
fi

if [ "${PKG_PLATFORM}" = "linux-amd64" ]; then
   ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
   $ROOT_DIR/build-linux-amd64-oss.sh
   exit $?
fi

. edge_build_base/src/scripts/setup_routines.sh
setup_create_package
