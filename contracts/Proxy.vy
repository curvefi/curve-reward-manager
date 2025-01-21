#pragma version ^0.4.0
"""
@title Proxy
@author martinkrung for curve.fi
@license MIT
@notice Distributes variable rewards for one gauge through Distributor
"""

event NewProxy:
    proxy: address
    implementation: address
    timestamp: uint256


@external
def deploy_proxy(implementation: address) -> address:
    # Creates and returns the proxy address
    proxy: address = create_minimal_proxy_to(implementation)

    log NewProxy(proxy, implementation, block.timestamp)

    return proxy
