# About

This RewardManager allows to use deposit_reward_token() only on a preset of gauges provided on contract creation. 

The manager can decide on the time and on the size of the reward, but has no access to funds anytime.

If set, a RecoveryGauge can be used to send back funds to a RecoveryAddress

# Flowchart

## Deploy

[![](https://mermaid.ink/img/pako:eNp9UslugzAQ_RU0ZxJhGyj4UClppJ56SXMq5ODGUxIlGGSgLU3y73VYImib2rJmeeM3i-YIm0wicIhVokW-tVaLWFnmFNVr61hgfsjqFFXZApczI1HrRr0eeGm0xA-h5ZNQIhlDzECb7B11_SiqBIcQsSaT-5Ns-IqTYfkHYy2GSsbqR52j1F3Vw9oapgJLQzMnURdXcKvTHLvXyFVj61sEfaerbI-KW7Pl_GYoi5qOTabRBGyrEU4nSSdpJ_vUf3c64PndKRtkfyDXuc-k1FgUY97-gg0p6lTspFmF4yUkhnKLKcbAjSqF3sdmRc4mTlRl9lyrDfBSV2iDzqpkC_xNHApjVbkUJS52wpSaXr25UC9ZlvZfjAn8CJ_AJ5R4U48FPg1dPwzJnR_YUAOnxJ26jHoec8PQdQNCzzZ8NRRkyhhxHOJR8_zAd9zzN2UN2Qg?type=png)](https://mermaid.live/edit#pako:eNp9UslugzAQ_RU0ZxJhGyj4UClppJ56SXMq5ODGUxIlGGSgLU3y73VYImib2rJmeeM3i-YIm0wicIhVokW-tVaLWFnmFNVr61hgfsjqFFXZApczI1HrRr0eeGm0xA-h5ZNQIhlDzECb7B11_SiqBIcQsSaT-5Ns-IqTYfkHYy2GSsbqR52j1F3Vw9oapgJLQzMnURdXcKvTHLvXyFVj61sEfaerbI-KW7Pl_GYoi5qOTabRBGyrEU4nSSdpJ_vUf3c64PndKRtkfyDXuc-k1FgUY97-gg0p6lTspFmF4yUkhnKLKcbAjSqF3sdmRc4mTlRl9lyrDfBSV2iDzqpkC_xNHApjVbkUJS52wpSaXr25UC9ZlvZfjAn8CJ_AJ5R4U48FPg1dPwzJnR_YUAOnxJ26jHoec8PQdQNCzzZ8NRRkyhhxHOJR8_zAd9zzN2UN2Qg)
```

graph TD
    subgraph Deployment
        A1[Deployer]
        A2[RewardManager]
        A3[RecoveryGauge]
        A1 -->|deploys| A2
        A1 -->|deploys| A3
    end

    subgraph RewardManager Deploy
        A2 -->|sets| B1[Managers: Manager0, Manager1, Manager3]
        A2 -->|sets| B2[RewardToken: ARB]
        A2 -->|sets| B3[Gauges: RecoveryGauge, Gauge0, Gauge1, Gauge2, Gauge3]
    end

    subgraph RecoveryGauge Deploy
        A3 -->|sets| C1[RecoveryAddress]
    end
```

## Interaction

[![](https://mermaid.ink/img/pako:eNqVUstu2zAQ_JXFHooUkB1Tr1o6FHDhNOihF7WniIbBirRsOCIFkmrrWv73UI_G8i2hIIC7nBnNrHjGQnGBKZaa1Xv4uaYS3DLNr6HxTVqhWWEPSkIm_jDNvzPJSqHhg6sL9Vvo0yNrSjHwurUm-YjZTJp-fkOfHhGYzT63FLmolTnYre6BW6uOQt6VnbgHrFKNtB8ptk5qKjtyd0p3JAOr7AvstKpg_BBFaOGB5DdmN_BuiYzkPXVxT-79t7rfdjLbQknbzfBtWcAIOTVxM7YuynsZGZmkzQa7PbgxggMzMDhu4YnkxrKjaz7Xrwmv1K8kX8mTkmIz7Y3p9TDeuz7V1OPDgLhatKqFx-v_WHGuhTGjpkNR2T3oYSV0xQ7c3c1zd0jR7kUlKKZuy5k-UqTy4nCsserHSRaYWt0ID7Vqyj2mO_ZsXNXUnFmxPjB3n6vXbs3kk1LVf4orMT3jX0xnPonmUbCM_SSMk4R8ipcenjD1STgPAz-KgjBJwnBJ_IuH_3oJMg8CsliQyHdvvIwX4eUFU3sDFg?type=png)](https://mermaid.live/edit#pako:eNqVUstu2zAQ_JXFHooUkB1Tr1o6FHDhNOihF7WniIbBirRsOCIFkmrrWv73UI_G8i2hIIC7nBnNrHjGQnGBKZaa1Xv4uaYS3DLNr6HxTVqhWWEPSkIm_jDNvzPJSqHhg6sL9Vvo0yNrSjHwurUm-YjZTJp-fkOfHhGYzT63FLmolTnYre6BW6uOQt6VnbgHrFKNtB8ptk5qKjtyd0p3JAOr7AvstKpg_BBFaOGB5DdmN_BuiYzkPXVxT-79t7rfdjLbQknbzfBtWcAIOTVxM7YuynsZGZmkzQa7PbgxggMzMDhu4YnkxrKjaz7Xrwmv1K8kX8mTkmIz7Y3p9TDeuz7V1OPDgLhatKqFx-v_WHGuhTGjpkNR2T3oYSV0xQ7c3c1zd0jR7kUlKKZuy5k-UqTy4nCsserHSRaYWt0ID7Vqyj2mO_ZsXNXUnFmxPjB3n6vXbs3kk1LVf4orMT3jX0xnPonmUbCM_SSMk4R8ipcenjD1STgPAz-KgjBJwnBJ_IuH_3oJMg8CsliQyHdvvIwX4eUFU3sDFg)

```graph TD
    subgraph Interaction RewardManager & RecoveryGauge
        D1[Manager]
        D2[RewardManager]
        D1 -->|"deposit_reward_token(gauge, amount)"| D2
        D2 -->|"forwards ARB from Manager" | E1[RecoveryGauge] 
        D2 -->|"forwards ARB from Manager" | R1[Gauge0/1/2]
        D1 -->|"deposit_reward_token_from_contract(gauge, amount)"| D2
        D2 -->| sends ARB from RewardManager| E1
        D2 -->| sends ARB from RewardManager| R1 
        R1 -->| ARB used as reward| Z1[staked lp]
      
        F1[Anyone]
        F1 -->|"recover()"| E1
        E1 -->|sends ARB to| G1[RecoveryAddress]
    end
```

## Origin

Based on https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/streamers/RewardStream.vy

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
3. Add all contract addresses to the managers array of the RewardManager
4. Deploy the RewardManager
5. Set RewardManager contract address and reward receiver address (gauge) for each SingleCampaign
6. set desired reward epochs for each SingleCampaign