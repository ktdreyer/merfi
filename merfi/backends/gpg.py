import os
import merfi
from merfi import logger, util
from merfi.backends import base


class Gpg(base.BaseBackend):
    help_menu = 'gpg handler for signing files'
    _help = """
Signs files with gpg. Crawls a given path looking for Yum and Debian repos.

Will perform these actions on 'repomd.xml' files:

    gpg --armor --detach-sig --output repomd.xml.asc repomd.xml

Will perform these actions on '.rpm' files:

    rpm --define ... --addsign filename.rpm

Will perform these actions on 'Release' files:

    gpg --armor --detach-sig --output Release.gpg Release
    gpg --clearsign --output InRelease Release

%s

Options:

Positional Arguments:

[path]        The path to crawl for repo files. Defaults to current
              working directory
"""
    executable = 'gpg'
    name = 'gpg'

    def sign_repomd(self, path):
        """ Sign a Yum repomd.xml file. """
        if merfi.config.get('check'):
            new_md_path = path + '.asc'
            logger.info('[CHECKMODE] signing: %s' % path)
            logger.info('[CHECKMODE] signed: %s' % new_md_path)
            return
        os.chdir(os.path.dirname(path))
        detached = ['gpg', '--batch', '--yes', '--armor', '--detach-sig',
                    '--output', 'repomd.xml.asc', 'repomd.xml']
        logger.info('signing: %s' % path)
        util.run(detached)

    def sign_rpm(self, rpm):
        """ Sign a .rpm file. """
        if merfi.config.get('check'):
            logger.info('[CHECKMODE] signed: %s' % rpm.name)
            return
        rpmsign = ['rpm',
                   # '--define', '_gpg_name 782096AC', # Not needed?
                   '--define', '_signature gpg',
                   '--define', '__gpg /usr/bin/gpg',
                   '--define', '__gpg_check_password_cmd /bin/true',
                   '--define', '__gpg_sign_cmd %{__gpg} gpg --batch --no-verbose --no-armor --no-secmem-warning -u "%{_gpg_name}" -sbo %{__signature_filename} %{__plaintext_filename}',  # noqa: E501
                   '--addsign', rpm.path]
        logger.info('signing: %s' % rpm.path)
        util.run(rpmsign)

    def sign_release(self, path):
        """ Sign a Debian "Release" file. """
        if merfi.config.get('check'):
            new_gpg_path = path.split(path)[0]+'Release.gpg'
            new_in_path = path.split(path)[0]+'InRelease'
            logger.info('[CHECKMODE] signing: %s' % path)
            logger.info('[CHECKMODE] signed: %s' % new_gpg_path)
            logger.info('[CHECKMODE] signed: %s' % new_in_path)
            return
        os.chdir(os.path.dirname(path))
        detached = ['gpg', '--batch', '--yes', '--armor', '--detach-sig',
                    '--output', 'Release.gpg', 'Release']
        clearsign = ['gpg', '--batch', '--yes', '--clearsign', '--output',
                     'InRelease', 'Release']
        logger.info('signing: %s' % path)
        util.run(detached)
        util.run(clearsign)
