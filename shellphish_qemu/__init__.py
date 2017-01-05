import os
import pkg_resources

__all__ = ('qemu_path', 'qemu_base', 'qemu_list')

def qemu_path(platform):
    for basename in (
        'shellphish-qemu-%s' % platform,
        'shellphish-qemu-linux-%s' % platform,
        '%s' % platform,
    ):
        path = os.path.join(qemu_base(), basename)
        if os.path.isfile(path):
            return path

    raise ValueError('Unable to find qemu for platform "%s"' % platform)

def qemu_base():
    return pkg_resources.resource_filename('shellphish_qemu', 'bin')

def qemu_list():
    qdir = os.listdir(qemu_base())
    prefix = 'shellphish-qemu-'
    pl = len(prefix)
    return sorted(x[pl:] for x in qdir if x.startswith(prefix))
