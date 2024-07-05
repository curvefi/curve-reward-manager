import ape
import pytest
import sys


def test_reward_manager_current_apr(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    current_apr = reward_manager.current_apr(recovery_gauge, 397157 * 10000, int(0.8739 * 10000), sender=bob)

    # reward_per_year: uint256 = reward_data.rate * 365 * 24 * 3600 * _token_price 
    # reward_per_year = 2343173790311650 * 365 * 24 * 360 * 8739 = 64576253808343275086160000
    # current_apr: uint256 = reward_per_year/_tvl
    # current_apr =  64576253808343275086160000 / 3971570000 =  16259628763522556
    # retuen value is 162596287635225553
    assert pytest.approx(current_apr, rel=1000) == 16259628763522556
    print(current_apr/10**18)


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


def test_reward_manager_current_apr_pips(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    current_apr = reward_manager.current_apr_pips(recovery_gauge, 397157 * 10000, int(0.8739 * 10000), sender=bob)
    print(current_apr)
    

def test_reward_manager_calc_optimal_apr_record(bob, recovery_gauge, reward_manager):
    # precison in pips, a pip is 1/10000, 2000 pips is 20%
    new_apr = reward_manager.set_optimal_receiver_data(recovery_gauge, 397157 * 10000, int(0.8739 * 10000) , int(0.2 * 10000), sender=bob)

    assert reward_manager.reward_receivers_data(recovery_gauge).tvl == 3971570000
    print(reward_manager.reward_receivers_data(recovery_gauge).tvl)

    assert reward_manager.reward_receivers_data(recovery_gauge).token_price == 8739
    print(reward_manager.reward_receivers_data(recovery_gauge).token_price)

    assert reward_manager.reward_receivers_data(recovery_gauge).target_apr == 2000
    print(reward_manager.reward_receivers_data(recovery_gauge).target_apr)

    assert reward_manager.reward_receivers_data(recovery_gauge).token_amount == 1743153500000000000000
    print(reward_manager.reward_receivers_data(recovery_gauge).token_amount / 10**18)
