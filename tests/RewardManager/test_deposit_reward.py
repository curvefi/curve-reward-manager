import ape
import pytest
import sys

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
    reward_manager.deposit_reward_token(recovery_gauge, 10 ** 18,  sender=bob)


def test_reward_manager_deposit(alice, bob, charlie, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 17
    reward_manager.deposit_reward_token(recovery_gauge, amount,  sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert amount == balance_recoverd

# send reward token to reward manager contract, then deposit_reward_tokens
def test_reward_manager_from_contract(alice, bob, charlie, reward_token, recovery_gauge, reward_manager):
    amount = 10 ** 16
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == 0
    reward_token.transferFrom(bob, reward_manager, amount, sender=bob)
    reward_manager_balance = reward_token.balanceOf(reward_manager, sender=alice)
    assert reward_manager_balance == amount
    reward_manager.deposit_reward_token_from_contract(recovery_gauge, amount, sender=bob)
    assert recovery_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(charlie, sender=alice)
    assert amount == balance_recoverd
    assert amount == reward_manager_balance

def test_reward_manager_revert(alice, recovery_gauge, reward_manager):
    with ape.reverts("dev: only reward managers can call this function"):
        reward_manager.deposit_reward_token(recovery_gauge, 10 ** 18,  sender=alice)

def test_reward_manager_calc_current_apr(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    current_apr = reward_manager.calc_current_apr(recovery_gauge, 397157 * 10000, 8739 , sender=bob)
    print(current_apr)


def test_reward_manager_calc_optimal_apr_record(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    new_apr = reward_manager.set_optimal_receiver_data(recovery_gauge, 397157 * 10000, int(0.8739 * 10000) , int(0.2 * 10000), sender=bob)

    assert reward_manager.reward_receivers_data(recovery_gauge).tvl == 3971570000
    print(reward_manager.reward_receivers_data(recovery_gauge).tvl)

    assert reward_manager.reward_receivers_data(recovery_gauge).token_price == 8739
    print(reward_manager.reward_receivers_data(recovery_gauge).token_price)

    assert reward_manager.reward_receivers_data(recovery_gauge)._target_apr == 2000
    print(reward_manager.reward_receivers_data(recovery_gauge).target_apr)

    assert reward_manager.reward_receivers_data(recovery_gauge).token_amount == 1743153500000000000000
    print(reward_manager.reward_receivers_data(recovery_gauge).token_amount)

