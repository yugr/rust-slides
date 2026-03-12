#!/bin/sh

# Script to build, install and test all compiler versions.

set -eu

error() {
  printf "$(basename $0): error: $@\\n" >&2
  exit 1
}

warn() {
  printf "$(basename $0): warning: $@\\n" >&2
}

usage() {
  cat <<EOF
Usage: $(basename $0) [OPT]... path/to/bare/repo path/to/ci-llvm
Build and install all toolchains and run tests.

Options:
  -f                Remove existing branches and builds.
  -j N              Number of parallel jobs.
  --help, -h        Print help and exit.
  --verbose, -v     Print diagnostic info (can be specified more than once).
  -x                Enable shell tracing.

Examples:
  \$ $(basename $0) -f ROOT
EOF
  exit
}

usage_short() {
  cat >&2 <<EOF
Usage: $(basename $0) [OPT]... path/to/bare/repo path/to/ci-llvm
Run \`$(basename $0) -h' for more details.
EOF
  exit 1
}

me=$(basename $0)

RUNALL=$(realpath $(dirname $0))/runall.sh

ARGS=$(getopt -o 'fhj:vx' --long 'verbose,help' -n "$(basename $0)" -- "$@")
eval set -- "$ARGS"

V=0
FORCE=
J=$(nproc)

while true; do
  case "$1" in
    -f)
      FORCE=1
      shift
      ;;
    -j)
      J=$2
      shift 2
      ;;
    -h | --help)
      usage
      ;;
    -v | --verbose)
      V=$((V + 1))
      shift
      ;;
    -x)
      set -x
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      error "unknown option: $1"
      ;;
    *)
      error 'internal error'
      ;;
  esac
done

BARE=$(realpath "$1")
CI_LLVM=$(realpath "$2")

WD=$PWD
CFG=$(dirname $0)/$(basename -s .sh $0).cfg

GIT="git --git-dir=$BARE"

if ! test -d "$BARE"; then
  error "$BARE is not a bare repo"
fi

sanitize() {
  echo "$1" | sed -e 's/#.*//; s/^ *//; s/ *$//'
}

# First uninstall tools

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')

  rustup toolchain uninstall $name || true
done < "$CFG"

# Then check that branches can be created

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  branch=$(echo "$cfg" | awk -F: '{print $2}')

  if $GIT worktree list | fgrep -q "[$branch]"; then
    if test -z "$FORCE"; then
      error "branch $branch already exists in $BARE"
    else
      wt=$($GIT worktree list | fgrep -q "[$branch]" | awk '{print $1}')
      $GIT worktree remove -f $wt
      $GIT branch -D $branch
    fi
  fi
done < "$CFG"

# Create worktrees

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')
  branch=$(echo "$cfg" | awk -F: '{print $2}')

  $GIT worktree add $WD/$name $branch
done < "$CFG"

# Checkout code

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')
  branch=$(echo "$cfg" | awk -F: '{print $2}')

  $GIT worktree add $WD/$name $branch
done < "$CFG"

# Build and install branches
# TODO: support no-static branch

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')
  branch=$(echo "$cfg" | awk -F: '{print $2}')

  (
    cd $WD/$name

    cat <<EOF > bootstrap.toml
# See bootstrap.example.toml for documentation of available options
#
profile = "compiler"  # Includes one of the default files in src/bootstrap/defaults
change-id = 138986

[rust]
channel = "nightly"
debug-assertions = false

[llvm]
assertions = true
EOF

    if ! ./x build -j$J library; then
      # CI LLVM no longer available so need to copy manually
      cp -r $CI_LLVM build/x86_64-unknown-linux-gnu
      ./x build -j$J library
    fi

    rustup toolchain link $name build/host/stage1
  )
done < "$CFG"

# Run tests

toolchains=''

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')

  (
    cd $WD/$name

    cat <<EOF > bootstrap.toml
# See bootstrap.example.toml for documentation of available options
#
profile = "compiler"  # Includes one of the default files in src/bootstrap/defaults
change-id = 138986

[rust]
channel = "nightly"
debug-assertions = false

[llvm]
assertions = true
EOF

    if ! ./x build -j$J library; then
      # CI LLVM no longer available so need to copy manually
      cp -r $CI_LLVM build/x86_64-unknown-linux-gnu
      ./x build -j$J library
    fi

    rustup toolchain link $name build/host/stage1
    toolchains="$toolchains $name"
  )
done < "$CFG"

$RUNALL --clone --runner-args "-j$J -v" $toolchains
