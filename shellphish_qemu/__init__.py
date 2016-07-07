import os
import distutils

def qemu_path(platform):
    for basename in (
        'shellphish-qemu-%s' % platform,
        'shellphish-qemu-linux-%s' % platform,
        '%s' % platform,
    ):
        path = os.path.join(qemu_base(), basename)
        if os.path.exists(path):
            return path

    return "NOT_FOUND"

def qemu_base():
    if __file__.startswith(distutils.sysconfig.PREFIX):
        return os.path.join(distutils.sysconfig.PREFIX, 'bin')
    else:
        return os.path.join(os.path.dirname(__file__), '..', 'bin')
