import os
import shutil
import merfi
from merfi import logger
from merfi import util
from merfi.backends import base


class RpmSign(base.BaseBackend):
    help_menu = 'rpm-sign handler for signing files'
    _help = """
Signs files with rpm-sign. Crawls a given path looking for Yum and Debian
repos.

%s

Options

--key         Name of the key to use (see rpm-sign --list-keys)
--keyfile     Full path location of the public keyfile, for example
              /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
              or /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta
--nat         A NAT is between this system and the signing server.

Positional Arguments:

[path]        The path to crawl for signing release files. Defaults to current
              working directory
    """
    executable = 'rpm-sign'
    name = 'rpm-sign'
    options = ['--key', '--keyfile', '--nat']

    def clear_sign(self, path, command, outfile):
        """
        When doing a "clearsign" with rpm-sign, the output goes to stdout, so
        that needs to be captured and written to the default output file for
        clear signed signatures (InRelease).
        """
        logger.info('signing: %s' % path)
        out, err, code = util.run_output(command)
        absolute_directory = os.path.dirname(os.path.abspath(path))
        with open(os.path.join(absolute_directory, outfile), 'w') as f:
            f.write(out)

    def sign(self):
        self.keyfile = self.parser.get('--keyfile')
        if self.keyfile and not os.path.isfile(self.keyfile):
            raise RuntimeError('%s is not a file' % self.keyfile)
        self.key = self.parser.get('--key')
        if not self.key:
            raise RuntimeError('specify a --key for signing')
        self.nat = self.parser.get('--nat')
        repos = super(RpmSign, self).sign()
        self.add_keyfile_to_repos(repos)
        return repos

    def add_keyfile_to_repos(self, repos):
        if not self.keyfile:
            return
        logger.info('using keyfile "%s" as release.asc' % self.keyfile)
        for repo in repos:
            logger.info('placing release.asc in %s' % repo)
            if merfi.config.get('check'):
                logger.info('[CHECKMODE] writing release.asc')
            else:
                shutil.copyfile(
                    self.keyfile,
                    os.path.join(repo, 'release.asc'))

    def sign_repomd(self, path):
        """ Sign a Yum repomd.xml file. """
        if merfi.config.get('check'):
            new_md_path = path + '.asc'
            logger.info('[CHECKMODE] signing: %s' % path)
            logger.info('[CHECKMODE] signed: %s' % new_md_path)
            return
        os.chdir(os.path.dirname(path))
        detached = ['rpm-sign', '--key', self.key, '--detachsign',
                    'repomd.xml', '--output', 'repomd.xml.asc']
        return util.run(detached)

    def sign_release(self, path):
        if merfi.config.get('check'):
            new_gpg_path = path.split('Release')[0]+'Release.gpg'
            new_in_path = path.split('Release')[0]+'InRelease'
            logger.info('[CHECKMODE] signing: %s' % path)
            logger.info('[CHECKMODE] signed: %s' % new_gpg_path)
            logger.info('[CHECKMODE] signed: %s' % new_in_path)
            return

        clearsign = ['rpm-sign', '--key', self.key, '--clearsign', 'Release']
        detached = ['rpm-sign', '--key', self.key, '--detachsign',
                    'repomd.xml', '--output', 'repomd.xml.asc']
        if self.nat:
            detached.insert(1, '--nat')
            clearsign.insert(1, '--nat')
        logger.info('signing: %s' % path)
        util.run(detached)
        self.clear_sign(path, clearsign, 'InRelease')
