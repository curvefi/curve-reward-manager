import os
import click
import time

from ape import project

from ape.cli import ConnectedProviderCommand, account_option

REWARD_MANAGERS = os.getenv('REWARD_MANAGERS')
REWARD_MANAGERS_AND_CAMPAIGNS = os.getenv('REWARD_MANAGERS_AND_CAMPAIGNS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
# EXISTING_TEST_GAUGE = os.getenv('EXISTING_TEST_GAUGE')

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
    if EXISTING_TEST_GAUGE is None:
        test_gauge = account.deploy(project.TestGauge, REWARD_TOKEN, RECOVERY_ADDRESS, max_priority_fee="1000 wei", max_fee="0.1 gwei", gas_limit="100000")
    else:
        test_gauge = EXISTING_TEST_GAUGE

    gauges.append(recovery_gauge)
    """
    account.set_autosign(True)

    gauges = GAUGE_ALLOWLIST.split(",")
    click.echo(gauges)
    managers = REWARD_MANAGERS_AND_CAMPAIGNS.split(",")
    click.echo(managers)

    deploy = account.deploy(project.RewardManager, managers, REWARD_TOKEN, gauges, RECOVERY_ADDRESS, max_priority_fee="10 wei", max_fee="0.1 gwei", gas_limit="400000")

cli.add_command(deploy)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_single_campaign(network, provider, account):
    managers = REWARD_MANAGERS.split(",")
    single_campaign = account.deploy(project.SingleCampaign, managers, max_priority_fee="1000 wei", max_fee="0.1 gwei", gas_limit="100000")

    click.echo(single_campaign)

cli.add_command(deploy_single_campaign)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_many_single_campaigns(ecosystem, network, provider, account):
    account.set_autosign(True)

    gauges = GAUGE_ALLOWLIST.split(",")
    managers = REWARD_MANAGERS.split(",")
    single_campaign_contracts = []

    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")

    if ecosystem.name == 'arbitrum':
        max_fee = "10 gwei"
        blockexplorer = "https://sepolia.arbiscan.io"
    else:
        max_fee = "0.1 gwei"
        print("Using max fee of 0.1 gwei")
        blockexplorer = "https://taikoscan.io"


    for gauge in gauges:
        single_campaign = account.deploy(project.SingleCampaign, managers, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")
        single_campaign_contracts.append(single_campaign)

        # Log contract address and transaction info
        with open("single_campaign_contracts.log", "a+") as f:
            f.write(f"Single Campaign Contract: {single_campaign.address}\n")
            f.write(f"Deployed for gauge: {gauge}, but not yet set\n")
            f.write(f"Link: {blockexplorer}/address/{single_campaign.address}\n")
            f.write(f"Single Campaign Contract List: {[str(contract) for contract in single_campaign_contracts]}\n")
            f.write(f"{','.join(str(contract) for contract in single_campaign_contracts)}\n")
            f.write("-" * 80 + "\n")

        # Sleep for 1 second between deployments
     
        time.sleep(61)

    click.echo(single_campaign_contracts)
    click.echo(single_campaign)

cli.add_command(deploy_many_single_campaigns)