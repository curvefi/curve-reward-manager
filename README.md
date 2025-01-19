# About

This Distributor allows to use deposit_reward_token() only on a preset of gauges provided on contract creation. 

The guard can decide on the time and on the size of the reward, but has no access to funds anytime.

If a RecoveryAddress is set, the guard can be used to send back funds to a RecoveryAddress

SingleCampaigns allows to set pre-defind reward epochs for on gauge over the Distributor.

SingleCampaigns can be loaded with crvUSD which then pays out 1 crvUSD on execution of one of the epochs.


# Flowchart

## Deploy Distributor


[![](https://mermaid.ink/img/pako:eNp9UlFvgjAQ_ivkntHQMpD2YYmGxKdli_Np4EO1NyVKMQW2MfW_rwWWsWXah37tfXffXe96gk0hETikaqvFcecs41Q5ZpX1ujPEeDwUTY6q6gi7piTpzKhXAytN4qysdLauq-IX4ScL3BRvqJuplBrLckgSZzS6P8tWrzwblRuc33GoZKr-1vmTuq95WFmrU2JlRGYkmddCy5I7LXpuh6RHf3UtkJpnvBuPZbFHxZ3pYuaYZI9PdheqcSprvxrtJ3NRb9GmtWjTWiQ90h79GwL_d7HtBriQo85FJs0wT5ZIodphjilwc5RC71Mz5IvxE6ZHz43aAK90jS7oot7ugL-KQ2lu9VGKCuNMmLbm3y5HoV6KYngFfoIP4JNgTCMvJEFAmUcZoy40wKkxR_6dx5jPJlFIg4sLn228Nw6jwGNhFLIgiPyQEBdQZmZoD90_bL_j5QuuJci8?type=png)](https://mermaid.live/edit#pako:eNp9UlFvgjAQ_ivkntHQMpD2YYmGxKdli_Np4EO1NyVKMQW2MfW_rwWWsWXah37tfXffXe96gk0hETikaqvFcecs41Q5ZpX1ujPEeDwUTY6q6gi7piTpzKhXAytN4qysdLauq-IX4ScL3BRvqJuplBrLckgSZzS6P8tWrzwblRuc33GoZKr-1vmTuq95WFmrU2JlRGYkmddCy5I7LXpuh6RHf3UtkJpnvBuPZbFHxZ3pYuaYZI9PdheqcSprvxrtJ3NRb9GmtWjTWiQ90h79GwL_d7HtBriQo85FJs0wT5ZIodphjilwc5RC71Mz5IvxE6ZHz43aAK90jS7oot7ugL-KQ2lu9VGKCuNMmLbm3y5HoV6KYngFfoIP4JNgTCMvJEFAmUcZoy40wKkxR_6dx5jPJlFIg4sLn228Nw6jwGNhFLIgiPyQEBdQZmZoD90_bL_j5QuuJci8)
```
graph TD
    subgraph Deployment
        A1[Deployer]
        A2[Distributor]
        A3[RecoveryAddress]
        A1 -->|deploys| A2
        A1 -->|deploys| A3
    end

    subgraph Distributor Deploy
        A2 -->|sets| B1[Guards: Guard0, Guard1, Guard3]
        A2 -->|sets| B2[RewardToken: ARB or OP or any token]
        A2 -->|sets| B3[Gauges: Gauge0, Gauge1, Gauge2, Gauge3]
        A2 -->|sets| B3[RecoveryAddress]
    end
```

## Interaction with Distributor

[![](https://mermaid.ink/img/pako:eNp1Uu9r2zAQ_VeO-zA6cNPITuzaHwalNmVsbMMtDBqNolqKY1JLRj-2pXH-98l11rpl0yfd3XtP7-60x0pxgRnWmnUbuMmpBH-Mux8TH6UVmlW2URLyxljd3DurNLyDUlTqp9C7C861MGbkDScnqyvHNAcPu25k_SAuWduxppZwqaQd1H5M0OFqojstEDg9_dBTNELyOy1-eck7q7ZCntTM1SIA1ionbQCiU9XmPcXei02Fj_y10gPXQFl8vyhzuPn6qfgCsNaqnbZEEXoovfdBfH5GzsKJmXI081rCGcGBGRi9mR5uycpYtvXZz9-eyf_oSI-jO3Zz8mS9IC_AgvxnJsWoMEzkbTtW9XBFVm-2cuR6PJVUYoCt0C1ruF_4fihRtBvRCoqZv3KmtxSpPHgc8y9f72SFmdVOBKiVqzeYrdmD8ZHrOLMib5j_JO1ztmPyVqn2L8WHmO3xN2YkDmfncXyeLtIkWoSLJA5wh1m0iGZLEqVpmpAwmYfxIcDHJ4H5bJlEaRyGvkCiZUSWhz8WSM99?type=png)](https://mermaid.live/edit#pako:eNp1Uu9r2zAQ_VeO-zA6cNPITuzaHwalNmVsbMMtDBqNolqKY1JLRj-2pXH-98l11rpl0yfd3XtP7-60x0pxgRnWmnUbuMmpBH-Mux8TH6UVmlW2URLyxljd3DurNLyDUlTqp9C7C861MGbkDScnqyvHNAcPu25k_SAuWduxppZwqaQd1H5M0OFqojstEDg9_dBTNELyOy1-eck7q7ZCntTM1SIA1ionbQCiU9XmPcXei02Fj_y10gPXQFl8vyhzuPn6qfgCsNaqnbZEEXoovfdBfH5GzsKJmXI081rCGcGBGRi9mR5uycpYtvXZz9-eyf_oSI-jO3Zz8mS9IC_AgvxnJsWoMEzkbTtW9XBFVm-2cuR6PJVUYoCt0C1ruF_4fihRtBvRCoqZv3KmtxSpPHgc8y9f72SFmdVOBKiVqzeYrdmD8ZHrOLMib5j_JO1ztmPyVqn2L8WHmO3xN2YkDmfncXyeLtIkWoSLJA5wh1m0iGZLEqVpmpAwmYfxIcDHJ4H5bJlEaRyGvkCiZUSWhz8WSM99)

```graph TD
    subgraph Interaction Distributor & RecoveryAddress
        D1[Guard or SingleCampaign Contract]
        D2[Distributor]
        D1 -->|"send_reward_token(gauge, amount, epoch)"| D2
        D2 -->|"forwards REWARD TOKEN  from Distributor" | R1[Gauge0/1/2]
        R1 -->| REWARD TOKEN used as rewards| Z1[staked LP]
      
        D1 -->|"recover_token(()"| E1
        E1[Distributor]
        E1 -->|sends REWARD TOKEN  to| G1[RecoveryAddress]
    end

```

## Install

```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install eth-ape'[recommended-plugins]'
ape plugins install arbitrum
ape test
```

## With SingleCampaign

1. Deploy many SingleCampaign contracts instances
2. Collect all contract addresses from the deployments of the SingleCampaign contracts
3. Add all contract addresses to the guards array of the Distributor
4. Deploy the Distributor
5. Set Distributor contract address and reward receiver address (gauge) for each SingleCampaign
6. set desired reward epochs for each SingleCampaign
7. if the Distributor has funds, call distribute_reward() can be called by anyone and the campaigne can be started 


## Passtrough 

https://arbiscan.io/address/0xB1a17c8BCb17cd0FDAb587c6b09749b021861E70