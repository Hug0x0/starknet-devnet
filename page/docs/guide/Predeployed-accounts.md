---
sidebar_position: 13
---

# Predeployed accounts

Devnet predeploys `--accounts` with some `--initial-balance`. The accounts get charged for transactions according to the `--gas-price`. A `--seed` can be used to regenerate the same set of accounts. Read more about it in the [Run section](#run).

To get the code of the account (currently fork of OpenZeppelin's [v0.4.0b](https://github.com/OpenZeppelin/cairo-contracts/releases/tag/v0.4.0b)), use one of the following:

- `GET /get_code?contractAddress=<ACCOUNT_ADDRESS>`
- [Starknet CLI](https://www.cairo-lang.org/docs/hello_starknet/cli.html#get-code): `starknet get_code --contract_address <ACCOUNT_ADDRESS> --feeder_gateway_url <DEVNET_URL>`
- [GitHub repository](https://github.com/Shard-Labs/cairo-contracts/tree/fix-account-query-version)

You can use the accounts in e.g. [**starknet-hardhat-plugin**](https://github.com/Shard-Labs/starknet-hardhat-plugin) via:

```typescript
const account = await starknet.getAccountFromAddress(
  ADDRESS,
  PRIVATE_KEY,
  "OpenZeppelin"
);
```
## Fetch predeployed accounts

```
GET /predeployed_accounts
```

Response:

```
[
  {
    "initial_balance": 1e+21,
    "address": "0x7c3e2...",
    "private_key": "0x6160...",
    "public_key": "0x6a5540..."
  },
  ...
]
```

## Fetch account balance

```
GET /account_balance?address=<HEX_ADDRESS>
```

Response:

```
{
  "amount": 123...456,
  "unit": "wei"
}

## Mint token - Local faucet

Other than using prefunded predeployed accounts, you can also add funds to an account that you deployed yourself.

The ERC20 contract used for minting ETH tokens and charging fees is at: `0x62230ea046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488`

### Query fee token address

```
GET /fee_token
```

Response:

```
{
  "symbol":"ETH",
  "address":"0x62230ea046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488",
}
```

### Mint with a transaction

By not setting the `lite` parameter or by setting it to `false`, new tokens will be minted in a separate transaction. You will receive the hash of this transaction, as well as the new balance after minting in the response.

`amount` needs to be an integer (or a float whose fractional part is 0, e.g. `1000.0` or `1e21`)

```
POST /mint
{
    "address": "0x6e3205f...",
    "amount": 500000
}
```

Response:

```
{
    "new_balance": 500000,
    "unit": "wei",
    "tx_hash": "0xa24f23..."
}
```

### Mint lite

By setting the `lite` parameter, new tokens will be minted without generating a transaction, thus executing faster.

```
POST /mint
{
    "address": "0x6e3205f...",
    "amount": 500000,
    "lite": true
}
```

Response:

```
{
    "new_balance": 500000,
    "unit": "wei",
    "tx_hash": null
}
```