# @version 0.3.10
"""
@title RewardManager
@author martinkrung for curve.fi
@license MIT
@notice reward manager contract who can deposit a fixed reward token to allowed gauges
"""

from vyper.interfaces import ERC20

interface Gauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256): nonpayable

manager: public(address)
reward_token: public(address)
reward_receivers: public(DynArray[address, 10])

# set epoch length for newer gauges
@external
def __init__(_manager: address, _reward_token: address, _reward_receivers: DynArray[address, 10]):
    """
    @notice Contract constructor
    @param _reward_receivers allowed gauges to receiver reward
    """
    self.manager = _manager
    self.reward_token = _reward_token
    self.reward_receivers = _reward_receivers

@external
def deposit_reward_token(_reward_receiver: address, _amount: uint256):
    
    assert msg.sender == self.manager, 'dev: only reward manager can call this function'

    assert _reward_receiver in self.reward_receivers
    # deposit reward token from sender to this contract
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount)

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)

    Gauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)

