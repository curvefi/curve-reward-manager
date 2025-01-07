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

# send reward token to reward manager contract, then deposit_reward_tokens
def test_reward_manager_send_reward_token(alice, bob, diana, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 16
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == 0
    reward_token.transferFrom(bob, reward_manager, amount, sender=bob)
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == amount
    reward_manager.send_reward_token(recovery_gauge, amount, sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd
    assert amount == reward_manager_balance

def test_reward_manager_send_reward_token_epoch(alice, bob, diana, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 16
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == 0
    reward_token.transferFrom(bob, reward_manager, amount, sender=bob)
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == amount
    reward_manager.send_reward_token(recovery_gauge, amount, 8 * DAY, sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd
    assert amount == reward_manager_balance

def test_reward_manager_deposit_simple(bob, recovery_gauge, reward_manager):
    reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18,  sender=bob)

def test_reward_manager_deposit_token(alice, bob, diana, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 17
    reward_manager.deposit_send_reward_token(recovery_gauge, amount,  sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd

def test_reward_manager_deposit_epoch(alice, bob, diana, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 17
    reward_manager.deposit_send_reward_token(recovery_gauge, amount, 8 * DAY, sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd

def test_reward_manager_sent_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("only reward managers can call this function"):
        reward_manager.send_reward_token(recovery_gauge, 10 ** 18, sender=alice)

def test_reward_manager_epoch_revert_too_short(bob, recovery_gauge, reward_manager):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        reward_manager.send_reward_token(recovery_gauge, 10 ** 18, DAY, sender=bob)

def test_reward_manager_epoch_revert_too_long(bob, recovery_gauge, reward_manager):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        reward_manager.send_reward_token(recovery_gauge, 10 ** 18, 53 * WEEK, sender=bob)

def test_reward_manager_deposit_sent_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("only reward managers can call this function"):
        reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18, sender=alice)

def test_reward_manager_deposit_epoch_revert_too_short(bob, recovery_gauge, reward_manager):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18, DAY, sender=bob)

def test_reward_manager_deposit_epoch_revert_too_long(bob, recovery_gauge, reward_manager):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        reward_manager.deposit_send_reward_token(recovery_gauge, 10 ** 18, 53 * WEEK, sender=bob)

def test_recover_token(bob, charlie, diana, lost_token, reward_manager):
    amount = 10 ** 18
    lost_token.transferFrom(charlie, reward_manager, amount, sender=charlie)
    assert lost_token.balanceOf(reward_manager) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert lost_token.balanceOf(charlie) == 9 * amount
    # recover lost token to diana (recovery address)
    reward_manager.recover_token(lost_token, amount, sender=bob)
    assert lost_token.balanceOf(diana) == amount

def test_recover_reward_token(bob, charlie, diana, reward_token, reward_manager):
    amount = 10 ** 18
    reward_token.transferFrom(bob, reward_manager, amount, sender=bob)
    assert reward_token.balanceOf(reward_manager) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert reward_token.balanceOf(bob) == 9 * amount
    # recover lost token to diana (recovery address)
    reward_manager.recover_token(reward_token, amount, sender=bob)
    assert reward_token.balanceOf(diana) == amount

def test_recover_token_revert_manager(alice, lost_token, reward_manager):
    with ape.reverts("only reward managers can call this function"):
        reward_manager.recover_token(lost_token, 10 ** 18, sender=alice)

def test_recover_token_revert_amount(bob, lost_token, reward_manager):
    with ape.reverts("amount must be greater than 0"):
        reward_manager.recover_token(lost_token, 0,  sender=bob)


