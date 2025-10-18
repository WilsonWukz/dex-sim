# guidance.py
banner = r"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ____  _____  __   ____   ____  _                        ║
║ |  _ \| ____|/ _| / ___| / ___|| |_ ___  __ _ _ __ ___   ║
║ | | | |  _| | |_  \___ \ \___ \| __/ _ \/ _` | '_ ` _ \  ║
║ | |_| | |___|  _|  ___) | ___) | ||  __/ (_| | | | | | | ║
║ |____/|_____|_|   |____/ |____/ \__\___|\__,_|_| |_| |_| ║
║                                                          ║
║                  Welcome to DEX-Sim !!!                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
print(banner)

GUIDANCE_TEXT_EN = r"""
📜 DEX-Sim User Guide (Corresponds exactly to main.py)
──────────────────────────────────────────────
Program Startup State (Default Example):
  - Registered DEX: 'Uniswap'
  - Created Wallet: 'Alice' (10 ETH + already deposited 20000 USDT)
  - Registered Pool: ETH/USDT (reserves = 10 / 20000) in Uniswap

General Notes
  - Enter a command at the prompt and press Enter to execute. Commands are case-insensitive (main.py converts input to uppercase).
  - To view this help again, type: GUIDE
  - Enter numeric values in decimal format, e.g., 12.5 or 12000 (the program uses Decimal internally for precise calculation).
  - Token symbols must be strictly consistent (e.g., "ETH", "USDT"); case does not affect matching, but avoid spaces or extra characters.

Supported Commands (Strictly matching keywords in main.py)
──────────────────────────────────────────────
GUIDE
  - Displays this help text.

+DEX
  - Adds a new DEX instance.
  - Program prompts: Enter DEX name:
  - Example Operation:
      +DEX
      Enter DEX name: SushiSwap

SHOW DEXS
  - Lists the names of all registered DEXs.

+WALLET
  - Creates a wallet and sets an initial balance for one token.
  - Program prompts:
      Enter your name:
      Enter your wallet symbol:
      Enter your symbol amount:
  - Example:
      +WALLET
      Enter your name: Bob
      Enter your wallet symbol: BTC
      Enter your symbol amount: 1.5

SHOW WALLETS
  - Lists all registered wallets and displays each wallet's balances.

DEPOSIT
  - Deposits a token into a specified wallet (simulation only, not on-chain).
  - Program prompts:
      Enter your name:
      Enter the symbol you want to deposit:
      How much you want to deposit the <symbol>?
  - The operation records a transaction history (type: DEPOSIT).

+POOL
  - Creates and registers a Liquidity Pool within a specified DEX.
  - Program prompts:
      Enter the DEX name to register the pool in:
      Enter the token A (e.g., BTC):
      Enter the token B (e.g., USDT):
      Enter initial reserve amount of <tokenA>:
      Enter initial reserve amount of <tokenB>:
  - Note: You must specify an existing/desired DEX name (e.g., "Uniswap" or a name you created with +DEX).

SHOW POOLS
  - Queries and displays the status of a pool for a token pair in a specific DEX (reserves, price, LP holdings, etc.).
  - Program prompts:
      Enter the DEX name you want to show its pool:
      Enter the token A (e.g., BTC):
      Enter the token B (e.g., USDT):

SWAP
  - Initiates an exchange (proactively initiated by a wallet, executed via the AMM pool).
  - Program prompts (in order):
      Wallet owner name:
      Enter DEX name to use:
      Token to swap FROM:
      Enter amount of <token_in> to swap:
      Token to swap TO:
  - Program Execution Flow:
      1) Locates the specified DEX's pool (token_in/token_out).
      2) Checks if the wallet's token_in balance is sufficient.
      3) Calls preview_swap (preview), then executes exec_swap (modifies pool reserves).
      4) Deducts the input token, deposits the output token into the wallet, and records SWAP in the transaction history.
  - Note: If no corresponding pool exists or the balance is insufficient, the program will reject the transaction and indicate the reason.

LP
  - Adds liquidity to the pool (Liquidity Providing).
  - Program prompts (and requires input for the amount of each token during interaction):
      What's your name:
      Which DEX you want to use?:
      The token A you want to provide to the pool of <DEX>:
      The token B you want to provide to the pool of <DEX>:
      Enter the amount you want to provide to the pool: The program will automatically calculate the amountA/B respect to the ratio of the liquidity you provide with the total current liquidity of the pool.
  - The program will attempt to call pool.add_lq(owner, amountA, amountB):
      - If the ratio does not match (must be consistent with the pool's ratio), add_lq will fail, the program will refund and indicate the reason.
      - On success, the amount of LP token obtained is recorded in wallet.lp_tokens, and a transaction history (type: LP) is recorded.

RMLP
  - Removes liquidity from the pool (Remove Liquidity).
  - Program prompts (in order):
      Enter the DEX name you want to use:
      The token A you want to take from the pool:
      The token B you want to take from the pool:
      The liquidity token you want to take from the pool of <DEX>:
  - The program checks your LP balance in that pool and calls pool.remove_lq(owner, lp_amount). Upon success, both tokens are returned to the wallet, and RMLP history is recorded.

HISTORY
  - Views the transaction history for a specific wallet (all deposit / swap / lp / rmlp records).
  - Program prompts:
      What's your name:

SAVE
  - Saves the current state of all DEXs (and their pools) and all wallets (balances, LP, transaction history) to a JSON file.
  - Program prompts:
      Enter filename to save (default: dexsim_state.json):
  - Default filename: dexsim_state.json

LOAD
  - Restores the previously saved state from a JSON file (replaces current in-memory DEXs and Wallets).
  - Program prompts:
      Enter filename to load (default: dexsim_state.json):
  - Note: Loading will overwrite current in-memory objects with data from the file. Proceed with caution.

EXIT
  - Exits the program.

Troubleshooting and Tips (Common Issues)
──────────────────────────────────────────────
  - "Pool/DEX/Wallet not found": Confirm the name matches exactly (no extra spaces) and the object has been created or loaded from a file.
  - "Insufficient balance/Transaction failed": First check wallet balance with SHOW WALLETS; if adding liquidity fails, provide tokens according to the pool's current ratio.
  - Save/Load failed: Confirm you have read/write permission for the path and the JSON file format has not been manually altered.
  - If you encounter an incomprehensible exception, paste the error message or traceback to me, and I will help you pinpoint the issue.

Example Typical Flow (Copy and paste into the interactive shell)
──────────────────────────────────────────────
  +DEX
  Enter DEX name: MyDEX

  +WALLET
  Enter your name: Carol
  Enter your wallet symbol: USDT
  Enter your symbol amount: 50000

  +POOL
  Enter the DEX name to register the pool in: MyDEX
  Enter the token A (e.g., BTC): ETH
  Enter the token B (e.g., USDT): USDT
  Enter initial reserve amount of ETH: 50
  Enter initial reserve amount of USDT: 300000

  SWAP
  Wallet owner name: Carol
  Enter DEX name to use: MyDEX
  Token to swap FROM: USDT
  Enter amount of USDT to swap: 12000
  Token to swap TO: ETH

  LP  (Liquidity Providing Example)
  What's your name: Carol
  Which DEX you want to use?: MyDEX
  The token A you want to provide to the pool of MyDEX: ETH
  The token B you want to provide to the pool of MyDEX: USDT
  Enter the amount you want to provide of ETH: 2
  Enter the amount you want to provide of USDT: 12000

Enjoy your use! If you would like me to automatically bind this help to the commands `GUIDE` and `HELP` (supporting both) or localize the help text to another language/shorter "Quick Start" version, let me know and I will adjust it.
"""

def show_guidance():
    print(GUIDANCE_TEXT_EN)