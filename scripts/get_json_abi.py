from ape import project

# Get ABI from your contract
abi = project.SingleCampaign.contract_type.abi
print(abi)

# Convert ABI objects to dictionaries
abi_dicts = [item.model_dump() for item in abi]
# Print it nicely formatted
import json
print(json.dumps(abi_dicts, indent=2))
