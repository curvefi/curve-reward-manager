import ape
import pytest

@pytest.fixture(scope="module")
def reward_token(project, alice, bob):
    reward_token = alice.deploy(project.TestToken)
    # mint token to bob
    reward_token.mint(bob, 10 ** 19, sender=alice)
    reward_token.approve(bob, 10 ** 19, sender=bob) 
    balance = reward_token.balanceOf(bob)
    return reward_token

@pytest.fixture(scope="module")
def recovery_gauge(project, alice, charlie, reward_token):
    # charlie is recovery address
    gauge = alice.deploy(project.RecoveryGauge, reward_token, charlie)
    return gauge

@pytest.fixture(scope="module")
def reward_manager(project, alice, bob, charlie, reward_token, recovery_gauge):
    # bob manager address
    reward_manager_contract = alice.deploy(project.RewardManager, [bob, charlie], reward_token, [recovery_gauge] )
    reward_token.approve(reward_manager_contract, 10 ** 19, sender=bob) 
    reward_manager_contract.set_mock_gauge_data(recovery_gauge, sender=bob)
    #print(reward_manager_contract)
    return reward_manager_contract