

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. $SCRIPT_DIR/../../src/external/edge_build_bootstrap/src/scripts/bootstrap_routines.sh

set -xu

bootstrap_setup

bootstrap_configure_toolchain

