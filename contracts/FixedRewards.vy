# @version 0.3.10
"""
@title Secure Epoch Distribution with RewardManager
@author Assistant
@notice Distributes rewards through RewardManager based on hardcoded epochs
"""

interface RewardManager:
    def send_reward_token(_reward_receiver: address, _amount: uint256): nonpayable

# State Variables
owner: public(address)
reward_manager_address: public(address)
reward_receiver_address: public(address)
is_setup_complete: bool

reward_epochs: public(DynArray[uint256, 52])  # Storing reward amounts
last_reward_distribution_time: public(uint256)
have_rewards_started: public(bool)

SECONDS_PER_WEEK: constant(uint256) = 7 * 24 * 60 * 60  # 1 week in seconds
MIN_SECONDS_BETWEEN_DISTRIBUTIONS: constant(uint256) = SECONDS_PER_WEEK

# Events

event SetupCompleted:
    reward_manager_address: indexed(address)
    reward_receiver_address: indexed(address)
    setup_timestamp: uint256

event RewardDistributed:
    reward_amount: uint256
    remaining_reward_epochs: uint256
    distribution_timestamp: uint256

@external
def __init__():
    """
    @notice Initialize the contract with hardcoded reward epoch amounts in reverse order
    """
    self.owner = msg.sender
    
    # Initialize with hardcoded reward epoch amounts in reverse order
    # Last epoch to be distributed
    self.reward_epochs.append(2 * 10**18)  # Epoch 3
    self.reward_epochs.append(1 * 10**18)  # Epoch 2
    self.reward_epochs.append(5 * 10**18)  # Epoch 1 - First epoch to be distributed
    self.have_rewards_started = False
    self.is_setup_complete = False
    
@external
def setup(_reward_manager_address: address, _reward_receiver_address: address) -> bool:
    """
    @notice Set the reward manager and receiver addresses (can only be set once)
    @param _reward_manager_address Address of the RewardManager contract
    @param _reward_receiver_address Address of the RewardReceiver contract
    @return bool Setup success
    """
    assert msg.sender == self.owner, "Only owner can setup"
    assert not self.is_setup_complete, "Setup already completed"
    
    self.reward_manager_address = _reward_manager_address
    self.reward_receiver_address = _reward_receiver_address
    self.is_setup_complete = True
    
    log SetupCompleted(_reward_manager_address, _reward_receiver_address, block.timestamp)
    return True

@external
def distribute_reward() -> bool:
    """
    @notice Distribute rewards for the current epoch if conditions are met
    @return bool Distribution success
    """
    assert self.is_setup_complete, "Setup not completed"
    assert len(self.reward_epochs) > 0, "No remaining reward epochs"
    
    # If this is the first distribution, set the start time
    if not self.have_rewards_started:
        self.last_reward_distribution_time = block.timestamp
        self.have_rewards_started = True
    else:
        # Check if minimum time has passed since last distribution
        assert block.timestamp >= self.last_reward_distribution_time + MIN_SECONDS_BETWEEN_DISTRIBUTIONS, "Minimum time between distributions not met"
    
    # Get the reward amount for the current epoch (last in array)  
    current_reward_amount: uint256 = self.reward_epochs.pop()
    
    # Update last distribution time before external call
    self.last_reward_distribution_time = block.timestamp
    
    # Call reward manager to send reward
    RewardManager(self.reward_manager_address).send_reward_token(self.reward_receiver_address, current_reward_amount)
    
    log RewardDistributed(
        current_reward_amount,
        len(self.reward_epochs),  # Remaining reward epochs
        block.timestamp
    )
    
    return True

@external
@view
def get_next_epoch_info() -> (uint256, uint256):
    """
    @notice Get information about the next epoch to be distributed
    @return tuple(
        next_reward_amount: Amount for next epoch,
        seconds_until_next_distribution: Seconds left until next distribution is allowed
    )
    """
    assert len(self.reward_epochs) > 0, "No remaining reward epochs"
    
    seconds_until_next_distribution: uint256 = 0
    if self.have_rewards_started:
        if block.timestamp < self.last_reward_distribution_time + MIN_SECONDS_BETWEEN_DISTRIBUTIONS:
            seconds_until_next_distribution = self.last_reward_distribution_time + MIN_SECONDS_BETWEEN_DISTRIBUTIONS - block.timestamp
    
    return (
        self.reward_epochs[len(self.reward_epochs) - 1],  # Next reward amount to distribute (last element)
        seconds_until_next_distribution
    )

@external
@view
def get_remaining_epochs() -> uint256:
    """
    @notice Get the number of remaining reward epochs
    @return uint256 Remaining number of reward epochs
    """
    return len(self.reward_epochs)