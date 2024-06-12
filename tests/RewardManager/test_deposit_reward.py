import ape
import pytest
import sys

def test_reward_manager_manager(bob, test_gauge, reward_manager):
    assert reward_manager.manager() == bob

def test_reward_manager_reward_token(bob, reward_token, reward_manager):
    assert reward_manager.reward_token() == reward_token

def test_reward_manager_receivers(bob, test_gauge, reward_manager):
    reward_receivers = reward_manager.reward_receivers(0)
    print(reward_receivers)
    assert test_gauge == reward_receivers

def test_reward_manager_deposit(bob, test_gauge, reward_manager):
    reward_manager.deposit_reward_token(test_gauge, 10 ** 18,  sender=bob)

def test_reward_manager_deposit(alice, bob, charlie, reward_token, test_gauge, reward_manager):
    amount = 10 ** 17
    reward_manager.deposit_reward_token(test_gauge, amount,  sender=bob)
    assert test_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert amount == balance_recoverd

def test_reward_manager_revert(alice, test_gauge, reward_manager):
    with ape.reverts("dev: only reward manager can call this function"):
        reward_manager.deposit_reward_token(test_gauge, 10 ** 18,  sender=alice)
