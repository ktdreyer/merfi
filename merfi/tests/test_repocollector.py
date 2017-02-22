from merfi.collector import RepoCollector, DebRepo, RpmRepo


class TestRepoCollector(object):

    def setup(self):
        self.paths = RepoCollector(path='/', _eager=False)

    def test_simple_rpm_tree(self, rpmrepos):
        path = rpmrepos / 'jewel' / 'el6'
        repos = RepoCollector(str(path))
        expected = [RpmRepo(str(path))]
        assert set(repos) == set(expected)

    def test_simple_deb_tree(self, debrepos):
        path = debrepos / 'jewel'
        repos = RepoCollector(str(path))
        expected = [DebRepo(str(path))]
        assert set(repos) == set(expected)

    def test_nested_rpm_trees(self, rpmrepos):
        repos = RepoCollector(str(rpmrepos))
        expected = [
            RpmRepo(str(rpmrepos.join('jewel').join('el6'))),
            RpmRepo(str(rpmrepos.join('jewel').join('el7'))),
            RpmRepo(str(rpmrepos.join('luminous').join('el6'))),
            RpmRepo(str(rpmrepos.join('luminous').join('el7'))),
        ]
        assert set(repos) == set(expected)

    def test_nested_deb_trees(self, debrepos):
        repos = RepoCollector(str(debrepos))
        expected = [
            DebRepo(str(debrepos.join('jewel'))),
            DebRepo(str(debrepos.join('luminous'))),
        ]
        assert set(repos) == set(expected)


def TestRpmRepo(object):

    def test_init(self, rpmrepos):
        path = str(rpmrepos / 'jewel' / 'el6')
        r = RpmRepo(path)
        assert isinstance(r, RpmRepo)

    def test_repomd(self, rpmrepos):
        path = str(rpmrepos / 'jewel' / 'el6')
        r = RpmRepo(path)
        expected = str(rpmrepos / 'jewel' / 'el6' / 'repomd.xml')
        assert r.repomd == expected

    def test_rpms(self, rpmrepos):
        path = str(rpmrepos / 'jewel' / 'el6')
        r = RpmRepo(path)
        expected = [str(rpmrepos / 'jewel' / 'el6' / 'test.el6.rpm')]
        assert set(r.rpms) == set(expected)


def TestDebRepo(object):

    def test_init(self, debrepos):
        path = str(debrepos / 'jewel')
        r = DebRepo(path)
        assert isinstance(r, DebRepo)

    def test_releases(self, debrepos):
        path = str(debrepos / 'jewel')
        r = DebRepo(path)
        expected = [
            str(debrepos / 'dists' / 'trusty' / 'Release'),
            str(debrepos / 'dists' / 'xenial' / 'Release'),
        ]
        assert set(r.releases) == set(expected)
