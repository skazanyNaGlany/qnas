#!/bin/sh

set -u
set -e

python3 $PWD/`dirname $0`/post-build.py

