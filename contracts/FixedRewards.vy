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
reward_manager: public(address)
reward_receiver: public(address)
setup_complete: bool

epochs: public(DynArray[uint256, 52])  # Just storing amounts now
last_distribution_time: public(uint256)
is_started: public(bool)

WEEK: constant(uint256) = 7 * 24 * 60 * 60  # 1 week in seconds
MIN_TIME_BETWEEN_DISTRIBUTIONS: constant(uint256) = WEEK

# Events

event SetupDone:
    reward_manager: indexed(address)
    reward_receiver: indexed(address)
    timestamp: uint256

event RewardDistributed:
    amount: uint256
    remaining_epochs: uint256
    timestamp: uint256

@external
def __init__():
    """
    @notice Initialize the contract with hardcoded epoch amounts in reverse order
    """
    self.owner = msg.sender
    
    # Initialize with hardcoded epoch amounts in reverse order
    # Last to be distributed
    self.epochs.append(2 * 10**18)  # Epoch 3
    self.epochs.append(1 * 10**18)  # Epoch 2
    self.epochs.append(5 * 10**18)  # Epoch 1 - First to be distributed
    self.is_started = False
    self.setup_complete = False
    
@external
def setup(_reward_manager: address, _reward_receiver: address) -> bool:
    """
    @notice Set the reward manager address (can only be set once)
    @param _reward_manager Address of the RewardManager contract
    @param _reward_receiver Address of the RewardReceiver contract
    @return bool Success
    """
    assert msg.sender == self.owner, "Only owner"
    assert not self.setup_complete, "Already set"
    
    self.reward_manager = _reward_manager
    self.reward_receiver = _reward_receiver
    self.setup_complete = True
    
    log SetupDone(_reward_manager, _reward_receiver, block.timestamp)
    return True

@external
def distribute_reward() -> bool:
    """
    @notice Distribute rewards for the current epoch if conditions are met
    @return bool Success of distribution
    """
    assert self.setup_complete, "Setup not done"
    assert len(self.epochs) > 0, "No more epochs"
    
    # If this is the first distribution, set the start time
    if not self.is_started:
        self.last_distribution_time = block.timestamp
        self.is_started = True
    else:
        # Check if minimum time has passed since last distribution
        assert block.timestamp >= self.last_distribution_time + MIN_TIME_BETWEEN_DISTRIBUTIONS, "Minimum time not passed"
    
    # Remove the distributed epoch (last element)
    # Get the amount for current epoch (last in array)
    amount: uint256 = self.epochs.pop()
    
    # Update the last distribution time before external call
    self.last_distribution_time = block.timestamp
    
    # Call reward manager to send reward
    RewardManager(self.reward_manager).send_reward_token(self.reward_receiver, amount)
    
    log RewardDistributed(
        amount,
        len(self.epochs),  # Remaining epochs
        block.timestamp
    )
    
    return True

@external
@view
def get_next_epoch_info() -> (uint256, uint256):
    """
    @notice Get information about the next epoch to be distributed
    @return tuple(
        amount: Amount for next epoch,
        time_until_distribution: Seconds left until distribution allowed
    )
    """
    assert len(self.epochs) > 0, "No more epochs"
    
    time_until_distribution: uint256 = 0
    if self.is_started:
        if block.timestamp < self.last_distribution_time + MIN_TIME_BETWEEN_DISTRIBUTIONS:
            time_until_distribution = self.last_distribution_time + MIN_TIME_BETWEEN_DISTRIBUTIONS - block.timestamp
    
    return (
        self.epochs[len(self.epochs) - 1],  # Next amount to distribute (last element)
        time_until_distribution
    )

@external
@view
def get_remaining_epochs() -> uint256:
    """
    @notice Get number of remaining epochs
    @return uint256 Number of remaining epochs
    """
    return len(self.epochs)