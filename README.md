* Docs: [https://docs.uniswap.io/](https://docs.uniswap.io/)
* Reddit: [https://www.reddit.com/r/Uniswap/](https://www.reddit.com/r/UniSwap/)
* Email: [hayden@uniswap.io](mailto:hayden@uniswap.io)
* Whitepaper: [Link](https://hackmd.io/C-DvwDSfSxuh-Gd4WKE_ig)

## Installation:

#### Requires [Python 3](https://www.python.org/download/releases/3.0/)

1) Clone Uniswap
```
$ git clone https://github.com/Uniswap/contracts-vyper
$ cd contracts-vyper
```

2) Setup virtual environment
```
$ pip3 install virtualenv
$ virtualenv -p python3 env
$ source env/bin/activate
```

3) Install dependencies
```
pip install -r requirements.txt
```

4) Run tests
```
$ pytest -v tests/
```
