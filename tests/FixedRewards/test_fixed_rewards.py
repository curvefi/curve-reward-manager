import ape
import pytest

DAY = 86400
WEEK = 604800

def test_initial_state(fixed_rewards):
    assert not fixed_rewards.is_setup_complete()
    assert not fixed_rewards.is_reward_epochs_set()
    assert fixed_rewards.get_number_of_remaining_epochs() == 0

def test_managers(bob, charlie, fixed_rewards):
    assert fixed_rewards.managers(0) == bob
    assert fixed_rewards.managers(1) == charlie

def test_set_reward_manager(bob, reward_manager, test_gauge, fixed_rewards):
    # Setup the reward manager and receiver using manager account with default epoch duration (3 days)
    min_epoch_duration = 3 * DAY
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=bob)

    assert fixed_rewards.reward_manager_address() == reward_manager.address
    print(fixed_rewards.reward_manager_address())
    assert fixed_rewards.receiving_gauge() == test_gauge.address
    assert fixed_rewards.min_epoch_duration() == min_epoch_duration

def test_set_reward_manager_revert_not_manager(alice, reward_manager, test_gauge, fixed_rewards):
    min_epoch_duration = 3 * DAY
    with ape.reverts("only managers can call this function"):
        fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=alice)

def test_set_reward_manager_revert_already_set(bob, reward_manager, test_gauge, fixed_rewards):
    min_epoch_duration = 3 * DAY
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=bob)

    with ape.reverts("Setup already completed"):
        fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=bob)
        
def test_set_reward_epochs(charlie, fixed_rewards):
    new_epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    
    # Set new reward epochs using manager account
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    
    assert fixed_rewards.get_number_of_remaining_epochs() == len(new_epochs)
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

def test_distribution_after_set_epochs(alice, bob, charlie, reward_manager, fixed_rewards, reward_token, test_gauge, chain):
    new_epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Set new reward epochs
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    
    # Setup the reward manager and receiver addresses with 3 day epoch duration
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)

    # First distribution - should be 3 tokens
    fixed_rewards.distribute_reward(sender=bob)

    assert fixed_rewards.get_number_of_remaining_epochs() == 2
    assert reward_token.balanceOf(test_gauge) == 3 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Second distribution - should be 2 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 1
    assert reward_token.balanceOf(test_gauge) == 5 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Third distribution - should be 1 token
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 0
    assert reward_token.balanceOf(test_gauge) == 6 * 10**18

def test_set_reward_manager_revert_not_owner(alice, reward_manager, test_gauge, fixed_rewards):
    with ape.reverts("only managers can call this function"):
        fixed_rewards.setup(reward_manager.address, test_gauge.address, 3 * DAY, sender=alice)

def test_distribution_order(alice, bob, charlie, reward_manager, fixed_rewards, reward_token, test_gauge, chain):
    # Setup the reward manager and receiver
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)

    # First distribution - should be 5 tokens
    fixed_rewards.distribute_reward(sender=bob)

    assert fixed_rewards.get_number_of_remaining_epochs() == 2
    assert reward_token.balanceOf(test_gauge) == 5 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Second distribution - should be 1 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 1
    assert reward_token.balanceOf(test_gauge) == 6 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Third distribution - should be 2 tokens
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 0
    assert reward_token.balanceOf(test_gauge) == 8 * 10**18


def test_distribution_timing(alice, bob, charlie, reward_manager, fixed_rewards, test_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)

    # First distribution can happen immediately
    fixed_rewards.distribute_reward(sender=bob)
    
    # Try to distribute again immediately - should fail
    with ape.reverts("Minimum time between distributions not met"):
        fixed_rewards.distribute_reward(sender=bob)
    
    # Move time forward less than a week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration - 1000
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
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration + 10000
    chain.mine()

    # Should succeed now
    fixed_rewards.distribute_reward(sender=bob)

def test_distribute_revert_no_reward_manager(bob, fixed_rewards):
    with ape.reverts("Setup not completed"):
        fixed_rewards.distribute_reward(sender=bob)

def test_distribute_revert_no_epochs(alice, bob, charlie, reward_manager, fixed_rewards, test_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)

    # Distribute all epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
            chain.mine()
        fixed_rewards.distribute_reward(sender=bob)
    
    # Try to distribute when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        fixed_rewards.distribute_reward(sender=bob)

def test_get_next_epoch_info(alice, bob, charlie, reward_manager, fixed_rewards, test_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)

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

def test_get_next_epoch_info_revert_no_epochs(alice, bob, charlie, reward_manager, fixed_rewards, test_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    min_epoch_duration = 3 * DAY

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)
    
    # Distribute all epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
            chain.mine()
        fixed_rewards.distribute_reward(sender=bob)
    
    # Try to get next epoch info when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        fixed_rewards.get_next_epoch_info()

def test_remaining_epochs_count(alice, bob, charlie, reward_manager, fixed_rewards, test_gauge, chain):
    new_epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 4 * DAY
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)

    # Setup the reward manager and receiver
    fixed_rewards.setup(reward_manager.address, test_gauge.address, min_epoch_duration, sender=charlie)

    # Distribute epochs and check count
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 2
    
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 1
    
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    fixed_rewards.distribute_reward(sender=bob)
    assert fixed_rewards.get_number_of_remaining_epochs() == 0

def test_min_epoch_duration_default(fixed_rewards):
    """Test that min_epoch_duration is initialized to WEEK"""
    assert fixed_rewards.min_epoch_duration() == WEEK

def test_setup_with_custom_epoch_duration(bob, reward_manager, test_gauge, fixed_rewards):
    """Test setting a custom min_epoch_duration during setup"""
    custom_duration = 4 * DAY  # 4 days
    fixed_rewards.setup(reward_manager.address, test_gauge.address, custom_duration, sender=bob)
    
    assert fixed_rewards.min_epoch_duration() == custom_duration
    assert fixed_rewards.is_setup_complete()

def test_setup_revert_epoch_too_short(bob, reward_manager, test_gauge, fixed_rewards):
    """Test that setting too short epoch duration reverts"""
    too_short = 2 * DAY  # 2 days (minimum is 3 days)
    
    with ape.reverts("epoch duration must be between 3 days and a year"):
        fixed_rewards.setup(reward_manager.address, test_gauge.address, too_short, sender=bob)

def test_setup_revert_epoch_too_long(bob, reward_manager, test_gauge, fixed_rewards):
    """Test that setting too long epoch duration reverts"""
    too_long = 53 * WEEK  # More than a year
    
    with ape.reverts("epoch duration must be between 3 days and a year"):
        fixed_rewards.setup(reward_manager.address, test_gauge.address, too_long, sender=bob)

def test_distribution_respects_min_epoch_duration(bob, charlie, reward_manager, fixed_rewards, test_gauge, chain):
    """Test that distribution timing respects custom min_epoch_duration"""
    # Setup with 4-day minimum duration
    custom_duration = 4 * DAY
    new_epochs = [1 * 10**18, 2 * 10**18]
    
    fixed_rewards.set_reward_epochs(new_epochs, sender=charlie)
    fixed_rewards.setup(reward_manager.address, test_gauge.address, custom_duration, sender=bob)
    
    # First distribution should work
    fixed_rewards.distribute_reward(sender=bob)
    
    # Try to distribute before minimum duration - should fail
    chain.pending_timestamp = chain.pending_timestamp + custom_duration - 1000
    chain.mine()
    
    with ape.reverts("Minimum time between distributions not met"):
        fixed_rewards.distribute_reward(sender=bob)
    
    # Move past minimum duration - should succeed
    chain.pending_timestamp = chain.pending_timestamp + 2000  # Move past min duration
    chain.mine()
    
    fixed_rewards.distribute_reward(sender=bob)