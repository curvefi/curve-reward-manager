import os
import click

from ape import project

from ape.cli import ConnectedProviderCommand, account_option

REWARD_MANAGERS = os.getenv('REWARD_MANAGERS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
# EXISTING_RECOVERY_GAUGE = os.getenv('EXISTING_RECOVERY_GAUGE')

REWARD_TOKEN_TESTNET = os.getenv('REWARD_TOKEN_TESTNET')
GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')

DEPLOYED_REWARDMANAGER = os.getenv('DEPLOYED_REWARDMANAGER')

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
    """
    if EXISTING_RECOVERY_GAUGE is None:
        recovery_gauge = account.deploy(project.RecoveryGauge, REWARD_TOKEN, RECOVERY_ADDRESS, max_priority_fee="1000 wei", max_fee="0.1 gwei", gas_limit="100000")
    else:
        recovery_gauge = EXISTING_RECOVERY_GAUGE

    gauges.append(recovery_gauge)
    """
    gauges = GAUGE_ALLOWLIST.split(",")
    click.echo(gauges)
    managers = REWARD_MANAGERS.split(",")
    click.echo(managers)

    deploy = account.deploy(project.RewardManager, managers, REWARD_TOKEN, gauges, RECOVERY_ADDRESS, max_priority_fee="10 wei", max_fee="0.1 gwei", gas_limit="400000")

cli.add_command(deploy)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_fixed_rewards(network, provider, account):

    managers = REWARD_MANAGERS.split(",")
    fixed_rewards = account.deploy(project.FixedRewards, managers, max_priority_fee="1000 wei", max_fee="0.1 gwei", gas_limit="100000")

    #fixed_rewards.setup(reward_manager.address, recovery_gauge.address)

    click.echo(fixed_rewards)

cli.add_command(deploy_fixed_rewards)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_many_fixed_rewards(ecosystem, network, provider, account):


    account.set_autosign(True)

    gauges = GAUGE_ALLOWLIST.split(",")
    managers = REWARD_MANAGERS.split(",")
    fixed_rewards_contracts = []

    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")

    if ecosystem.name == 'arbitrum':
        max_fee = "10 gwei"
    else:
        max_fee = "0.1 gwei"
        print("Using max fee of 0.1 gwei")

    for gauge in gauges:
        # Sleep for 1 second between deployments
        import time

        fixed_rewards = account.deploy(project.FixedRewards, managers, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")
        fixed_rewards_contracts.append(fixed_rewards)
        #fixed_rewards.setup(DEPLOYED_REWARDMANAGER, gauge, sender=account, max_priority_fee="1000 wei", max_fee="1 gwei", gas_limit="1000000")

        #epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
        #fixed_rewards.set_reward_epochs(epochs, sender=account, max_priority_fee="1000 wei", max_fee="1 gwei", gas_limit="1000000")

        # Log contract address and transaction info
        with open("fixed_rewards_contracts.log", "a+") as f:
            f.write(f"Fixed Rewards Contract: {fixed_rewards.address}\n")
            f.write(f"Deployed for gauge: {gauge}, but not yet set\n")
            # Get transaction hash from last transaction (set_reward_epochs)
            f.write(f"Link: https://sepolia.arbiscan.io/address{fixed_rewards.address}\n")
            #tx_hash = fixed_rewards.last_tx_hash
            #f.write(f"Transaction: https://sepolia.arbiscan.io/tx/{tx_hash}\n")
            f.write(f"Fixed Rewards Contract List: {[str(contract) for contract in fixed_rewards_contracts]}\n")
            f.write("-" * 80 + "\n")

        # Sleep for 1 second between deployments
        import time
        time.sleep(61)

    click.echo(fixed_rewards_contracts)
    click.echo(fixed_rewards)

cli.add_command(deploy_many_fixed_rewards)