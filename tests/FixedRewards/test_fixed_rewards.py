import ape
import pytest

DAY = 86400
SECONDS_PER_WEEK = 604800

def test_initial_state(fixed_rewards):
    assert not fixed_rewards.is_setup_complete()
    assert not fixed_rewards.is_reward_epochs_set()
    assert fixed_rewards.get_remaining_epochs() == 0

def test_managers(bob, charlie, fixed_rewards):
    assert fixed_rewards.managers(0) == bob
    assert fixed_rewards.managers(1) == charlie

def test_set_reward_manager(bob, reward_manager, recovery_gauge, fixed_rewards):
    # Setup the reward manager and receiver using manager account
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=bob)

    assert fixed_rewards.reward_manager_address() == reward_manager.address
    assert fixed_rewards.reward_receiver_address() == recovery_gauge.address

def test_set_reward_manager_revert_not_manager(alice, reward_manager, recovery_gauge, fixed_rewards):
    with ape.reverts("only managers can call this function"):
        fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

def test_set_reward_manager_revert_already_set(bob, reward_manager, recovery_gauge, fixed_rewards):
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=bob)

    with ape.reverts("Setup already completed"):
        fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=bob)
        
def test_set_reward_epochs(charlie, fixed_rewards):
    new_epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    
    # Set new reward epochs using manager account
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    
    assert fixed_rewards.get_remaining_epochs() == len(new_epochs)
    assert fixed_rewards.is_reward_epochs_set()
    #assert fixed_rewards.reward_epochs() == new_epochs

    get_all_epochs = fixed_rewards.get_all_epochs()
    print(get_all_epochs)

def test_set_reward_epochs_revert_not_manager(alice, fixed_rewards):
    new_epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    
    with ape.reverts("only managers can call this function"):
        fixed_rewards.set_reward_epochs(new_epochs, sender=alice)

def test_set_reward_epochs_revert_invalid_length(charlie, fixed_rewards):
    # Try to set 0 epochs
    with ape.reverts("Must set between 1 and 52 epochs"):
        fixed_rewards.set_reward_epochs([], sender=charlie)
    
    # Try to set more than 52 epochs
    #new_epochs = [1 * 10**18] * 53
    #with ape.reverts("Must set between 1 and 52 epochs"):
    #    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

def test_distribution_after_set_epochs(alice, bob, charlie, reward_manager, fixed_rewards, reward_token, recovery_gauge, chain):
    new_epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    
    # Set new reward epochs
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    
    # Setup the reward manager and receiver addresses
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)

    # First distribution - should be 3 tokens
    fixed_rewards.distribute_reward(sender=bob)

    assert fixed_rewards.get_number_of_remaining_epochs() == 2
    assert reward_token.balanceOf(recovery_gauge) == 3 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    
    # Second distribution - should be 2 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 1
    assert reward_token.balanceOf(recovery_gauge) == 5 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    
    # Third distribution - should be 1 token
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 0
    assert reward_token.balanceOf(recovery_gauge) == 6 * 10**18

def test_set_reward_manager_revert_not_owner(alice, reward_manager, recovery_gauge, fixed_rewards):
    with ape.reverts("only managers can call this function"):
        fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=alice)

def test_distribution_order(alice, bob, charlie, reward_manager, fixed_rewards, reward_token, recovery_gauge, chain):
    # Setup the reward manager and receiver
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)

    # First distribution - should be 5 tokens
    fixed_rewards.distribute_reward(sender=bob)

    assert fixed_rewards.get_number_of_remaining_epochs() == 2
    assert reward_token.balanceOf(recovery_gauge) == 5 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    
    # Second distribution - should be 1 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 1
    assert reward_token.balanceOf(recovery_gauge) == 6 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
    chain.mine()
    
    # Third distribution - should be 2 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 0
    assert reward_token.balanceOf(recovery_gauge) == 8 * 10**18


def test_distribution_timing(alice, bob, charlie, reward_manager, fixed_rewards, recovery_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)

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
        
    # Move time forward less than a week
    chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK + 10000
    chain.mine()

    # Should succeed now
    fixed_rewards.distribute_reward(sender=bob)

def test_distribute_revert_no_reward_manager(bob, fixed_rewards):
    with ape.reverts("Setup not completed"):
        fixed_rewards.distribute_reward(sender=bob)

def test_distribute_revert_no_epochs(alice, bob, charlie, reward_manager, fixed_rewards, recovery_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)

    # Distribute all epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
            chain.mine()
        fixed_rewards.distribute_reward(sender=bob)
    
    # Try to distribute when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        fixed_rewards.distribute_reward(sender=bob)

def test_get_next_epoch_info(alice, bob, charlie, reward_manager, fixed_rewards, recovery_gauge):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)

    # Check initial next epoch
    amount, time_until = fixed_rewards.get_next_epoch_info()
    assert amount == 5 * 10**18  # First epoch amount
    assert time_until == 0  # No time restriction for first distribution
    
    # Distribute first epoch
    fixed_rewards.distribute_reward(sender=bob)
    
    # Check second epoch info
    amount, time_until = fixed_rewards.get_next_epoch_info()
    assert amount == 1 * 10**18  # Second epoch amount
    assert time_until > 0  # Should have time restriction now

def test_get_next_epoch_info_revert_no_epochs(alice, bob, charlie, reward_manager, fixed_rewards, recovery_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)
    
    # Distribute all epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + SECONDS_PER_WEEK
            chain.mine()
        fixed_rewards.distribute_reward(sender=bob)
    
    # Try to get next epoch info when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        fixed_rewards.get_next_epoch_info()

def test_remaining_epochs_count(alice, bob, charlie, reward_manager, fixed_rewards, recovery_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    assert fixed_rewards.get_remaining_epochs() == 3
    
    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, recovery_gauge.address, sender=charlie)

    # Distribute epochs and check count
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