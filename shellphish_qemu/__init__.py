import os

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
