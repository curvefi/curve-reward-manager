import ape
import pytest

SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800

def test_initial_state(fixed_rewards):
    assert fixed_rewards.get_remaining_epochs() == 3
    assert not fixed_rewards.have_rewards_started()

def test_setup(alice, reward_manager, recovery_gauge, fixed_rewards):
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    assert fixed_rewards.reward_manager_address() == reward_manager.address
    assert fixed_rewards.reward_receiver_address() == recovery_gauge.address

def test_setup_revert_already_setup(alice, reward_manager, recovery_gauge, fixed_rewards):
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    with ape.reverts("Setup already completed"):
        fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)


def test_setup_revert_not_owner(bob, reward_manager, recovery_gauge, fixed_rewards):
    with ape.reverts("Only owner can setup"):
        fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=bob)

def test_distribution_order(alice, bob, reward_manager, fixed_rewards, reward_token, recovery_gauge, chain):
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    # First distribution - should be 5 tokens
    fixed_rewards.distribute_reward(sender=bob)

    assert fixed_rewards.get_remaining_epochs() == 2
    assert reward_token.balanceOf(recovery_gauge) == 5 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    
    # Second distribution - should be 1 token
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_remaining_epochs() == 1
    assert reward_token.balanceOf(recovery_gauge) == 6 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    
    # Third distribution - should be 2 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_remaining_epochs() == 0
    assert reward_token.balanceOf(recovery_gauge) == 8 * 10**18


def test_distribution_timing(alice, bob, reward_manager, fixed_rewards, recovery_gauge, chain):
    # Setup the reward manager and receiver addresses  
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    # First distribution can happen immediately
    fixed_rewards.distribute_reward(sender=bob)
    
    # Try to distribute again immediately - should fail
    with ape.reverts("Minimum time between distributions not met"):
        fixed_rewards.distribute_reward(sender=bob)
    
    # Move time forward less than a week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK - 1000
    chain.mine()
    
    # Should still fail
    with ape.reverts("Minimum time between distributions not met"):
        fixed_rewards.distribute_reward(sender=bob)
    
    # Move time to exactly one week  
    chain.pending_timestamp = chain.pending_timestamp + 1000
    chain.mine()
    
    # Should succeed now
    fixed_rewards.distribute_reward(sender=bob)
        
    # Move time forward more than a week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK + 10000
    chain.mine()

    # Should succeed now
    fixed_rewards.distribute_reward(sender=bob)

def test_distribute_revert_setup_not_done(bob, fixed_rewards):
    with ape.reverts("Setup not completed"):
        fixed_rewards.distribute_reward(sender=bob)

def test_distribute_revert_no_reward_epochs(alice, bob, reward_manager, fixed_rewards, recovery_gauge, chain):
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    # Distribute all reward epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
            chain.mine()
        fixed_rewards.distribute_reward(sender=bob)
    
    # Try to distribute when no reward epochs remain
    with ape.reverts("No remaining reward epochs"):
        fixed_rewards.distribute_reward(sender=bob)

def test_get_next_epoch_info(alice, bob, reward_manager, fixed_rewards, recovery_gauge):
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    # Check initial next epoch info
    next_reward_amount, seconds_until_next_distribution = fixed_rewards.get_next_epoch_info()
    assert next_reward_amount == 5 * 10**18  # First epoch reward amount 
    assert seconds_until_next_distribution == 0  # No time restriction for first distribution
    
    # Distribute first reward epoch
    fixed_rewards.distribute_reward(sender=bob)
    
    # Check second epoch info
    next_reward_amount, seconds_until_next_distribution = fixed_rewards.get_next_epoch_info()
    assert next_reward_amount == 1 * 10**18  # Second epoch reward amount
    assert seconds_until_next_distribution > 0  # Should have time restriction now

def test_get_next_epoch_info_revert_no_epochs(alice, bob, reward_manager, fixed_rewards, recovery_gauge, chain):
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)
    
    # Distribute all reward epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
            chain.mine()
        fixed_rewards.distribute_reward(sender=bob)
    
    # Try to get next epoch info when no reward epochs remain  
    with ape.reverts("No remaining reward epochs"):
        fixed_rewards.get_next_epoch_info()

def test_remaining_epochs_count(alice, bob, reward_manager, fixed_rewards, recovery_gauge, chain):
    assert fixed_rewards.get_remaining_epochs() == 3
    
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

    # Distribute reward epochs and check remaining count
    fixed_rewards.distribute_reward(sender=bob)  
    assert fixed_rewards.get_remaining_epochs() == 2
    
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_remaining_epochs() == 1
    
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK  
    chain.mine()
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_remaining_epochs() == 0