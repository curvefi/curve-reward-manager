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
recovery_address: public(address)


@external
def __init__(_managers: DynArray[address, 3], _reward_token: address, _reward_receivers: DynArray[address, 20], _recovery_address: address):
    """
    @notice Contract constructor
    @param _managers set managers who can deposit reward token
    @param _reward_token set reward token address
    @param _reward_receivers allowed gauges to receiver reward
    @param _recovery_address set recovery address
    """
    self.managers = _managers
    self.reward_token = _reward_token
    self.reward_receivers = _reward_receivers
    self.recovery_address = _recovery_address

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

    assert 3 * WEEK / 7 <= _epoch and _epoch <= WEEK * 4 * 12, 'dev: epoch duration must be between 3 days and a year'

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)
    # legacy gauges have no epoch parameter 
    # new deposit_reward_token has epoch parameter default to WEEK
    if _epoch == WEEK:
        LegacyGauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)
    else:
        Gauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount, _epoch)


@external
def deposit_send_reward_token(_reward_receiver: address, _amount: uint256, _epoch: uint256 = WEEK):
    """
    @notice deposit reward token from sender to contract and then forwarded to gauge
    @param _reward_receiver gauges to receiver reward
    @param _amount amount of reward token to deposit
    @param _epoch The duration the rewards are distributed across in seconds. Between 3 days and a year, week by default
    """
   
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    assert 3 * WEEK / 7 <= _epoch and _epoch <= WEEK * 4 * 12, 'dev: epoch duration must be between 3 days and a year'

    # deposit reward token from sender to this contract
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount)

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)

    # legacy gauges have no epoch parameter
    # new deposit_reward_token has epoch parameter default to WEEK
    if _epoch == WEEK:
        LegacyGauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)
    else:
        Gauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount, _epoch)

@external
def recover_lost_token(_lost_token: address, _amount: uint256):
    """
    @notice recover wrong token from contract to recovery address
    @param _lost_token address of the token to recover
    @param _amount amount of the token to recover
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _lost_token != self.reward_token, 'dev: cannot recover reward token'
    assert _amount > 0, 'dev: amount must be greater than 0'

    assert ERC20(_lost_token).transfer(self.recovery_address, _amount)
