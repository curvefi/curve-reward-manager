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


interface GaugeFactory:
    def gauge_data(_gauge: address)-> bool: view


interface RewardManager:
    def current_apr_tvl_price(_gauge: address, _tvl: uint256, _token_price: uint256) -> uint256: view
    def current_apr_tvl(_gauge: address, _token_price: uint256) -> uint256: view
    def current_apr(_gauge: address) -> uint256: view
    def calculate_reward_token_amount(_gauge: address, _target_apr: uint256) -> uint256: view
    def token_price() -> uint256: view
    def crvUSD_tvl_in_gauge(_gauge: address) -> uint256: view
    def set_gauge_data(_gauge: address, _target_apr: uint256): nonpayable
    def deposit_reward_token_from_contract(_gauge: address, _amount: uint256): nonpayable
    def deposit_reward_token_with_target_rate(_gauge: address): nonpayable
    def deposit_reward_token_with_target_rate_on_step(_gauge: address, _target_apr: uint256): nonpayable
    def reward_duration_in_h(_gauge: address)-> uint256: view
    def calculate_new_min_apr(_gauge: address)-> uint256: view

managers: public(DynArray[address, 3])
reward_token: public(address)
gauges: public(DynArray[address, 20])

SECONDS_PER_YEAR: constant(uint256) = 365 * 24 * 3600
PRECISION: constant(uint256) = 10**4
HIGH_PRECISION: constant(uint256) = 10**10
EPOCH: constant(uint256) = 7 * 24 * 3600

struct GaugeData:
    tvl: uint256
    token_price: uint256
    target_apr: uint256
    token_amount: uint256

gauge_data: public(HashMap[address, GaugeData])


# set epoch length for newer gauges
@external
def __init__(_managers: DynArray[address, 3], _reward_token: address, _gauges: DynArray[address, 20]):
    """
    @notice Contract constructor
    @param _managers set managers who can deposit reward token
    @param _reward_token set reward token address
    @param _gauges allowed gauges to receiver reward
    """
    self.managers = _managers
    self.reward_token = _reward_token
    self.gauges = _gauges

@external
@nonreentrant('lock')
def deposit_reward_token(_gauge: address, _amount: uint256):
    
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    # deposit reward token from sender to this contract
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount)

    assert ERC20(self.reward_token).approve(_gauge, _amount)

    Gauge(_gauge).deposit_reward_token(self.reward_token, _amount)

@external
@nonreentrant('lock')
def deposit_reward_token_from_contract(_gauge: address, _amount: uint256):
    """
    @notice forward reward token from contract to gauge
    @param _gauge gauges to receiver reward
    @param _amount amount of reward token to deposit
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    assert ERC20(self.reward_token).approve(_gauge, _amount)

    Gauge(_gauge).deposit_reward_token(self.reward_token, _amount)


@external
@nonreentrant('lock')
def deposit_reward_token_to_stretch(_gauge: address):
    """
    @notice forward 1 reward token from contract to gauge, to stretch the reward duration
    @param _gauge gauges to receiver reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    assert ERC20(self.reward_token).approve(_gauge, 1)

    Gauge(_gauge).deposit_reward_token(self.reward_token, 1)


@external
def deposit_reward_token_with_target_rate(_gauge: address):
    """
    @notice forward reward token from contract to gauge for a target apr if reward is not active
    @param _gauge gauge to receiver reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    assert self.gauge_data[_gauge].tvl > 0, 'dev: no tvl data'
    assert self.gauge_data[_gauge].token_price > 0, 'dev: no token_price data'
    assert self.gauge_data[_gauge].target_apr > 0, 'dev: no target_apr data'
    assert self.gauge_data[_gauge].token_amount > 0, 'dev: no token_amount data'

    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is inactive
    assert reward_duration == 0, 'dev: rewards needs to inactive'

    token_amount: uint256 = self.gauge_data[_gauge].token_amount

    RewardManager(self).deposit_reward_token_from_contract(self.reward_token, token_amount)

    # reset data
    self.gauge_data[_gauge] = GaugeData({
        tvl: 0,
        token_price: 0,
        target_apr: 0,
        token_amount: 0
    })

@external
def deposit_reward_token_with_target_rate_on_step(_gauge: address, _target_apr: uint256):
    """
    @notice set storage for calculate_reward_token_amount, used for testing
    @param _gauge gauges to receive reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    RewardManager(self).set_gauge_data(_gauge, _target_apr)
    RewardManager(self).deposit_reward_token_with_target_rate(_gauge)


@external
def set_gauge_data(_gauge: address, _target_apr: uint256):
    """
    @notice set storage for calculate_reward_token_amount, this is done to avoid front-running
    @param _gauge gauges to receive reward
    @param _target_apr target apr in pips, 1 pip is 1/10000
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    self.gauge_data[_gauge]  = GaugeData({
        tvl: RewardManager(self).crvUSD_tvl_in_gauge(_gauge),
        token_price: RewardManager(self).token_price(),
        target_apr: _target_apr,
        token_amount: 0
    })

    self.gauge_data[_gauge].token_amount = RewardManager(self).calculate_reward_token_amount(_gauge, _target_apr)

@external
def set_mock_gauge_data(_gauge: address):
    """
    @notice set storage for calculate_reward_token_amount, used for testing
    @param _gauge gauges to receive reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    self.gauge_data[_gauge]  = GaugeData({
        tvl: 397157 * 10000,
        token_price: 8739,
        target_apr: 10000,
        token_amount: 0
    })


@external
def set_force_gauge_data(_gauge: address, _tvl: uint256, _token_price: uint256, _target_apr: uint256):
    """
    @notice force gauge data if reward epoch is over
    @param _gauge gauge to receiver reward
    @param _tvl value of pool in $, with 4 decimal places, 1 is 10000
    @param _token_price price of token in $, with 4 decimal places, 1 is 10000
    @param _target_apr target apr in pips, 1 pip is 1/10000
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    self.gauge_data[_gauge] = GaugeData({
        tvl: _tvl,
        token_price: _token_price,
        target_apr: _target_apr,
        token_amount: 0
    })

    self.gauge_data[_gauge].token_amount = RewardManager(self).calculate_reward_token_amount(_gauge, _target_apr)

@view
@external
def calculate_additional_tokens_needed(_gauge: address, _target_apr: uint256) -> uint256:
    """
    @notice Calculate the additional tokens needed to reach the target APR based on the existing reward rate and duration.
    @param _gauge Address of the gauge to receive the reward.
    @param _target_apr Target APR in pips (1 pip = 1/10000 = 0.0001 = 0.01%).
    @return Additional tokens needed to reach the target APR (in token's smallest unit, e.g., wei for 18 decimal tokens).
    """
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'
    assert _target_apr > 0, 'dev: target apr needs to be > 0'

    # Read existing reward data
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    reward_duration: uint256 = reward_data.period_finish - block.timestamp

    # Calculate the existing reward rate in tokens per second
    existing_reward_rate: uint256 = reward_data.rate

    # Calculate the target reward rate in tokens per second to reach the target APR
    tvl: uint256 = RewardManager(self).crvUSD_tvl_in_gauge(_gauge)

    # Adjusted calculation to ensure non-zero values
    target_reward_rate: uint256 = (_target_apr * tvl * PRECISION * PRECISION) / SECONDS_PER_YEAR

    # Calculate the additional reward rate in tokens per second needed to reach the target APR
    additional_reward_rate: uint256 = target_reward_rate + reward_data.rate

    # Calculate the additional token amount needed (assuming 18 decimal places for the token)
    additional_token_amount: uint256 = additional_reward_rate * reward_duration * 10**18

    return additional_token_amount

@view
@external
def calculate_reward_token_amount(_gauge: address, _target_apr: uint256) -> uint256:
    """
    @notice Calculate the amount of reward tokens needed to achieve the target APR
    @param _gauge Address of the gauge to receive the reward
    @param _target_apr Target APR in pips (1 pip = 1/10000 = 0.0001 = 0.01%)
    @return Amount of reward tokens needed (in token's smallest unit, e.g., wei for 18 decimal tokens)
    """
    assert self.gauge_data[_gauge].tvl > 1000 * PRECISION, 'dev: tvl needs to be > $1000'
    assert self.gauge_data[_gauge].token_price > 1, 'dev: token price needs to be > $0.0001'
    assert _target_apr > 50, 'dev: target apr needs to be > 0.5%'

    tvl: uint256 = self.gauge_data[_gauge].tvl
    reward_duration: uint256 = EPOCH  # 1 week in seconds

    # Calculate reward amount in USD (with 4 decimal places)
    reward_usd: uint256 = (_target_apr * tvl * reward_duration) / (SECONDS_PER_YEAR * PRECISION * PRECISION)

    # Calculate token amount (assuming 18 decimal places for the token)
    token_amount: uint256 = reward_usd * 10**18 / self.gauge_data[_gauge].token_price

    return token_amount



@view
@external
def calculate_new_min_apr_old(_gauge: address) -> uint256:
    """
    @notice Calculate the new APR based on the available tokens stretched over one epoch.
    @param _gauge Address of the gauge to receive reward.
    @return New APR calculated based on the total tokens available for the next epoch as 10**18
    """
    # token_price = 6351  in 10**4
    # rate = 425920239494974 in seconds
    # Read current reward data
    # duration = 25219 in seconds
    # tvl = 1469397192 in 10**4
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    reward_duration: uint256 = reward_data.period_finish - block.timestamp

    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'

    # Get the token price and calculate reward in USD
    token_price: uint256 = RewardManager(self).token_price()
    reward_in_usd: uint256 = (reward_data.rate  * reward_duration / 10**18) * token_price 

    # Calculate new APR
    tvl: uint256 = RewardManager(self).crvUSD_tvl_in_gauge(_gauge)
    fraction: uint256 = SECONDS_PER_YEAR  / reward_duration 
    new_apr: uint256 = (reward_in_usd / tvl * fraction) * 10**18

    return new_apr

@view
@external
def calculate_new_min_apr(_gauge: address) -> uint256:
    """
    @notice Calculate the new APR based on the available tokens stretched over one epoch.
    @param _gauge Address of the gauge to receive reward.
    @return New APR calculated based on the total tokens available for the next epoch as 10**4
    """
    # Read current reward data
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    reward_duration: uint256 = reward_data.period_finish - block.timestamp

    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'

    # Get the token price and calculate reward in USD
    token_price: uint256 = RewardManager(self).token_price()
    reward_in_usd: uint256 = (reward_data.rate * reward_duration / 10**18) * token_price  # Convert to USD

    # get tvl
    tvl: uint256 = RewardManager(self).crvUSD_tvl_in_gauge(_gauge)

    # Ensure TVL is greater than zero to avoid division by zero
    assert tvl > 0, 'dev: tvl must be greater than 0'

    # Calculate new APR
    # fraction = SECONDS_PER_YEAR / reward_duration
    # new_apr = (reward_in_usd / tvl) * fraction * 10**4
    new_apr: uint256 = reward_in_usd * 10 ** 1 / tvl * (SECONDS_PER_YEAR / reward_duration)

    return new_apr

@view
@external
def calculate_new_min_apr_simple(_gauge: address) -> uint256:
    """
    @notice Calculate the new APR based on the available tokens stretched over one epoch.
    @param _gauge Address of the gauge to receive reward.
    @return New APR calculated based on the total tokens available for the next epoch as 10**18
    """
 
    # Read current reward data
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    current_apr: uint256 = RewardManager(self).current_apr(_gauge)

    reward_duration: uint256 = reward_data.period_finish - block.timestamp

    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'

    fraction: uint256 = reward_duration * HIGH_PRECISION / EPOCH * HIGH_PRECISION
    new_apr: uint256 = current_apr * fraction / (HIGH_PRECISION**2) 

    return new_apr


@view
@external
def calculate_new_min_apr_pips(_gauge: address) -> uint256:
    new_apr: uint256 = RewardManager(self).calculate_new_min_apr(_gauge) 
    return new_apr/10**14

@view
@external
def token_price() -> uint256:
    """
    @notice get token price from chainlink as 5 decimals
    # todo: integrate decimals from chainlink
    # give fixed price for mock! token is dangerous
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
def crvUSD_tvl_in_gauge(_gauge: address) -> uint256:
    """
    @notice TVL of gauge as crvUSD with 4 decimal places, 1 is 10000
    @param _gauge gauges
    """
    tvl: uint256 = Gauge(_gauge).totalSupply()
    # totalSupply is 10**21
    # tvl is 10**4
    tvl = tvl / 10**17
    return tvl



@external
def set_token_amount(_gauge: address):
    """
    @notice set optimal receiver data
    @param _gauge gauges to receive reward
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert _gauge in self.gauges, 'dev: only gauge which are allowed'

    target_apr: uint256 = self.gauge_data[_gauge].target_apr

    new_token_amount: uint256 = RewardManager(self).calculate_reward_token_amount(_gauge, target_apr)

    self.gauge_data[_gauge].token_amount = new_token_amount
    
###
# section with different apr calculations   
###

@view
@external
def current_apr(_gauge: address) -> uint256:
    """
    @notice current apr in gauge as 10**18
    @param _gauge gauges to receive reward
    @return current apr as 10**18
    """
    
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    tvl: uint256 = RewardManager(self).crvUSD_tvl_in_gauge(_gauge)
    token_price: uint256 = RewardManager(self).token_price()

    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    # rate is per second
    reward_per_year: uint256 = reward_data.rate * SECONDS_PER_YEAR * token_price 
    # apr as 10**18
    current_apr: uint256 = reward_per_year/tvl
    return current_apr


@view
@external
def current_apr_in_pips(_gauge: address) -> uint256:
    """
    @notice current apr in gauge in pips
    @param _gauge gauges to receive reward
    @return current apr in pips, 1 pip is 1/10000
    """
    current_apr: uint256 = RewardManager(self).current_apr(_gauge)
    return current_apr/10 ** 14 


@view
@external
def current_apr_tvl(_gauge: address, _token_price: uint256) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _gauge gauges to receive reward
    @param _token_price price of token in $, with 4 decimal places, 1 is 10000
    """
    assert _token_price > 1, 'dev: tvl needs to be > $0.0001'
    
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)
    tvl: uint256 = RewardManager(self).crvUSD_tvl_in_gauge(_gauge)

    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    # rate is per second
    reward_per_year: uint256 = reward_data.rate * SECONDS_PER_YEAR * _token_price 
    # apr as 10**18
    current_apr: uint256 = reward_per_year/tvl

    return current_apr

@view
@external
def current_apr_tvl_price(_gauge: address, _tvl: uint256, _token_price: uint256) -> uint256:
    """
    @notice forward reward token from contract to gauge
    @param _gauge gauges to receive reward
    @param _tvl value of pool in $, with 4 decimal places, 1 is 10000
    @param _token_price price of token in $, with 4 decimal places, 1 is 10000
    """
    assert _tvl > 1000 * 10000, 'dev: tvl needs to be > $1000'
    assert _token_price > 1, 'dev: tvl needs to be > $0.0001'
    
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)

    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    # only calculate if reward is active
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    # rate is per second
    reward_per_year: uint256 = reward_data.rate * SECONDS_PER_YEAR * _token_price 
    # apr as 10**18
    current_apr: uint256 = reward_per_year/_tvl
    return current_apr


@view
@external
def reward_duration_in_h(_gauge: address)-> uint256:
    reward_data: Reward = Gauge(_gauge).reward_data(self.reward_token)  
    reward_duration: uint256 = reward_data.period_finish - block.timestamp
    assert reward_duration > 0, 'dev: reward_duration needs to be > 0'
    return reward_duration / 3600

@view
@external
def gauge_exists(_gauge: address)-> bool:
    """
    @notice check if gauge is a valid gauge, asking the factory
    @param _gauge gauges to receive reward
    @return bool
    """
    factory: address = 0xabC000d88f23Bb45525E447528DBF656A9D55bf5
    return GaugeFactory(factory).gauge_data(_gauge)

@external
def kill():
    """
    @notice  kill contract if no balance, selfdestruct is deprecated and dangerous too!
    """
    assert msg.sender in self.managers, 'dev: only reward managers can call this function'
    assert ERC20(self.reward_token).balanceOf(self) == 0, 'dev: not empty, balance to recover'
    selfdestruct(msg.sender)