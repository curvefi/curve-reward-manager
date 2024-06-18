# @version 0.3.10
"""
@title RecoveryGauge
@author martinkrung for curve.fi
@license MIT
@notice test gauge for testing and to recover token
"""

from vyper.interfaces import ERC20

reward_token: public(address)
recovery_address: public(address)


struct Reward:
    distributor: address
    period_finish: uint256
    rate: uint256
    last_update: uint256
    integral: uint256

reward_data: public(HashMap[address, Reward])


@external
def __init__(_reward_token: address,_recovery_address: address):
    """
    @notice Contract constructor
    @param _reward_token set reward token fixed
    @param _recovery_address set recovery address
    """
    self.reward_token = _reward_token
    self.recovery_address = _recovery_address

    self.reward_data[_reward_token] = Reward({
        distributor: msg.sender,
        period_finish: 1719000000, # Friday, June 21, 2024 8:00:00 PM
        rate: 2343173790311650,
        last_update: 1718389499,
        integral: 5945129356764
    })

@external
def deposit_reward_token(_reward_token: address, _amount: uint256):
    """
    @notice send recoverd token to predefined recovery address
    @dev _reward_token is not used, it is just to make it compatible with the interface
    @param _reward_token reward token address
    @param _amount amount of reward token to deposit
    """
    
    assert ERC20(self.reward_token).transferFrom(msg.sender, self, _amount, default_return_value=True)


@external
def recover_token()->bool:
    """
    @notice send recoverd token to predefined recovery address
    @dev anybody can call that function to recover token
    """
    amount: uint256 = ERC20(self.reward_token).balanceOf(self)
    if amount > 0:
        assert ERC20(self.reward_token).transfer(self.recovery_address, amount)
        return True
    else:
        return False