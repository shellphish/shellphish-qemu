import os
import sys
import time
import shutil
import random
import subprocess
import platform

from distutils.errors import LibError
from distutils.util import get_platform
from distutils.command.build import build as _build
from setuptools import setup
from setuptools.command.develop import develop as _develop

BIN_PATH = os.path.join("shellphish_qemu", "bin")

QEMU_REPO_PATH_CGC_BASE = "shellphish-qemu-cgc-base"
QEMU_REPO_PATH_LINUX = "shellphish-qemu-linux"
QEMU_LINUX_TRACER_PATCH = os.path.join("..", "patches", "tracer-qemu.patch")
QEMU_LINUX_UPDATE_PATCH = os.path.join("..", "patches", "ucontext.patch")
QEMU_CGC_COREDUMP_PATCH = os.path.join("..", "patches", "cgc-coredump.patch")

QEMU_PATH_CGC_TRACER = os.path.join(BIN_PATH, "shellphish-qemu-cgc-tracer")
QEMU_PATH_CGC_NXTRACER = os.path.join(BIN_PATH, "shellphish-qemu-cgc-nxtracer")
QEMU_PATH_CGC_BASE = os.path.join(BIN_PATH, "shellphish-qemu-cgc-base")

QEMU_PATH_LINUX_I386 = os.path.join(BIN_PATH, "shellphish-qemu-linux-i386")
QEMU_PATH_LINUX_X86_64 = os.path.join(BIN_PATH, "shellphish-qemu-linux-x86_64")
QEMU_PATH_LINUX_MIPS = os.path.join(BIN_PATH, "shellphish-qemu-linux-mips")
QEMU_PATH_LINUX_MIPSEL = os.path.join(BIN_PATH, "shellphish-qemu-linux-mipsel")
QEMU_PATH_LINUX_MIPS64 = os.path.join(BIN_PATH, "shellphish-qemu-linux-mips64")
QEMU_PATH_LINUX_PPC = os.path.join(BIN_PATH, "shellphish-qemu-linux-ppc")
QEMU_PATH_LINUX_PPC64 = os.path.join(BIN_PATH, "shellphish-qemu-linux-ppc64")
QEMU_PATH_LINUX_ARM = os.path.join(BIN_PATH, "shellphish-qemu-linux-arm")
QEMU_PATH_LINUX_AARCH64 = os.path.join(BIN_PATH, "shellphish-qemu-linux-aarch64")

ALL_QEMU_BINS = [
    QEMU_PATH_CGC_BASE,
    QEMU_PATH_CGC_TRACER,
    QEMU_PATH_CGC_NXTRACER,
    QEMU_PATH_LINUX_I386,
    QEMU_PATH_LINUX_X86_64,
    QEMU_PATH_LINUX_MIPS,
    QEMU_PATH_LINUX_MIPSEL,
    QEMU_PATH_LINUX_MIPS64,
    QEMU_PATH_LINUX_PPC,
    QEMU_PATH_LINUX_PPC64,
    QEMU_PATH_LINUX_ARM,
    QEMU_PATH_LINUX_AARCH64,
]

def _clone_cgc_qemu():
    # grab the CGC repo
    if not os.path.exists(QEMU_REPO_PATH_CGC_BASE) \
            or not os.path.exists(QEMU_REPO_PATH_CGC_BASE):
        TRACER_QEMU_REPO_CGC = "https://github.com/mechaphish/qemu-cgc"
        # since we're cloning from gitlab we'll need to try a couple times, since gitlab
        # has a cap on the number of ssh workers
        retrieved = False

        for _ in range(10):
            if subprocess.call(['git', 'clone', '--branch', 'base_cgc', '--depth=1', TRACER_QEMU_REPO_CGC, QEMU_REPO_PATH_CGC_BASE]) == 0:
                retrieved = True
                break
            else:
                time.sleep(random.randint(0, 10))

        if not retrieved:
            raise LibError("Unable to retrieve tracer qemu")

    # update tracer qemu for cgc
    if subprocess.call(['git', 'pull'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to retrieve cgc base qemu")

def _clone_linux_qemu():
    # grab the linux tarball
    if not os.path.exists(QEMU_REPO_PATH_LINUX):
        TRACER_QEMU_REPO_LINUX = "https://github.com/qemu/qemu.git"
        if subprocess.call(['git', 'clone', '--branch', 'v2.3.0', '--depth=1', TRACER_QEMU_REPO_LINUX, QEMU_REPO_PATH_LINUX]) != 0:
            raise LibError("Unable to retrieve qemu repository \"%s\"" % TRACER_QEMU_REPO_LINUX)
        #if subprocess.call(['git', '-C', QEMU_REPO_PATH_LINUX, 'checkout', 'tags/v2.3.0']) != 0:
        #   raise LibError("Unable to checkout version 2.3.0 of qemu")
        if subprocess.call(['git', '-C', QEMU_REPO_PATH_LINUX, 'apply', QEMU_LINUX_TRACER_PATCH]) != 0:
            raise LibError("Unable to apply tracer patch to qemu")
        if subprocess.call(['git', '-C', QEMU_REPO_PATH_LINUX, 'apply', QEMU_LINUX_UPDATE_PATCH]) != 0:
            raise LibError("Unable to apply ucontext_t update patch to qemu")
        if subprocess.call(['git', '-C', QEMU_REPO_PATH_CGC_BASE, 'apply', QEMU_CGC_COREDUMP_PATCH]) != 0:
            raise LibError("Unable to apply ucontext_t update patch to qemu")

def _build_qemus():
    if not os.path.exists(BIN_PATH):
        try:
            os.makedirs(BIN_PATH)
        except OSError:
            raise LibError("Unable to create bin directory")

    print("Configuring CGC tracer qemu...")
    if subprocess.call(['make', 'clean'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to clean shellphish-qemu-cgc-tracer")

    if subprocess.call(['./cgc_configure_tracer_opt'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to configure shellphish-qemu-cgc-tracer")

    print("Building CGC tracer qemu...")
    if subprocess.call(['make', '-j4'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to build shellphish-qemu-cgc")

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_CGC_BASE, "i386-linux-user", "qemu-i386"), QEMU_PATH_CGC_TRACER)

    if subprocess.call(['make', 'clean'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to clean shellphish-qemu-cgc")

    print("Configuring CGC nxtracer qemu...")
    if subprocess.call(['./cgc_configure_nxtracer_opt'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to configure shellphish-qemu-cgc-nxtracer")

    print("Building CGC nxtracer qemu...")
    if subprocess.call(['make', '-j4'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to build shellphish-qemu-cgc-nxtracer")

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_CGC_BASE, "i386-linux-user", "qemu-i386"), QEMU_PATH_CGC_NXTRACER)

    if subprocess.call(['make', 'clean'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to clean shellphish-qemu-cgc")

    print("Configuring CGC base qemu...")
    if subprocess.call(['./cgc_configure_opt'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to configure shellphish-qemu-cgc-base")

    print("Building CGC base qemu...")
    if subprocess.call(['make', '-j4'], cwd=QEMU_REPO_PATH_CGC_BASE) != 0:
        raise LibError("Unable to build shellphish-qemu-cgc")

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_CGC_BASE, "i386-linux-user", "qemu-i386"), QEMU_PATH_CGC_BASE)

    print("Configuring Linux qemu...")
    if subprocess.call(['./tracer-config'], cwd=QEMU_REPO_PATH_LINUX) != 0:
        raise LibError("Unable to configure shellphish-qemu-linux")
    print("Building Linux qemu...")
    if subprocess.call(['make', '-j4'], cwd=QEMU_REPO_PATH_LINUX) != 0:
        raise LibError("Unable to build shellphish-qemu-linux")


    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "i386-linux-user", "qemu-i386"), QEMU_PATH_LINUX_I386)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "x86_64-linux-user", "qemu-x86_64"), QEMU_PATH_LINUX_X86_64)

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "mipsel-linux-user", "qemu-mipsel"), QEMU_PATH_LINUX_MIPSEL)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "mips-linux-user", "qemu-mips"), QEMU_PATH_LINUX_MIPS)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "mips64-linux-user", "qemu-mips64"), QEMU_PATH_LINUX_MIPS64)

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "ppc-linux-user", "qemu-ppc"), QEMU_PATH_LINUX_PPC)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "ppc64-linux-user", "qemu-ppc64"), QEMU_PATH_LINUX_PPC64)

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "arm-linux-user", "qemu-arm"), QEMU_PATH_LINUX_ARM)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "aarch64-linux-user", "qemu-aarch64"), QEMU_PATH_LINUX_AARCH64)

    os.chmod(QEMU_PATH_CGC_BASE, 0o755)
    os.chmod(QEMU_PATH_CGC_TRACER, 0o755)
    os.chmod(QEMU_PATH_CGC_NXTRACER, 0o755)
    os.chmod(QEMU_PATH_LINUX_I386, 0o755)
    os.chmod(QEMU_PATH_LINUX_X86_64, 0o755)
    os.chmod(QEMU_PATH_LINUX_MIPSEL, 0o755)
    os.chmod(QEMU_PATH_LINUX_MIPS, 0o755)
    os.chmod(QEMU_PATH_LINUX_MIPS64, 0o755)
    os.chmod(QEMU_PATH_LINUX_PPC, 0o755)
    os.chmod(QEMU_PATH_LINUX_PPC64, 0o755)
    os.chmod(QEMU_PATH_LINUX_ARM, 0o755)
    os.chmod(QEMU_PATH_LINUX_AARCH64, 0o755)

    try:
        cgc_base_ver = subprocess.check_output([QEMU_PATH_CGC_BASE, '-version'])
        cgc_tracer_ver = subprocess.check_output([QEMU_PATH_CGC_TRACER, '-version'])
        cgc_nxtracer_ver = subprocess.check_output([QEMU_PATH_CGC_NXTRACER, '-version'])
        assert b'AFL' not in cgc_base_ver
        assert b'AFL' not in cgc_tracer_ver
        assert b'AFL' not in cgc_nxtracer_ver
        assert b'TRACER' not in cgc_base_ver
        assert b'TRACER' in cgc_tracer_ver
        assert b'TRACER' in cgc_nxtracer_ver
        assert b'enforce NX' not in cgc_base_ver    # Playing it safe
        assert b'enforce NX' not in cgc_tracer_ver  # Playing it safe
        assert b'enforce NX' in cgc_nxtracer_ver    # Mainly used by Antonio for CI tests
    except subprocess.CalledProcessError as e:
        raise LibError("Unable to check CGC qemu -version [ {} returned {}, output '{}' ]".format(e.cmd, e.returncode, e.output))
    except AssertionError:
        raise LibError("Wrong configuration for the CGC qemus! Make sure to clean, and check with -version")


    # remove the source directory after building
    #shutil.rmtree(QEMU_REPO_PATH_LINUX)
    #shutil.rmtree(QEMU_REPO_PATH_CGC)

class build(_build):
    def run(self):
            self.execute(_clone_cgc_qemu, (), msg="Cloning CGC QEMU")
            self.execute(_clone_linux_qemu, (), msg="Cloning Linux QEMU")
            self.execute(_build_qemus, (), msg="Building Tracer QEMU")
            _build.run(self)

class develop(_develop):
    def run(self):
            self.execute(_clone_cgc_qemu, (), msg="Cloning CGC QEMU")
            self.execute(_clone_linux_qemu, (), msg="Cloning Linux QEMU")
            self.execute(_build_qemus, (), msg="Building Tracer QEMU")
            _develop.run(self)

if 'bdist_wheel' in sys.argv and '--plat-name' not in sys.argv:
    idx = sys.argv.index('bdist_wheel') + 1
    sys.argv.insert(idx, '--plat-name')
    name = get_platform()
    if 'linux' in name:
        # linux_* platform tags are disallowed because the python ecosystem is fubar
        # linux builds should be built in the centos 5 vm for maximum compatibility
        # see https://github.com/pypa/manylinux
        # see also https://github.com/angr/angr-dev/blob/master/bdist.sh
        sys.argv.insert(idx + 1, 'manylinux1_' + platform.machine())
    else:
        # https://www.python.org/dev/peps/pep-0425/
        sys.argv.insert(idx + 1, name.replace('.', '_').replace('-', '_'))


setup(
    name='shellphish-qemu',
    version='0.9.9',
    description="A pip-installable set of qemus.",
    packages=['shellphish_qemu'],
    provides=['shellphish_qemu'],
    requires=['pkg_resources'],
    cmdclass={'build': build, 'develop': develop},
    zip_safe=True,
    include_package_data=True,
    package_data={
        'shellphish_qemu': ['bin/*']
    }
)
