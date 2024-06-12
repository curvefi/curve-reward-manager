import ape
import pytest

@pytest.fixture(scope="session")
def alice(accounts):
    return accounts[0]

@pytest.fixture(scope="session")
# manager address
def bob(accounts):
    return accounts[1]

@pytest.fixture(scope="session")
# recovery address
# backup manager address
def charlie(accounts):
    return accounts[2]