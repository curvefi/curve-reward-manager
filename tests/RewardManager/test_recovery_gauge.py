import ape
import pytest
import sys


def test_recovery_gauge_reward_token(recovery_gauge, reward_token):
    assert recovery_gauge.reward_token() == reward_token

def test_recovery_gauge_recovery_address(charlie, recovery_gauge):
    assert recovery_gauge.recovery_address() == charlie

def test_recovery_gauge_deposit_reward_token(bob, recovery_gauge, reward_token):
    balance = reward_token.balanceOf(bob)
    assert reward_token.approve(recovery_gauge, balance, sender=bob)
    print(balance)
    recovery_gauge.deposit_reward_token(reward_token, balance, sender=bob)


def test_recovery_gauge_recover_token(alice, bob, charlie, recovery_gauge, reward_token):
    balance = reward_token.balanceOf(bob)
    assert reward_token.approve(recovery_gauge, balance, sender=bob)
    recovery_gauge.deposit_reward_token(reward_token, balance, sender=bob)
    
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert balance_recoverd == balance