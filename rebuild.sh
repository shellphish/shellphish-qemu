#!/bin/bash
set -eux

rm -rf shellphish-qemu-cgc-base/
rm -rf shellphish-qemu-cgc-tracer/
rm -f bin/shellphish-qemu-cgc-base
rm -f bin/shellphish-qemu-cgc-tracer

pip install -e .
python setup.py bdist_wheel

