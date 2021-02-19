#!/bin/bash
set -ex

checkout_dir=$(realpath $(dirname $0))

docker build -t shellphish_qemu_build_image -f - $checkout_dir << EOF
FROM quay.io/pypa/manylinux_2_24_x86_64

RUN sed -i -E "s/^deb (.+)$/deb \\1\\ndeb-src \\1\\n/g" /etc/apt/sources.list
RUN apt-get update; apt-get build-dep -y qemu

WORKDIR /build
CMD /opt/python/cp36-cp36m/bin/python setup.py bdist_wheel --plat-name manylinux_2_24_x86_64 && \
    auditwheel repair --plat manylinux_2_24_x86_64 --strip dist/*.whl
EOF

docker run --rm --name shellphish_qemu_build -v $checkout_dir:/build -t shellphish_qemu_build_image
