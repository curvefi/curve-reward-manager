all:

start_env:
	# source will not work, but this is for cmd documentation
	source .env
	source .venv/bin/activate

deploy_info:
	ape run scripts/deploy_manager.py info --network arbitrum:mainnet-fork:foundry

deploy_local:
	ape run scripts/deploy_manager.py deploy --network arbitrum:mainnet-fork:foundry

deploy_arbitrum_sepolia:
	ape run scripts/deploy_manager.py deploy --network arbitrum:sepolia:infura

deploy_arbitrum:
	ape run scripts/deploy_manager.py deploy --network arbitrum:mainnet:infura

import_pvk:
	ape accounts import arbideploy

networks_list:
	ape networks list

noisy_test:
	ape test -rP  --capture=no

test:
	ape test 
