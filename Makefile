all:

start_env:
	# source will not work, but this is for cmd documentation
	source .env
	source .venv/bin/activate

deploy_info:
	ape run scripts/deploy_manager.py info --network arbitrum:mainnet-fork:foundry

deploy_local:
	ape run scripts/deploy_manager.py deploy --network arbitrum:mainnet-fork:foundry

deploy_fixed_rewards_local:
	ape run scripts/deploy_manager.py deploy-fixed-rewards --network arbitrum:mainnet-fork:foundry

deploy_fixed_rewards_arbitrum_sepolia:
	ape run scripts/deploy_manager.py deploy-fixed-rewards --network arbitrum:sepolia:infura

deploy_fixed_rewards_taiko:
	ape run scripts/deploy_manager.py deploy-fixed-rewards --network taiko:mainnet:node

get_constructor_abi:
	python  scripts/get_constructor_abi.py

deploy_arbitrum_sepolia:
	ape run scripts/deploy_manager.py deploy --network arbitrum:sepolia:infura

deploy_arbitrum:
	ape run scripts/deploy_manager.py deploy --network arbitrum:mainnet:infura

deploy_info_taiko:
	ape run scripts/deploy_manager.py info --network taiko:mainnet:node

deploy_taiko:
	ape run scripts/deploy_manager.py deploy --network taiko:mainnet:node

deploy_fixed_rewards_taiko:
	ape run scripts/deploy_manager.py deploy-many-fixed-rewards --network taiko:mainnet:node


import_pvk:
	ape accounts import arbideploy

networks_list:
	ape networks list

noisy_test:
	ape test -rP  --capture=no --network ethereum:local:test

test:
	ape test --network ethereum:local:test

