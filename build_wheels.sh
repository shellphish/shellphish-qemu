#!/bin/bash
set -ex

checkout_dir=$(realpath $(dirname $0))

docker build -t shellphish_qemu_build_image -f - $checkout_dir << EOF
# This is OK because all binaries are static
FROM ubuntu:focal

ENV DEBIAN_FRONTEND="noninteractive"

RUN sed -i -E "s/^deb (.+)$/deb \\1\\ndeb-src \\1\\n/g" /etc/apt/sources.list
RUN apt-get update; apt-get build-dep -y qemu
RUN apt-get install -y python3-setuptools python3-pip python2 ninja-build unzip patchelf
RUN pip3 install wheel auditwheel

RUN useradd build
USER build

WORKDIR /build
CMD python3 setup.py bdist_wheel --plat-name manylinux_2_24_x86_64 && \
    auditwheel repair --plat manylinux_2_24_x86_64 dist/*.whl
EOF

docker run --rm --name shellphish_qemu_build -v $checkout_dir:/build -t shellphish_qemu_build_image
