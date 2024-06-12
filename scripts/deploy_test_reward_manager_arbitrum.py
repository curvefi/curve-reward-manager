from pathlib import Path
from readline import append_history_file

import os
import click
from ape import accounts, project, chain, networks
from ape.cli import NetworkBoundCommand, network_option, account_option
from eth._utils.address import generate_contract_address
from eth_utils import to_checksum_address, to_canonical_address
from datetime import datetime

# some constants from .env if needed
# COLLECTOR_ADDRESS = os.getenv('COLLECTOR_ADDRESS')

REWARD_MANAGER = os.getenv('REWARD_MANAGER')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')

REWARD_TOKEN_TESTNET = os.getenv('REWARD_TOKEN_TESTNET')
GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')


@click.group(short_help="Deploy the project")
def cli():
    pass


@cli.command(cls=NetworkBoundCommand)
@account_option()
def deploy_testnet(network, account):

    test_gauge = account.deploy(project.TestGauge, REWARD_TOKEN_TESTNET, RECOVERY_ADDRESS, max_priority_fee="1000 wei", max_fee="2 gwei", gas_limit="100000")

    deploy = account.deploy(project.RewardManager, REWARD_MANAGER, REWARD_TOKEN_TESTNET, [test_gauge], max_priority_fee="1000 wei", max_fee="2 gwei", gas_limit="100000")


@cli.command(cls=NetworkBoundCommand)
@account_option()
def deploy(network, account):

    test_gauge = account.deploy(project.TestGauge, REWARD_TOKEN, RECOVERY_ADDRESS, max_priority_fee="1000 wei", max_fee="2 gwei", gas_limit="100000")

    gauges = GAUGE_ALLOWLIST.split(",")
    gauges.append(test_gauge)
    print(gauges)

    deploy = account.deploy(project.RewardManager, REWARD_MANAGER, REWARD_TOKEN, gauges, max_priority_fee="1000 wei", max_fee="2 gwei", gas_limit="100000")


@cli.command(cls=NetworkBoundCommand)
#@network_option()
@account_option()
def publish(network, account):
    print(account)
    print(network)
    networks.provider.network.explorer.publish_contract("")