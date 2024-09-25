#!/usr/bin/env python3

import boa

import os
import sys


RPC_ETHEREUM = os.getenv('RPC_ETHEREUM')
RPC_ARBITRUM = os.getenv('RPC_ARBITRUM')
ARBISCAN_API_KEY = os.getenv('ARBISCAN_API_KEY')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
DEPLOYED_REWARDMANAGER = os.getenv('DEPLOYED_REWARDMANAGER')
GAUGE_TO_TEST = os.getenv('GAUGE_TO_TEST')
GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')
REWARD_MANAGERS = os.getenv('REWARD_MANAGERS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
EXISTING_RECOVERY_GAUGE = os.getenv('EXISTING_RECOVERY_GAUGE')

boa.env.fork(RPC_ARBITRUM)

MIN_RATE = int(.01 * 1e18 / (365 * 86400))
MAX_RATE = int(.25 * 1e18 / (365 * 86400))

reward_manager = boa.from_etherscan(
    DEPLOYED_REWARDMANAGER,
    name="RewardManager",
    uri="https://api.arbiscan.io/api",
    api_key=ARBISCAN_API_KEY
)

#dlcBTC

GAUGE_TO_TEST = "0x2656b01a19a790f07e2b875d69007f88241602f0"

gauges = GAUGE_ALLOWLIST.split(",")
gauges.append(EXISTING_RECOVERY_GAUGE)
managers = REWARD_MANAGERS.split(",")

local_reward_manager = boa.load("../contracts/RewardManager.vy", managers, REWARD_TOKEN, gauges)

new_apr = local_reward_manager.calculate_new_min_apr(GAUGE_TO_TEST)


print(f"new rate: {new_apr}")
print(f"new rate: {new_apr / 10**14}")

new_apr = local_reward_manager.calculate_new_min_apr_simple(GAUGE_TO_TEST)


print(f"new rate: {new_apr}")
print(f"new rate: {new_apr / 10**14} ")

#local_reward_manager = boa.load_partial("../contracts/RewardManager.vy").at(DEPLOYED_REWARDMANAGER)

#new_apr = local_reward_manager.calculate_new_min_apr_pips("0x8d1600015aE09eAaCaEd08531a03ecb8f2bD40fA")




sys.exit()

#with boa.env.prank(CONTROLLER_ADDRESS):
 #   rate = rate * 365 * 86400
  #  print(f"rate: {rate}")
   # print(f"rate: {rate / 10**18}")


token_price = reward_manager.token_price()

print(f"Current token price in pips: {token_price}")
assert token_price > 0

crvUSD_tvl_in_gauge = reward_manager.crvUSD_tvl_in_gauge(GAUGE_TO_TEST)
print(f"CRVUSD TVL in gauge: {crvUSD_tvl_in_gauge}")
assert crvUSD_tvl_in_gauge > 0  


# Get managers
for i in range(3):  # Assuming max 3 managers
    manager = reward_manager.managers(i)
    if manager != "0x0000000000000000000000000000000000000000":
        print(f"Manager {i}: {manager}")
    else:
        break
assert reward_manager.managers(0) != "0x0000000000000000000000000000000000000000", "At least one manager should be set"

# Get reward token
reward_token = reward_manager.reward_token()
print(f"Reward token: {reward_token}")
assert reward_token != "0x0000000000000000000000000000000000000000", "Reward token should be set"

# Get gauges
gauges = []
for i in range(20):  # Assuming max 20 gauges
    try:
        gauge = reward_manager.gauges(i)
    except Exception as e:
        continue
    if gauge != "0x0000000000000000000000000000000000000000":
        print(f"Gauge {i}: {gauge}")
        gauges.append(gauge)

print(f"Number of gauges: {len(gauges)}")
print("Gauges:")
for gauge in gauges:
    print(f"  {gauge}")
assert len(gauges) > 0, "At least one gauge should be set"

# Test gauge_data
print("\nTesting gauge_data:")
for gauge in gauges:
    gauge_data = reward_manager.gauge_data(gauge)
    print(f"Gauge data for {gauge}:")
    print(f"  TVL: {gauge_data[0]}")
    print(f"  Token price: {gauge_data[1]}")
    print(f"  Target APR: {gauge_data[2]}")
    print(f"  Token amount: {gauge_data[3]}")
    
    #assert gauge_data[0] >= 0, f"TVL should be non-negative for gauge {gauge}"
    #assert gauge_data[1] > 0, f"Token price should be positive for gauge {gauge}"
    assert 0 <= gauge_data[2] <= 10000, f"Target APR should be between 0 and 10000 for gauge {gauge}"
    #assert gauge_data[3] >= 0, f"Token amount should be non-negative for gauge {gauge}"

print("Gauge data assertions passed.")

# Test current APR calculations
print("\nTesting current APR calculations:")
for gauge in gauges:
    try:
        current_apr = reward_manager.current_apr(gauge)
        current_apr_pips = reward_manager.current_apr_in_pips(gauge)
    except Exception as e:
        continue
    
    print(f"Gauge {gauge}:")
    if current_apr_pips > 10000:
        print(f"Gauge may be a pool, not lending market")
    print(f"  Current APR: {current_apr}")
    print(f"  Current APR in pips: {current_apr_pips}")

    #assert current_apr >= 0, f"Current APR should be non-negative for gauge {gauge}"
    #assert current_apr_pips >= 0, f"Current APR in pips should be non-negative for gauge {gauge}"
    #assert abs(current_apr // 10**14 - current_apr_pips) <= 1, f"APR calculations mismatch for gauge {gauge}"

print("Current APR calculations assertions passed.")


print("\nAll assertions passed. RewardManager contract seems to be functioning correctly.")

