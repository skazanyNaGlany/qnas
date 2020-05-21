#!python3

import os

exec_filepath = os.path.realpath(__file__)

DIRPATH = exec_filepath[0:len(exec_filepath)-len(os.path.basename(__file__))]
CONFIG_PATHNAME = os.path.realpath(os.path.join(DIRPATH, '..', '.config'))


CUSTOM_CONFIG = '''
BR2_PACKAGE_BTRFS_PROGS=y
BR2_PACKAGE_CIFS_UTILS=y
BR2_PACKAGE_CMOCKA=y
BR2_PACKAGE_DOSFSTOOLS=y
BR2_PACKAGE_DOSFSTOOLS_FATLABEL=y
BR2_PACKAGE_DOSFSTOOLS_FSCK_FAT=y
BR2_PACKAGE_DOSFSTOOLS_MKFS_FAT=y
BR2_PACKAGE_E2FSPROGS=y
BR2_PACKAGE_E2FSPROGS_FSCK=y
BR2_PACKAGE_E2TOOLS=y
BR2_PACKAGE_EXFAT=y
BR2_PACKAGE_EXFATPROGS=y
BR2_PACKAGE_EXFAT_UTILS=y
BR2_PACKAGE_F2FS_TOOLS=y
BR2_PACKAGE_GMP=y
BR2_PACKAGE_GNUTLS=y
BR2_PACKAGE_HAS_ZLIB=y
BR2_PACKAGE_KVM_UNIT_TESTS_ARCH_SUPPORTS=y
BR2_PACKAGE_LIBEASTL_ARCH_SUPPORTS=y
BR2_PACKAGE_LIBFUSE=y
BR2_PACKAGE_LIBGCRYPT=y
BR2_PACKAGE_LIBGPG_ERROR=y
BR2_PACKAGE_LIBICONV=y
BR2_PACKAGE_LIBTASN1=y
BR2_PACKAGE_LIBTIRPC=y
BR2_PACKAGE_LIBZLIB=y
BR2_PACKAGE_LZO=y
BR2_PACKAGE_NETTLE=y
BR2_PACKAGE_NTFS_3G=y
BR2_PACKAGE_NTFS_3G_ENCRYPTED=y
BR2_PACKAGE_NTFS_3G_NTFSPROGS=y
BR2_PACKAGE_PCRE=y
BR2_PACKAGE_POPT=y
BR2_PACKAGE_PROVIDES_ZLIB="libzlib"
BR2_PACKAGE_UTIL_LINUX=y
BR2_PACKAGE_UTIL_LINUX_LIBBLKID=y
BR2_PACKAGE_UTIL_LINUX_LIBUUID=y
BR2_PACKAGE_VALGRIND_ARCH_SUPPORTS=y
BR2_PACKAGE_WINE_ARCH_SUPPORTS=y
BR2_PACKAGE_XFSPROGS=y
BR2_PACKAGE_ZLIB=y
BR2_PACKAGE_SAMBA4=y
BR2_PACKAGE_SAMBA4_AD_DC=y
BR2_PACKAGE_SAMBA4_ADS=y
BR2_PACKAGE_SAMBA4_SMBTORTURE=y
BR2_PACKAGE_TCPDUMP=y
BR2_PACKAGE_TCPDUMP_SMB=y
BR2_TOOLCHAIN_BUILDROOT_WCHAR=y
BR2_TARGET_ROOTFS_EXT2_SIZE="200M"
BR2_ROOTFS_POST_BUILD_SCRIPT="vsnas/vsnasinit.sh"
'''


print('Patching', CONFIG_PATHNAME)

def comment_config_out_keys():
    print('Commenting out keys')

    with open(CONFIG_PATHNAME, 'r+') as f:
        current_config_lines = f.read().split('\n')
        len_current_config_lines = len(current_config_lines)

        for iline in CUSTOM_CONFIG.splitlines():
            iline = iline.strip()

            if iline.startswith('# ') and iline.endswith(' is not set'):
                ikey = iline.split()[1] + '='
            else:
                ikey = iline.split('=')[0] + '='

            for iconfigindex in range(len_current_config_lines):
                if current_config_lines[iconfigindex] == '# vsNAS customized config':
                    break

                if current_config_lines[iconfigindex].startswith(ikey):
                    current_config_lines[iconfigindex] = '# ' + current_config_lines[iconfigindex].strip()
                    print(ikey[:-1])

        f.seek(0)
        f.write('\n'.join(current_config_lines))


def write_custom_config():
    print('Patching')

    with open(CONFIG_PATHNAME, 'a') as f:
        f.write('\n')
        f.write('#\n')
        f.write('# vsNAS customized config\n')
        f.write('#\n')
        f.write(CUSTOM_CONFIG)
        f.write('\n')


comment_config_out_keys()
write_custom_config()
