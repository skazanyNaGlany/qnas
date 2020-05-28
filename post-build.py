#!python3

import os
import io

# smb://192.168.1.5/sda1/
# qemu-system-arm -kernel e:\projects\kernel-qemu-4.4.34-jessie -append "root=/dev/sda2 panic=1 rootfstype=ext4 quiet" -hda e:\projects\sdcard.img -cpu arm1176 -m 256 -M versatilepb -serial none -nic user,hostfwd=tcp::1139-:139
# sudo apt-get install repo git-core gitk git-gui gcc-arm-linux-gnueabihf u-boot-tools device-tree-compiler gcc-aarch64-linux-gnu mtools parted libudev-dev libusb-1.0-0-dev python-linaro-image-tools linaro-image-tools autoconf autotools-dev libsigsegv2 m4 intltool libdrm-dev curl sed make binutils build-essential gcc g++ bash patch gzip bzip2 perl tar cpio python unzip rsync file bc wget libncurses5 libqt4-dev libglib2.0-dev libgtk2.0-dev libglade2-dev cvs git mercurial rsync openssh-client subversion asciidoc w3m dblatex graphviz python-matplotlib libc6 libssl-dev texinfo liblz4-tool genext2fs

exec_filepath = os.path.realpath(__file__)

DIRPATH = exec_filepath[0:len(exec_filepath)-len(os.path.basename(__file__)) - 1]
DIRPATH_BASENAME = os.path.basename(DIRPATH)
CONFIG_PATHNAME = os.path.realpath(os.path.join(DIRPATH, '..', '.config'))
VERSION_PATHNAME = os.path.realpath(os.path.join(DIRPATH, 'VERSION'))

APP_NAME, APP_UNIXNAME, APP_VERSION = open(VERSION_PATHNAME).read().splitlines()

base_dir = os.environ['BASE_DIR']
cmdline_txt_path = os.path.join(base_dir, 'images', 'rpi-firmware', 'cmdline.txt')
config_txt_path = os.path.join(base_dir, 'images', 'rpi-firmware', 'config.txt')
inittab_path = os.path.join(base_dir, 'target', 'etc', 'inittab')
interfaces_path = os.path.join(base_dir, 'target', 'etc', 'network', 'interfaces')
local_interfaces_path = os.path.join(DIRPATH, 'etc', 'network', 'interfaces')
S91smb_path = os.path.join(base_dir, 'target', 'etc', 'init.d', 'S91smb')
rc_local_path = os.path.join(base_dir, 'target', 'etc', 'rc.local')
local_rc_local_path = os.path.join(DIRPATH, 'etc', 'rc.local')
smb_conf_path = os.path.join(base_dir, 'target', 'etc', 'samba', 'smb.conf')
local_smb_conf_path = os.path.join(DIRPATH, 'etc', 'samba', 'smb.conf')
hostname_path = os.path.join(base_dir, 'target', 'etc', 'hostname')
issue_path = os.path.join(base_dir, 'target', 'etc', 'issue')
rcs_path = os.path.join(base_dir, 'target', 'etc', 'init.d', 'rcS')
media_sda1_path = os.path.join(base_dir, 'target', 'media', 'sda1')

rc_local_content = open(local_rc_local_path).read().strip().format(
    APP_NAME=APP_NAME,
    APP_UNIXNAME=APP_UNIXNAME,
    APP_VERSION=APP_VERSION
)
interfaces_content = open(local_interfaces_path).read().strip().format(
    APP_NAME=APP_NAME,
    APP_UNIXNAME=APP_UNIXNAME,
    APP_VERSION=APP_VERSION
)
smb_conf_content = open(local_smb_conf_path).read().strip().format(
    APP_NAME=APP_NAME,
    APP_UNIXNAME=APP_UNIXNAME,
    APP_VERSION=APP_VERSION
)


def lprint(*args):
    print(APP_NAME + ':', *args)


def file_extract_lines(filename):
    lines = []

    for iline in open(filename, 'r').readlines():
        lines.append(iline)

    return lines


def file_write_lines(filename, lines):
    with open(filename, 'w+') as f:
        f.writelines(lines)


def enable_overscan():
    try:
        lines = file_extract_lines(config_txt_path)

        for i, iline in enumerate(lines):
            if iline == 'disable_overscan=1\n':
                iline = '# disable_overscan=1\n'
                lines[i] = iline

                lprint('Overscan enabled')
                break

        file_write_lines(config_txt_path, lines)
    except FileNotFoundError:
        lprint('Unable to open', config_txt_path, 'perhaps your board does not support it.')


def quiet_boot():
    try:
        file_write_lines(cmdline_txt_path, ['root=/dev/mmcblk0p2 rootwait console=tty1 console=ttyAMA0,115200 quiet'])
    except FileNotFoundError:
        lprint('Unable to open', cmdline_txt_path, 'perhaps your board does not support it.')


def disable_serial_console():
    lines = file_extract_lines(inittab_path)

    for i, iline in enumerate(lines):
        if iline.endswith(' # GENERIC_SERIAL\n'):
            lines[i] = '# ' + iline

            lprint('Serial console disabled')
            break

    file_write_lines(inittab_path, lines)


def enable_hdmi_console():
    lines = file_extract_lines(inittab_path)
    hdmi_console_run_entry = 'tty1::respawn:/sbin/getty -L  tty1 0 vt100 # HDMI console\n'

    if hdmi_console_run_entry in lines:
        return

    for i, iline in enumerate(lines):
        if iline == '::sysinit:/etc/init.d/rcS\n':
            lines.insert(i + 1, hdmi_console_run_entry)

            lprint('HDMI console enabled')
            break

    file_write_lines(inittab_path, lines)


def write_rc_local():
    open(rc_local_path, 'w+').write(rc_local_content.strip() + '\n')
    os.chmod(rc_local_path, 0o777)


def set_static_ip():
    open(interfaces_path, 'w+').write(interfaces_content.strip() + '\n')


def remove_smb_init():
    if os.path.exists(S91smb_path):
        os.remove(S91smb_path)

        lprint('SMB init script removed')


def write_smb_conf():
    open(smb_conf_path, 'w+').write(smb_conf_content.strip() + '\n')


def write_hostname():
    open(hostname_path, 'w+').write(APP_UNIXNAME)


def write_issue():
    open(issue_path, 'w+').write('Welcome to {APP_NAME} {APP_VERSION}\n'.format(APP_NAME=APP_NAME, APP_VERSION=APP_VERSION))


def enable_rc_local2():
    lines = file_extract_lines(inittab_path)
    rc_local_run_entry = '::sysinit:/etc/rc.local\n'

    if rc_local_run_entry in lines:
        return

    for i, iline in enumerate(lines):
        if iline == '::sysinit:/etc/init.d/rcS\n':
            lines.insert(i + 1, rc_local_run_entry)

            lprint('/etc/rc.local enabled')
            break

    file_write_lines(inittab_path, lines)


def create_directories():
    try:
        os.mkdir(media_sda1_path, 0o777)
    except FileExistsError:
        pass


lprint('Customizing target file system at', base_dir)
enable_overscan()
quiet_boot()
disable_serial_console()
enable_hdmi_console()
set_static_ip()
write_rc_local()
remove_smb_init()
write_smb_conf()
write_hostname()
write_issue()
enable_rc_local2()
create_directories()

lprint('Affected files:')
lprint(config_txt_path)
lprint(cmdline_txt_path)
lprint(inittab_path)
lprint(interfaces_path)
lprint(rc_local_path)
lprint(hostname_path)
lprint(issue_path)
