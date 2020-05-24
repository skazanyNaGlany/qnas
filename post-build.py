#!python3

import os
import io

# smb://192.168.1.5/sda1/
# qemu-system-arm -kernel e:\projects\kernel-qemu-4.4.34-jessie -append "root=/dev/sda2 panic=1 rootfstype=ext4 quiet" -hda e:\projects\sdcard.img -cpu arm1176 -m 256 -M versatilepb -serial none -nic user,hostfwd=tcp::1139-:139
# sudo apt-get install repo git-core gitk git-gui gcc-arm-linux-gnueabihf u-boot-tools device-tree-compiler gcc-aarch64-linux-gnu mtools parted libudev-dev libusb-1.0-0-dev python-linaro-image-tools linaro-image-tools autoconf autotools-dev libsigsegv2 m4 intltool libdrm-dev curl sed make binutils build-essential gcc g++ bash patch gzip bzip2 perl tar cpio python unzip rsync file bc wget libncurses5 libqt4-dev libglib2.0-dev libgtk2.0-dev libglade2-dev cvs git mercurial rsync openssh-client subversion asciidoc w3m dblatex graphviz python-matplotlib libc6 libssl-dev texinfo liblz4-tool genext2fs

base_dir = os.environ['BASE_DIR']
cmdline_txt_path = os.path.join(base_dir, 'images', 'rpi-firmware', 'cmdline.txt')
config_txt_path = os.path.join(base_dir, 'images', 'rpi-firmware', 'config.txt')
inittab_path = os.path.join(base_dir, 'target', 'etc', 'inittab')
interfaces_path = os.path.join(base_dir, 'target', 'etc', 'network', 'interfaces')
S91smb_path = os.path.join(base_dir, 'target', 'etc', 'init.d', 'S91smb')
rc_local_path = os.path.join(base_dir, 'target', 'etc', 'rc.local')
smb_conf_path = os.path.join(base_dir, 'target', 'etc', 'samba', 'smb.conf')
hostname_path = os.path.join(base_dir, 'target', 'etc', 'hostname')
issue_path = os.path.join(base_dir, 'target', 'etc', 'issue')
rcs_path = os.path.join(base_dir, 'target', 'etc', 'init.d', 'rcS')
media_sda1_path = os.path.join(base_dir, 'target', 'media', 'sda1')

rc_local_content = """
#!/bin/sh

# copy these steps for each drive
mkdir -p /media/sda1

mount -t ntfs -o umask=000 /dev/sda1 /media/sda1
mount -t btrfs /dev/sda1 /media/sda1
mount -o umask=000 /dev/sda1 /media/sda1

chmod 0777 /media/sda1

# run samba
smbd -s /etc/samba/smb.conf
"""

interfaces_content = """
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address 192.168.1.5
netmask 255.255.255.0
gateway 192.168.1.1
"""

smb_conf_content = """
[global]
    netbios name = qnas
    display charset = UTF-8
    bind interfaces only = yes
    server string = qnas
    unix charset = UTF-8
    workgroup = WORKGROUP
    browseable = yes
    deadtime = 120
    domain master = yes
    encrypt passwords = true
    enable core files = no
    guest account = nobody
    guest ok = yes
    invalid users = root
    local master = yes
    load printers = no
    map to guest = Bad User
    min protocol = LANMAN1
    max protocol = SMB2
    min receivefile size = 16384
    null passwords = yes
    obey pam restrictions = yes
    os level = 20
    passdb backend = smbpasswd
    preferred master = yes
    printable = no
    security = user
    smb encrypt = disabled
    smb passwd file = /etc/samba/smbpasswd
    socket options = TCP_NODELAY IPTOS_LOWDELAY SO_KEEPALIVE SO_RCVBUF=262144 SO_SNDBUF=262144
    syslog = 2
    use sendfile = yes
    writeable = yes
    keepalive = 30
    deadtime = 300
    log file = /tmp/samba.log
    read raw = yes
    write raw = yes
    wide links = yes
    getwd cache = yes
    stat cache = yes
    strict sync = no
    large readwrite = yes
    strict allocate = yes
    max xmit = 131072
    aio read size = 64360
    aio write size = 64360
    aio write behind = true
    write cache size = 12826144

# copy it for each drive
[sda1]
    path = /media/sda1
    read only = yes
    writable = yes
    guest ok = yes
    guest_only = yes
    browseable = yes
    force user = nobody
    create mask = 0777
    directory mask = 0777
"""


def file_extract_lines(filename):
    lines = []

    for iline in open(filename, 'r').readlines():
        lines.append(iline)

    return lines


def file_write_lines(filename, lines):
    with open(filename, 'w+') as f:
        f.writelines(lines)


def enable_overscan():
    lines = file_extract_lines(config_txt_path)

    for i, iline in enumerate(lines):
        if iline == 'disable_overscan=1\n':
            iline = '# disable_overscan=1\n'
            lines[i] = iline

            print('Overscan enabled')
            break

    file_write_lines(config_txt_path, lines)


def quiet_boot():
    file_write_lines(cmdline_txt_path, ['root=/dev/mmcblk0p2 rootwait console=tty1 console=ttyAMA0,115200 quiet'])


def disable_serial_console():
    lines = file_extract_lines(inittab_path)

    for i, iline in enumerate(lines):
        if iline.endswith(' # GENERIC_SERIAL\n'):
            lines[i] = '# ' + iline

            print('Serial console disabled')
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

            print('HDMI console enabled')
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

        print('SMB init script removed')


def write_smb_conf():
    open(smb_conf_path, 'w+').write(smb_conf_content.strip() + '\n')


def write_hostname():
    open(hostname_path, 'w+').write('qnas')


def write_issue():
    open(issue_path, 'w+').write('Welcome to QNAS\n')


def enable_rc_local2():
    lines = file_extract_lines(inittab_path)
    rc_local_run_entry = '::sysinit:/etc/rc.local\n'

    if rc_local_run_entry in lines:
        return

    for i, iline in enumerate(lines):
        if iline == '::sysinit:/etc/init.d/rcS\n':
            lines.insert(i + 1, rc_local_run_entry)

            print('/etc/rc.local enabled')
            break

    file_write_lines(inittab_path, lines)


def create_directories():
    os.mkdir(media_sda1_path, 0o777)


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

print(config_txt_path)
print(cmdline_txt_path)
print(inittab_path)
print(interfaces_path)
print(rc_local_path)
print(hostname_path)
print(issue_path)
