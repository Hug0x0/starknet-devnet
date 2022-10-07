"""
Test block number
"""

import pytest

from .account import declare, invoke
from .shared import (
    ARTIFACTS_PATH,
    FAILING_CONTRACT_PATH,
    GENESIS_BLOCK_NUMBER,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
)
from .util import devnet_in_background, deploy, call

BLOCK_NUMBER_CONTRACT_PATH = f"{ARTIFACTS_PATH}/block_number.cairo/block_number.json"
BLOCK_NUMBER_ABI_PATH = f"{ARTIFACTS_PATH}/block_number.cairo/block_number_abi.json"


def my_get_block_number(address: str):
    """Execute my_get_block_number on block_number.cairo contract deployed at `address`"""
    return call(
        function="my_get_block_number", address=address, abi_path=BLOCK_NUMBER_ABI_PATH
    )


EXPECTED_TX_HASH = "0x4df621f3aa655224d2cbce2d00d911cc58f78ebd75c3611db2ba3abad25dd85"


@pytest.mark.usefixtures("run_devnet_in_background")
@pytest.mark.parametrize(
    "run_devnet_in_background, expected_tx_hash",
    [
        ([*PREDEPLOY_ACCOUNT_CLI_ARGS], EXPECTED_TX_HASH),
        ([*PREDEPLOY_ACCOUNT_CLI_ARGS, "--lite-mode"], "0x0"),
    ],
    indirect=True,
)
def test_block_number_incremented(expected_tx_hash):
    """
    Tests how block number is incremented in regular mode and lite mode.
    In regular mode with salt "0x42" our expected hash is
    0x4f1ea446f67c1be47619444eae4d8118f6e017d0e6fe16e89b3df03da38606d.
    In lite mode we expect 0x4f1ea446f67c1be47619444eae4d8118f6e017d0e6fe16e89b3df03da38606d
    transaction hash because currently, we can't disable tx hash calculations.
    """

    deploy_info = deploy(BLOCK_NUMBER_CONTRACT_PATH, salt="0x42")
    block_number_before = my_get_block_number(deploy_info["address"])

    assert int(block_number_before) == GENESIS_BLOCK_NUMBER + 1
    assert expected_tx_hash == deploy_info["tx_hash"]

    invoke(
        calls=[(deploy_info["address"], "write_block_number", [])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )

    written_block_number = call(
        function="read_block_number",
        inputs=[],
        address=deploy_info["address"],
        abi_path=BLOCK_NUMBER_ABI_PATH,
    )
    assert int(written_block_number) == GENESIS_BLOCK_NUMBER + 2

    block_number_after = my_get_block_number(deploy_info["address"])
    assert int(block_number_after) == GENESIS_BLOCK_NUMBER + 2


@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_block_number_incremented_on_declare():
    """Declare tx should increment get_block_number response"""

    deploy_info = deploy(BLOCK_NUMBER_CONTRACT_PATH)
    block_number_before = my_get_block_number(deploy_info["address"])
    assert int(block_number_before) == GENESIS_BLOCK_NUMBER + 1

    # just to declare a new class - nothing fails here
    declare(
        FAILING_CONTRACT_PATH,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )

    block_number_after = my_get_block_number(deploy_info["address"])
    assert int(block_number_after) == GENESIS_BLOCK_NUMBER + 2


@devnet_in_background()
def test_block_number_not_incremented_if_deploy_fails():
    """
    Since the deploy fails, no block should be created;
    get_block_number should return an unchanged value
    """

    deploy_info = deploy(BLOCK_NUMBER_CONTRACT_PATH)
    block_number_before = my_get_block_number(deploy_info["address"])
    assert int(block_number_before) == GENESIS_BLOCK_NUMBER + 1

    deploy(FAILING_CONTRACT_PATH)

    block_number_after = my_get_block_number(deploy_info["address"])
    assert int(block_number_after) == GENESIS_BLOCK_NUMBER + 1


@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_block_number_not_incremented_if_invoke_fails():
    """
    Since the invoke fails, no block should be created;
    get_block_number should return an unchanged value
    """

    deploy_info = deploy(BLOCK_NUMBER_CONTRACT_PATH)
    block_number_before = my_get_block_number(deploy_info["address"])
    assert int(block_number_before) == GENESIS_BLOCK_NUMBER + 1

    invoke(
        calls=[(deploy_info["address"], "fail", [])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=10**18,  # must supply max fee so that it's not calculated implicitly
    )

    block_number_after = my_get_block_number(deploy_info["address"])
    assert int(block_number_after) == GENESIS_BLOCK_NUMBER + 1
