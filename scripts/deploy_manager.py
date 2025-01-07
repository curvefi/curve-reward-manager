import os
import click

from ape import project

from ape.cli import ConnectedProviderCommand, account_option

REWARD_MANAGERS = os.getenv('REWARD_MANAGERS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
EXISTING_RECOVERY_GAUGE = os.getenv('EXISTING_RECOVERY_GAUGE')

REWARD_TOKEN_TESTNET = os.getenv('REWARD_TOKEN_TESTNET')
GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')

@click.group()
def cli():
    pass

@click.command(cls=ConnectedProviderCommand)
@account_option()
def info(ecosystem, provider, account, network):
    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")
    click.echo(f"provider_id: {provider.chain_id}")
    click.echo(f"connected: {provider.is_connected}")
    click.echo(f"account: {account}")

cli.add_command(info)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy(network, provider, account):

    if EXISTING_RECOVERY_GAUGE is None:
        recovery_gauge = account.deploy(project.RecoveryGauge, REWARD_TOKEN, RECOVERY_ADDRESS, max_priority_fee="1000 wei", max_fee="0.1 gwei", gas_limit="100000")
    else:
        recovery_gauge = EXISTING_RECOVERY_GAUGE

    gauges = GAUGE_ALLOWLIST.split(",")
    gauges.append(recovery_gauge)
    click.echo(gauges)
    managers = REWARD_MANAGERS.split(",")
    click.echo(managers)

    deploy = account.deploy(project.RewardManager, managers, REWARD_TOKEN, gauges, RECOVERY_ADDRESS, max_priority_fee="10 wei", max_fee="0.1 gwei", gas_limit="400000")

cli.add_command(deploy)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_fixed_rewards(network, provider, account):

    managers = REWARD_MANAGERS.split(",")
    fixed_rewards = account.deploy(project.FixedRewards, managers, max_priority_fee="1000 wei", max_fee="1 gwei", gas_limit="100000", publish=True)

    #fixed_rewards.setup(reward_manager.address, recovery_gauge.address)

    click.echo(fixed_rewards)

cli.add_command(deploy_fixed_rewards)