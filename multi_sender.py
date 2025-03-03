import asyncio
from web3 import AsyncWeb3
from random import randint
from config import *

GAS_MULTIPLIER = 1.2
w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC))

RECIPIENTS_FILE = open("recipients.txt")
RECIPIENTS_LEN = len(RECIPIENTS_FILE.readline())
RECIPIENTS = []

wallets_type = "addresses"
if RECIPIENTS_LEN > 50:
    wallets_type = "private keys"

for line in RECIPIENTS_FILE:
    if wallets_type == "private keys":
        if line.strip():
            recipient_address = w3.eth.account.from_key(PRIVATE_KEY).address
            RECIPIENTS.append(recipient_address)
    else:
        RECIPIENTS = [line.strip() for line in RECIPIENTS_FILE if line.strip()]


async def send_eth():
    sender = w3.eth.account.from_key(PRIVATE_KEY)
    sender_address = sender.address

    nonce = await w3.eth.get_transaction_count(sender_address)
    chain_id = await w3.eth.chain_id

    for recipient in RECIPIENTS:
        try:
            amount_eth = randint(amount[0] * 10e18, amount[1] * 10e18) / 10e18
            amount_to_recipient = w3.to_wei(amount_eth, 'ether')
            tx = {
                'chainId': chain_id,
                'from': sender_address,
                'to': recipient,
                'value': amount_to_recipient,
                'nonce': nonce,
                'maxPriorityFeePerGas': await w3.eth.max_priority_fee,
                'maxFeePerGas': int(await w3.eth.gas_price * GAS_MULTIPLIER),
                'gas': 21000,
                'type': '0x2',
            }

            # Отправка транзакции
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"Отправлено {w3.from_wei(amount_to_recipient, 'ether')} ETH на {recipient} | TX: {tx_hash.hex()}")

            nonce += 1
            await asyncio.sleep(DELAY)
        except Exception as error:
            print(f'Ошибка: {error} при отправки на кошелёк {recipient}')
            with open("failed.txt", 'a', encoding="utf-8") as f:
                f.write(f'{recipient}\n')

asyncio.run(send_eth())
