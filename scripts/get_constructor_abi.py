import os
import click
from ape import project
from eth_abi import encode

REWARD_MANAGERS = os.getenv('REWARD_MANAGERS')


def get_constructor_args():
    managers = REWARD_MANAGERS.split(",")
    print("Managers:", managers)

    # Get constructor ABI
    constructor = next(item for item in project.SingleCampaign.contract_type.abi if item.type == 'constructor')

    # Get the constructor input types
    input_types = [arg.type for arg in constructor.inputs]
    constructor_args = [managers]

    # Encode the arguments
    encoded_args = encode(input_types, constructor_args)
    print("Encoded constructor arguments:", encoded_args.hex())


if __name__ == "__main__":
    get_constructor_args()