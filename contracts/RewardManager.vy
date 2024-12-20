# @version 0.3.10
"""
@title RewardManager
@author martinkrung for curve.fi
@license MIT
@notice reward manager contract who can deposit a fixed reward token to allowed gauges
"""

from vyper.interfaces import ERC20

interface LegacyGauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256): nonpayable

interface Gauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256, _epoch: uint256): nonpayable

WEEK: constant(uint256) = 604800

VERSION: constant(String[8]) = "1.0.0"

managers: public(DynArray[address, 3])
reward_token: public(address)
reward_receivers: public(DynArray[address, 20])

@external
def __init__(_managers: DynArray[address, 3], _reward_token: address, _reward_receivers: DynArray[address, 20]):
    """
    @notice Contract constructor
    @param _managers set managers who can deposit reward token
    @param _reward_token set reward token address
    @param _reward_receivers allowed gauges to receiver reward
    """
    self.managers = _managers
    self.reward_token = _reward_token
    self.reward_receivers = _reward_receivers

@external
def send_reward_token(_reward_receiver: address, _amount: uint256, _epoch: uint256 = WEEK):
    """
    @notice send reward token from contract to gauge
    @param _reward_receiver gauges to receiver reward
    @param _amount The amount of reward token being sent
    @param _epoch The duration the rewards are distributed across in seconds. Between 3 days and a year, week by default
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    assert 3 * WEEK / 7 <= _epoch and _epoch <= WEEK * 4 * 12, "Epoch duration"

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)
    # legacy gauges have no epoch parameter, 
    # new deposit_reward_token has epoch parameter default to WEEK
    if _epoch == WEEK:
        LegacyGauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)
    else:
        Gauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount, _epoch)


@external
def deposit_send_reward_token(_reward_receiver: address, _amount: uint256):
    """
    @notice deposit reward token from sender to contract, then send to gauge
    @param _reward_receiver gauges to receiver reward
    @param _amount amount of reward token to deposit
    """
    
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    # deposit reward token from sender to this contract
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount)

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)

    LegacyGauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)

