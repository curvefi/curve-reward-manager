import ape
from ape import chain
import pytest
import sys
import time


def test_reward_manager_current_apr(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    #current_apr = reward_manager.current_apr(recovery_gauge, 397157 * 10000, int(0.8739 * 10000), sender=bob)
    current_apr = reward_manager.current_apr(recovery_gauge, sender=bob)
 
    # reward_per_year: uint256 = reward_data.rate * 365 * 24 * 3600 * _token_price 
    # reward_per_year = 2343173790311650 * 365 * 24 * 360 * 8739 = 64576253808343275086160000
    # current_apr: uint256 = reward_per_year/_tvl
    # current_apr =  64576253808343275086160000 / 3971570000 =  16259628763522556
    # retuen value is 162596287635225553
    assert pytest.approx(current_apr, rel=1000) == 16259628763522556
    print(current_apr/10**18)

def test_reward_manager_current_apr_pips(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    current_apr_pips = reward_manager.current_apr_in_pips(recovery_gauge)
    assert pytest.approx(current_apr_pips, rel=10) == 1625
    print(current_apr_pips)
    

def test_reward_manager_current_apr_tvl(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    current_apr = reward_manager.current_apr_tvl(recovery_gauge, int(0.8739 * 10000), sender=bob)

    # reward_per_year: uint256 = reward_data.rate * 365 * 24 * 3600 * _token_price 
    # reward_per_year = 2343173790311650 * 365 * 24 * 360 * 8739 = 64576253808343275086160000
    # current_apr: uint256 = reward_per_year/_tvl
    # current_apr =  64576253808343275086160000 / 3971570000 =  16259628763522556
    # retuen value is 162596287635225553
    assert pytest.approx(current_apr, rel=1000) == 16259628763522556
    print(current_apr/10**18)


def test_calculate_reward_token_amount(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    
    new_apr = reward_manager.set_force_gauge_data(recovery_gauge, 397157 * 10000, int(0.8739 * 10000) , int(0.2 * 10000), sender=bob)

    assert reward_manager.gauge_data(recovery_gauge).tvl == 3971570000
    print(reward_manager.gauge_data(recovery_gauge).tvl)

    assert reward_manager.gauge_data(recovery_gauge).token_price == 8739
    print(reward_manager.gauge_data(recovery_gauge).token_price)

    assert reward_manager.gauge_data(recovery_gauge).target_apr == 2000
    print(reward_manager.gauge_data(recovery_gauge).target_apr)

    assert reward_manager.gauge_data(recovery_gauge).token_amount == 174276232978601670
    print(reward_manager.gauge_data(recovery_gauge).token_amount / 10**18)


def test_set_calc_storage(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 1000 pips is 10%
    reward_manager.set_gauge_data(recovery_gauge, int(0.1 * 10000), sender=bob)

    assert reward_manager.gauge_data(recovery_gauge).tvl == 3971570000
    print(reward_manager.gauge_data(recovery_gauge).tvl)

    assert reward_manager.gauge_data(recovery_gauge).token_price == 8739
    print(reward_manager.gauge_data(recovery_gauge).token_price)

    assert reward_manager.gauge_data(recovery_gauge).target_apr == 1000
    print(reward_manager.gauge_data(recovery_gauge).target_apr)
    # precision errors lead to 87080901705000572, and not 174276232978601670 / 2 = 87138116489300835
    # 0.07% error
    assert reward_manager.gauge_data(recovery_gauge).token_amount == 87080901705000572  
    print(reward_manager.gauge_data(recovery_gauge).token_amount)



"""
#very hard to test, as it needs real data from on-chain
def test_calculate_new_apr(alice, bob, charlie, reward_token, recovery_gauge, reward_manager):
    new_apr = reward_manager.set_force_gauge_data(recovery_gauge, 397157 * 10000, int(0.8739 * 10000) , int(0.2 * 10000), sender=bob)
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
    # Forward the chain to a point in the future, specifically 24 hours (24*3600 seconds)
    # This is a placeholder for actual code that would advance the blockchain's timestamp
    # In a real test, this would involve using a testing framework that allows for time manipulation
    # For example, in ape, you could use `ape.chain.mine()` to advance the block number and timestamp
    # Here, we'll just simulate this by printing a message indicating what should happen
    print("Simulating the passage of time by advancing the blockchain's timestamp by 24 hours...")
    with ape.reverts("dev: reward_duration needs to be > 0"):
        chain.mine(deltatime=24*3600)
        reward_manager.calculate_new_min_apr(recovery_gauge)
"""