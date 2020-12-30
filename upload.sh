#!/bin/bash

set -xu

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PKG_DIR=$ROOT_DIR/pkg

PKG_NAME=$(conan inspect $ROOT_DIR | grep -F 'name:' | sed -e 's!name: !!g' )
PKG_VER=$(conan inspect $ROOT_DIR | grep -F 'version:' | sed -e 's!version: !!g' )
#PKG_USER=psl
#PKG_CHANNEL=dev

PKG_NAME_FULL="$PKG_NAME/$PKG_VER" # @$PKG_USER/$PKG_CHANNEL"
echo "Uploading package $PKG_NAME_FULL"

conan remote list

for i in $(seq 1 3); do
   conan upload $PKG_NAME_FULL --all -r=psl-conan -c --retry 5  --retry-wait 15 && break
   sleep 15 && false
done

