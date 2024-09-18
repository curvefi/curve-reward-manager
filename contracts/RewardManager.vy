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
    def totalSupply() -> uint256: view

struct Reward:
    distributor: address
    period_finish: uint256
    rate: uint256
    last_update: uint256
    integral: uint256

interface Chainlink:
    # def latestRoundData() -> uint256: view
    def latestAnswer() -> uint256: view

interface RewardManager:
    def current_apr_tvl_price(_reward_receiver: address, _tvl: uint256, _token_price: uint256) -> uint256: view
    def current_apr_tvl(_reward_receiver: address, _token_price: uint256) -> uint256: view
    def current_apr(_reward_receiver: address) -> uint256: view
    def calculate_reward_token_amount(_reward_receiver: address, _target_apr: uint256) -> uint256: view
    def token_price() -> uint256: view
    def crvUSDTVLinGauge(_reward_receiver: address) -> uint256: view

managers: public(DynArray[address, 3])
reward_token: public(address)
reward_receivers: public(DynArray[address, 20])

apr: public(uint256)

SECONDS_PER_YEAR: constant(uint256) = 365 * 24 * 3600
PRECISION: constant(uint256) = 10000

struct RewardRecieverData:
    tvl: uint256
    token_price: uint256
    target_apr: uint256
    token_amount: uint256

reward_receivers_data: public(HashMap[address, RewardRecieverData])


# set epoch length for newer gauges
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
def current_apr_tvl_price(_reward_receiver: address, _tvl: uint256, _token_price: uint256) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receive reward
    @param _tvl value of pool in $, with 4 decimal places, 1 is 10000
    @param _token_price price of token in $, with 4 decimal places, 1 is 10000
    """
    assert _tvl > 1000 * 10000, 'dev: tvl needs to be > $1000'
    assert _token_price > 1, 'dev: tvl needs to be > $0.0001'
    
    reward_data: Reward = Gauge(_reward_receiver).reward_data(self.reward_token)

    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    # rate is per second
    reward_per_year: uint256 = reward_data.rate * 365 * 24 * 3600 * _token_price 
    # apr as 10**18
    current_apr: uint256 = reward_per_year/_tvl

    return current_apr


@view
@external
def current_apr_tvl(_reward_receiver: address, _token_price: uint256) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receive reward
    @param _token_price price of token in $, with 4 decimal places, 1 is 10000
    """
    assert _token_price > 1, 'dev: tvl needs to be > $0.0001'
    
    reward_data: Reward = Gauge(_reward_receiver).reward_data(self.reward_token)
    tvl: uint256 = Gauge(_reward_receiver).totalSupply()
    # totalSupply is 10**21
    # tvl is 10**4
    tvl = tvl / 10**17
    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    # rate is per second
    reward_per_year: uint256 = reward_data.rate * 365 * 24 * 3600 * _token_price 
    # apr as 10**18
    current_apr: uint256 = reward_per_year/tvl

    return current_apr


@view
@external
def current_apr(_reward_receiver: address) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receive reward
    @return current apr as 10**18
    """
    
    reward_data: Reward = Gauge(_reward_receiver).reward_data(self.reward_token)
    tvl: uint256 = RewardManager(self).crvUSDTVLinGauge(_reward_receiver)
    token_price: uint256 = RewardManager(self).token_price()

    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    # rate is per second
    reward_per_year: uint256 = reward_data.rate * 365 * 24 * 3600 * token_price 
    # apr as 10**18
    current_apr: uint256 = reward_per_year/tvl
    return current_apr


@view
@external
def current_apr_in_pips(_reward_receiver: address) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _reward_receiver gauges to receive reward
    @return current apr in pips, 1 pip is 1/10000
    """
    current_apr: uint256 = RewardManager(self).current_apr(_reward_receiver)
    return current_apr/10 ** 14 


@external
def setCalcStorage(_reward_receiver: address, _target_apr: uint256):
    """
    @notice set storage for calculate_reward_token_amount, this is done to avoid front-running
    @param _reward_receiver gauges to receive reward
    @param _target_apr target apr in pips, 1 pip is 1/10000
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    self.reward_receivers_data[_reward_receiver]  = RewardRecieverData({
        tvl: RewardManager(self).crvUSDTVLinGauge(_reward_receiver),
        token_price: RewardManager(self).token_price(),
        target_apr: _target_apr,
        token_amount: 0
    })


@external
def setMockCalcStorage(_reward_receiver: address):
    """
    @notice set storage for calculate_reward_token_amount, used for testing
    @param _reward_receiver gauges to receive reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    self.reward_receivers_data[_reward_receiver]  = RewardRecieverData({
        tvl: 397157 * 10000,
        token_price: 8739,
        target_apr: 10000,
        token_amount: 0
    })


@view
@external
def calculate_reward_token_amount(_reward_receiver: address, _target_apr: uint256) -> uint256:
    """
    @notice Calculate the amount of reward tokens needed to achieve the target APR
    @param _reward_receiver Address of the gauge to receive the reward
    @param _target_apr Target APR in pips (1 pip = 1/10000 = 0.0001 = 0.01%)
    @return Amount of reward tokens needed (in token's smallest unit, e.g., wei for 18 decimal tokens)
    """
    assert self.reward_receivers_data[_reward_receiver].tvl > 1000 * 10000, 'dev: tvl needs to be > $1000'
    assert self.reward_receivers_data[_reward_receiver].token_price > 1, 'dev: token price needs to be > $0.0001'
    assert _target_apr > 50, 'dev: target apr needs to be > 0.5%'

    tvl: uint256 = self.reward_receivers_data[_reward_receiver].tvl
    reward_duration: uint256 = 7 * 24 * 3600  # 1 week in seconds

    # Calculate reward amount in USD (with 4 decimal places)
    reward_usd: uint256 = (_target_apr * tvl * reward_duration) / (SECONDS_PER_YEAR * PRECISION * PRECISION)

    # Calculate token amount (assuming 18 decimal places for the token)
    token_amount: uint256 = reward_usd * 10**18 / self.reward_receivers_data[_reward_receiver].token_price

    return token_amount


@view
@external
def token_price() -> uint256:
    """
    @notice get token price from chainlink as 5 decimals
    # todo: integrate decimals from chainlink
    # give fixed price for mock token is dangerouos
    """
    # assert self.reward_token == 0x912CE59144191C1204E64559FE8253a0e49E6548, 'dev: only ARB is supported'
    if self.reward_token == 0x912CE59144191C1204E64559FE8253a0e49E6548:
        price_feed: address = 0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6
        # latestRoundData: uint256 = Chainlink(price_feed).latestRoundData()
        latestAnswer: uint256 = Chainlink(price_feed).latestAnswer()
        latestAnswer = latestAnswer / 10 ** 4
        return latestAnswer
    else:
        return 8739 # mock token price to $0.8739



@view
@external
def crvUSDTVLinGauge(_reward_receiver: address) -> uint256:
    """
    @notice TVL of gauge as crvUSD with 4 decimal places, 1 is 10000
    @param _reward_receiver gauges
    """
    tvl: uint256 = Gauge(_reward_receiver).totalSupply()
    # totalSupply is 10**21
    # tvl is 10**4
    tvl = tvl / 10**17
    return tvl


@external
def set_optimal_receiver_data(_reward_receiver: address, _tvl: uint256, _token_price: uint256, _target_apr: uint256):
    """
    @notice set optimal receiver data
    @param _reward_receiver gauges to receiver reward
    @param _tvl value of pool in $, with 4 decimal places, 1 is 10000
    @param _token_price price of token in $, with 4 decimal places, 1 is 10000
    @param _target_apr target apr in pips, 1 pip is 1/10000
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    self.reward_receivers_data[_reward_receiver] = RewardRecieverData({
        tvl: _tvl,
        token_price: _token_price,
        target_apr: _target_apr,
        token_amount: RewardManager(self).calculate_reward_token_amount(_reward_receiver, _target_apr)
    })


@external
def setTokenAmount(_reward_receiver: address):
    """
    @notice set optimal receiver data
    @param _reward_receiver gauges to receive reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'

    assert _reward_receiver in self.reward_receivers, 'dev: only reward receiver which are allowed'

    target_apr: uint256 = self.reward_receivers_data[_reward_receiver].target_apr

    new_token_amount: uint256 = RewardManager(self).calculate_reward_token_amount(_reward_receiver, target_apr)

    self.reward_receivers_data[_reward_receiver].token_amount = new_token_amount
    

@external
def kill():
    """
    @notice  kill contract if no balance
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert ERC20(self.reward_token).balanceOf(self) > 0, 'dev: no balance to recover'
    selfdestruct(msg.sender)