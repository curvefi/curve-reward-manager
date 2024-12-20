import ape
import pytest
import sys

DAY = 86400
WEEK = 604800
def test_reward_manager_manager(bob, charlie, reward_manager):
    assert reward_manager.managers(0) == bob
    assert reward_manager.managers(1) == charlie

def test_reward_manager_reward_token(bob, reward_token, reward_manager):
    assert reward_manager.reward_token() == reward_token

def test_reward_manager_receivers(bob, recovery_gauge, reward_manager):
    reward_receivers = reward_manager.reward_receivers(0)
    print(reward_receivers)
    assert recovery_gauge == reward_receivers

def test_reward_manager_deposit(bob, recovery_gauge, reward_manager):
    reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18,  sender=bob)

def test_reward_manager_deposit(alice, bob, charlie, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 17
    reward_manager.deposit_send_reward_token(recovery_gauge, amount,  sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert amount == balance_recoverd

# send reward token to reward manager contract, then deposit_reward_tokens
def test_reward_manager_send_reward_token(alice, bob, charlie, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 16
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == 0
    reward_token.transferFrom(bob, reward_manager, amount, sender=bob)
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == amount
    reward_manager.send_reward_token(recovery_gauge, amount, sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert amount == balance_recoverd
    assert amount == reward_manager_balance

def test_reward_manager_send_reward_token_epoch(alice, bob, charlie, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 16
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == 0
    reward_token.transferFrom(bob, reward_manager, amount, sender=bob)
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == amount
    reward_manager.send_reward_token(recovery_gauge, amount, 8 * DAY, sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert amount == balance_recoverd
    assert amount == reward_manager_balance

def test_reward_manager_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("dev: epoch duration must be between 3 days and a year"):
        reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18, 53 * WEEK, sender=alice)

def test_reward_manager_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("dev: epoch duration must be between 3 days and a year"):
        reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18, 2 * DAY, sender=alice)


def test_reward_manager_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("dev: only reward managers can call this function"):
        reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18,  sender=alice)

def test_reward_manager_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("dev: only reward managers can call this function"):
        reward_manager.send_reward_token(recovery_gauge, 10 ** 18,  sender=alice)
