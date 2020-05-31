# QNAS

QNAS is quick and simple NAS server, designed for Open PS2 Loader and the Raspberry Pi.

It is booting in 10 seconds, and has support for most popular file systems like FAT32, EXFAT, NTFS, EXT2, EXT3, EXT4, BTRFS, F2FS, XFS.

After boot it will serve your USB stick at `\\192.168.1.5\sda1`

## Features
* Samba 4.0
* File systems support:
  * FAT32
  * EXFAT
  * NTFS
  * EXT2
  * EXT3
  * EXT4
  * BTRFS
  * F2FS
  * XFS
* Booting in 10 seconds
* Built-in few tools:
  * Python 3
  * Fsck
  * TcpDump
* Boards support:
  * Raspberry Pi A, B, A+ or B+
  * Raspberry Pi 2 B
  * Raspberry Pi 3 B and B+
  * Raspberry Pi 4 B
  * Orange Pi PC
* Easy customization by own `/media/sda1/rc.local` file
* Based on Buildroot

## Basic usage
Just flash IMG file for your board from [releases](https://github.com/skazanyNaGlany/qnas/releases) to your SD card, connect your USB stick with your files and SD card to the SBC and run it. After a while it will serve your files at `\\192.168.1.5\sda1`

All builds for supported boards are located in [releases](https://github.com/skazanyNaGlany/qnas/releases) section.

## Advanced usage
It is possible to provide own `rc.local` file at your USB stick, which will be used instead of default `/etc/rc.local`

### Example of custom `rc.local` file
`/media/sda1/rc.local`:
```
#!/bin/sh

ifconfig eth0 inet 192.168.1.100 netmask 255.255.255.0 up

smbd -s /etc/samba/smb.conf

```

In that custom `rc.local` file we will change QNAS default IP address to `192.168.1.100`, so after boot it will serve files under `\\192.168.1.100\sda1` instead of `\\192.168.1.5\sda1`

Make sure your custom `rc.local` file has `+x` executable flag enabled, if you are using file system other than EXFAT, FAT32, NTFS on your USB stick.


## Second advanced usage
Of course along with your own `rc.local` you can also provide custom Samba configuration file, just place it in your USB stick and run `smbd` with it. 

### Example of custom `rc.local` and `smb.conf` file

`/media/sda1/rc.local`:
```
#!/bin/sh

ifconfig eth0 inet 192.168.1.100 netmask 255.255.255.0 up

smbd -s /media/sda1/smb.conf

```

`/media/sda1/smb.conf`:
```
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
```

## Build for other board
### Prerequirements
There are few packages needed by Buildroot:
```
sudo apt-get install repo git-core gitk git-gui gcc-arm-linux-gnueabihf u-boot-tools device-tree-compiler gcc-aarch64-linux-gnu mtools parted libudev-dev libusb-1.0-0-dev python-linaro-image-tools linaro-image-tools autoconf autotools-dev libsigsegv2 m4 intltool libdrm-dev curl sed make binutils build-essential gcc g++ bash patch gzip bzip2 perl tar cpio python unzip rsync file bc wget libncurses5 libqt4-dev libglib2.0-dev libgtk2.0-dev libglade2-dev cvs git mercurial rsync openssh-client subversion asciidoc w3m dblatex graphviz python-matplotlib libc6 libssl-dev texinfo liblz4-tool genext2fs virtualenv
```

### Build process
You can easily build QNAS for other board with these easy steps:
```
$ git clone https://github.com/buildroot/buildroot.git
$ cd buildroot
$ git clone https://github.com/skazanyNaGlany/qnas.git qnas
$ qnas/configure.sh
$ make menuconfig
$ # Perform some changes before the build or just save without any changes. That step is required even if you will not change the config.
$ make
```

Make sure that you have internet connection since Buildroot will download some additional packages during build.

After few hours you should get your IMG file ready to flash to your SD card at `output/images/sdcard.img`


## Other tips
You can access your share at Windows by `\\192.168.1.5/sda1` or `smb://192.168.1.5/sda1/` at Linux.

You can test your build with QEMU using such command:
`qemu-system-arm -kernel e:\projects\kernel-qemu-4.4.34-jessie -append "root=/dev/sda2 panic=1 rootfstype=ext4 quiet" -hda e:\projects\sdcard.img -cpu arm1176 -m 256 -M versatilepb -serial none -nic user,hostfwd=tcp::1139-:139`


