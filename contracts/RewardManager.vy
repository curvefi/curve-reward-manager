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
    def reward_data(_reward_token: address) -> Reward: view

struct Reward:
    distributor: address
    period_finish: uint256
    rate: uint256
    last_update: uint256
    integral: uint256

managers: public(DynArray[address, 3])
reward_token: public(address)
reward_receivers: public(DynArray[address, 10])

apr: public(uint256)

struct RewardRecieverData:
    tvl: uint256
    token_price: uint256
    target_apr: uint256
    token_amount: uint256

reward_receivers_data: public(HashMap[address, RewardRecieverData])

# set epoch length for newer gauges
@external
def __init__(_managers: DynArray[address, 3], _reward_token: address, _reward_receivers: DynArray[address, 10]):
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
def deposit_reward_token(_reward_receiver: address, _amount: uint256):
    
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    # deposit reward token from sender to this contract
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount)

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)

    Gauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)

@external
def deposit_reward_token_from_contract(_reward_receiver: address, _amount: uint256):
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receiver reward
    @param _amount amount of reward token to deposit
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    assert ERC20(self.reward_token).approve(_reward_receiver, _amount)

    Gauge(_reward_receiver).deposit_reward_token(self.reward_token, _amount)

@external
def deposit_reward_token_with_target_rate(_reward_receiver: address):
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receiver reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    assert self.reward_receivers_data[_reward_receiver].tvl > 0, 'dev: no tvl data'
    assert self.reward_receivers_data[_reward_receiver].token_price > 0, 'dev: no token_price data'
    assert self.reward_receivers_data[_reward_receiver].target_apr > 0, 'dev: no target_apr data'
    assert self.reward_receivers_data[_reward_receiver].token_amount > 0, 'dev: no token_amount data'

    token_amount: uint256 = self.reward_receivers_data[_reward_receiver].token_amount

    assert ERC20(self.reward_token).approve(_reward_receiver, token_amount)

    Gauge(_reward_receiver).deposit_reward_token(self.reward_token, token_amount)

    # reset data
    self.reward_receivers_data[_reward_receiver] = RewardRecieverData({
        tvl: 0,
        token_price: 0,
        target_apr: 0,
        token_amount: 0
    })

@view
@external
def calc_current_apr(_reward_receiver: address, tvl: uint256, token_price: uint256) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receiver reward
    @param tvl value of pool in $, with 5 digits 1 is 10000
    @param token_price price of token in $, with 5 digits, 1 is 10000
    """
    # tvl needs to be > $1000
    assert tvl > 1000 * 10000
    # token price needs to be > $0.0001
    assert token_price > 1
    
    reward_data: Reward = Gauge(_reward_receiver).reward_data(self.reward_token)

    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0

    reward_total: uint256 = reward_data.rate * reward_duration * token_price
    # apr as 10**18
    current_apr: uint256 = reward_total/tvl * (365 * 24 * 3600/reward_duration )

    return current_apr


@view
@internal
def calc_optimal_apr(_reward_receiver: address, tvl: uint256, token_price: uint256, _target_apr: uint256) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receiver reward
    @param tvl value of pool in $, with 5 digits 1 is 10000
    @param token_price price of token in $, with 5 digits, 1 is 10000
    @param _target_apr target apr in pips, 1 pip is 1/10000
    """
    # tvl needs to be > $1000
    assert tvl > 1000 * 10000
    # token price needs to be > $0.0001
    assert token_price > 1
    # token price needs to be > 0.5%
    assert _target_apr >  50

    reward_data: Reward = Gauge(_reward_receiver).reward_data(self.reward_token)

    # with fixed epoch length = 1 week
    reward_duration: uint256 = 7*24*3600

    # precison in pips, a pip is 1/10000
    # 2326 pips = 23.26%
    # in $
    #new_reward_total: uint256 = tvl * _target_apr / (365 * 24 * 3600 / reward_duration )

    new_reward_total: uint256 =   _target_apr * tvl * reward_duration / (365 * 24 * 3600)

    # self.apr = new_reward_total
    # 18 digits token and pip correction
    new_token_amount: uint256 = new_reward_total / token_price * 10 ** 18 / 10000

    return new_token_amount



@external
def set_optimal_receiver_data(_reward_receiver: address, tvl: uint256, token_price: uint256, _target_apr: uint256):

    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    self.reward_receivers_data[_reward_receiver] = RewardRecieverData({
        tvl: tvl,
        token_price: token_price,
        target_apr: _target_apr,
        token_amount: self.calc_optimal_apr(_reward_receiver, tvl, token_price, _target_apr)
    })
