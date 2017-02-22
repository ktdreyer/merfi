from merfi import base, logger, util
from merfi.collector import RepoCollector
from tambo import Transport


class BaseBackend(base.BaseCommand):

    options = []
    parser = None

    def parse_args(self):
        self.parser = Transport(self.argv, options=self.options)
        self.parser.catch_help = self.help()
        self.parser.parse_args()
        self.path = util.infer_path(self.parser.unknown_commands)
        self.check_dependency()
        self.sign()

    def sign(self):
        logger.info('Starting path collection, looking for files to sign')
        repos = RepoCollector(self.path)

        if repos:
            logger.info('%s repos found' % len(repos))
        else:
            logger.warning('No paths found that matched')

        for repo in repos:
            for path in getattr(repo, 'repomd', set()):
                self.sign_repomd(path)
            for rpm in getattr(repo, 'rpms', set()):
                self.sign_rpm(rpm)
            for path in getattr(repo, 'releases', set()):
                self.sign_release(path)

        return repos

    def sign_repomd(self, path):
        raise NotImplemented()

    def sign_rpm(self, rpm):
        raise NotImplemented()

    def sign_release(self, path):
        raise NotImplemented()
