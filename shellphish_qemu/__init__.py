import os
import distutils

def qemu_path(platform):
    basename = 'shellphish-qemu-%s' % platform
    if __file__.startswith(distutils.sysconfig.PREFIX):
        path = os.path.join(distutils.sysconfig.PREFIX, 'bin', basename)
    else:
        path = os.path.join(os.path.dirname(__file__), '..', 'bin', basename)

    return path if os.path.exists(path) else None
