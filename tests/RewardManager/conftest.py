import ape
import pytest

@pytest.fixture(scope="module")
def reward_token(project, alice, bob):
    reward_token = alice.deploy(project.TestToken)
    # mint token to bob
    reward_token.mint(bob, 10 ** 19, sender=alice)
    reward_token.approve(bob, 10 ** 19, sender=bob) 
    balance = reward_token.balanceOf(bob)
    print(balance)
    return reward_token

@pytest.fixture(scope="module")
def lost_token(project, alice, charlie):
    lost_token = alice.deploy(project.TestToken)
    # mint token to charlie
    lost_token.mint(charlie, 10 ** 19, sender=alice)
    lost_token.approve(charlie, 10 ** 19, sender=charlie)
    balance = lost_token.balanceOf(charlie)
    print(balance)
    return lost_token


@pytest.fixture(scope="module")
def recovery_gauge(project, alice, charlie, reward_token):
    # charlie is recovery address
    gauge = alice.deploy(project.RecoveryGauge, reward_token, charlie)
    return gauge

@pytest.fixture(scope="module")
def reward_manager(project, alice, bob, charlie, diana, reward_token, recovery_gauge):
    # bob manager address
    reward_manager_contract = alice.deploy(project.RewardManager, [bob, charlie], reward_token, [recovery_gauge], diana)
    reward_token.approve(reward_manager_contract, 10 ** 19, sender=bob) 
    print(reward_manager_contract)
    return reward_manager_contract