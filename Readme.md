# 🏦 DEX-Sim — A Simple Decentralized Exchange Simulation Platform

## 📌 Overview

**DEX-Sim** is a command-line based simulation platform for decentralized exchanges (DEX).
It allows users to:

* Create and manage DEXs
* Create liquidity pools
* Provide and withdraw liquidity
* Swap between tokens
* Simulate wallet balances and transaction history

The goal of this project is to **mimic the core mechanism of DEXs such as Uniswap**, and help learners understand how automated market makers (AMM) work in practice.

---

## ✨ Features

* 🧰 Create and register multiple DEXs
* 💧 Create token pairs and liquidity pools
* 👛 Manage user wallets with multiple token balances
* 🔁 Add and remove liquidity with proportional ratios
* 💱 Token swapping using AMM pricing model
* 🧾 Track and display transaction history

---

## 🖥️ Usage

### 1. Clone the repository

```bash
git clone https://github.com/WilsonWukz/dex-sim.git
cd dex-sim
```

### 2. (Optional) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install required dependencies (if any)

```bash
pip install -r requirements.txt
```

### 4. Run the simulation

```bash
python main.py
```

---

## 💻 Example Commands

```text
Enter your command (Type 'GUIDE' for help): +DEX
Enter DEX name: d1
DEX d1 added successfully!

Enter your command (Type 'GUIDE' for help): LP
What's your name: Wilson
Which DEX you want to use?: d1
The token A you want to provide to the pool of d1: BTC
The token B you want to provide to the pool of d1: ETH
...
```

Supported commands include:

* `+DEX` → Add a new DEX
* `SHOW DEXS` → Display all registered DEXs
* `+WALLET` → Create a new wallet
* `LP` → Provide liquidity
* `SWAP` → Swap between tokens
* `WITHDRAW` → Remove liquidity
* `GUIDE` → Show the help guide

---

## 📂 Project Structure

```
dex-sim/
├── main.py              # Main entry point of the program
├── dex.py               # DEX class and pool management
├── wallet.py            # Wallet and balance management
├── guidance.py          # User guidance and help messages
├── requirements.txt     # Dependencies
└── README.md            # Project documentation
```

---

## 🧠 Concept Reference

* Automated Market Maker (AMM)
* Liquidity Pool
* Constant Product Formula
* Token Swaps
* LP Tokens

This project is designed for educational purposes only and does not involve any real assets or blockchain interaction.

---

## 🧑‍💻 Author

👤 **Wilson Wu**
📬 [GitHub Profile](https://github.com/WilsonWukz)

---

## 🪪 License

This project is licensed under the [MIT License](./LICENSE).