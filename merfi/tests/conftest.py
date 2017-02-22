import os
import pytest
import py

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


@pytest.fixture(scope="function")
def rpmrepos(request):
    """ Return a set of Yum repositories with .rpm files to sign. """
    return py.path.local(FIXTURES_DIR).join('rpmrepos')


@pytest.fixture(scope="function")
def debrepos(request):
    """ Return a set of Debian repositories to sign. """
    return py.path.local(FIXTURES_DIR).join('debrepos')
