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

## Interaction

[![](https://mermaid.ink/img/pako:eNqVUstu2zAQ_JXFHooUkB1Tr1o6FHDhNOihF7WniIbBirRsOCIFkmrrWv73UI_G8i2hIIC7nBnNrHjGQnGBKZaa1Xv4uaYS3DLNr6HxTVqhWWEPSkIm_jDNvzPJSqHhg6sL9Vvo0yNrSjHwurUm-YjZTJp-fkOfHhGYzT63FLmolTnYre6BW6uOQt6VnbgHrFKNtB8ptk5qKjtyd0p3JAOr7AvstKpg_BBFaOGB5DdmN_BuiYzkPXVxT-79t7rfdjLbQknbzfBtWcAIOTVxM7YuynsZGZmkzQa7PbgxggMzMDhu4YnkxrKjaz7Xrwmv1K8kX8mTkmIz7Y3p9TDeuz7V1OPDgLhatKqFx-v_WHGuhTGjpkNR2T3oYSV0xQ7c3c1zd0jR7kUlKKZuy5k-UqTy4nCsserHSRaYWt0ID7Vqyj2mO_ZsXNXUnFmxPjB3n6vXbs3kk1LVf4orMT3jX0xnPonmUbCM_SSMk4R8ipcenjD1STgPAz-KgjBJwnBJ_IuH_3oJMg8CsliQyHdvvIwX4eUFU3sDFg?type=png)](https://mermaid.live/edit#pako:eNqVUstu2zAQ_JXFHooUkB1Tr1o6FHDhNOihF7WniIbBirRsOCIFkmrrWv73UI_G8i2hIIC7nBnNrHjGQnGBKZaa1Xv4uaYS3DLNr6HxTVqhWWEPSkIm_jDNvzPJSqHhg6sL9Vvo0yNrSjHwurUm-YjZTJp-fkOfHhGYzT63FLmolTnYre6BW6uOQt6VnbgHrFKNtB8ptk5qKjtyd0p3JAOr7AvstKpg_BBFaOGB5DdmN_BuiYzkPXVxT-79t7rfdjLbQknbzfBtWcAIOTVxM7YuynsZGZmkzQa7PbgxggMzMDhu4YnkxrKjaz7Xrwmv1K8kX8mTkmIz7Y3p9TDeuz7V1OPDgLhatKqFx-v_WHGuhTGjpkNR2T3oYSV0xQ7c3c1zd0jR7kUlKKZuy5k-UqTy4nCsserHSRaYWt0ID7Vqyj2mO_ZsXNXUnFmxPjB3n6vXbs3kk1LVf4orMT3jX0xnPonmUbCM_SSMk4R8ipcenjD1STgPAz-KgjBJwnBJ_IuH_3oJMg8CsliQyHdvvIwX4eUFU3sDFg)

```graph TD
    subgraph Interaction Distributor & RecoveryGauge
        D1[Guard]
        D2[Distributor]
        D1 -->|"deposit_reward_token(gauge, amount)"| D2
        D2 -->|"forwards ARB from Distributor" | E1[RecoveryGauge] 
        D2 -->|"forwards ARB from Distributor" | R1[Gauge0/1/2]
        D1 -->|"deposit_reward_token_from_contract(gauge, amount)"| D2
        D2 -->| sends ARB from Distributor| E1
        D2 -->| sends ARB from Distributor| R1 
        R1 -->| ARB used as reward| Z1[staked lp]
      
        F1[Anyone]
        F1 -->|"recover()"| E1
        E1 -->|sends ARB to| G1[RecoveryAddress]
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