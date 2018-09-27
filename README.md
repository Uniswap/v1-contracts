## Whitepaper
https://hackmd.io/C-DvwDSfSxuh-Gd4WKE_ig?view

## Email
hayden@uniswap.io

## Installation:

#### Tested in macOS High Sierra

1) Install Python 3 (requires [Homebrew](https://brew.sh/))
```
$ xcode-select --install (if needed)
$ brew install python3
```

2) Clone Uniswap repo
```
$ git clone https://github.com/Uniswap/contracts-vyper
$ cd contracts-vyper
```

3) Update pip and setup virtual environment
```
$ pip3 install --upgrade pip
$ pip3 install virtualenv
$ virtualenv -p python3 env
$ source env/bin/activate
```

4) [Install Vyper](https://vyper.readthedocs.io/en/latest/installing-vyper.html)
```
$ git clone https://github.com/ethereum/vyper.git
$ cd vyper
$ make
$ make test
$ cd ..
```

5) Install other dependencies
```
$ pip install pytest
$ pip install eth-tester[py-evm]==0.1.0b32
pip install web3==4.4.1
```

6) Run tests
```
$ cd tests
$ pytest -v
```

6) If you run into issues...
```
$ brew install pkg-config autoconf automake libyaml
$ brew install gmp
$ export CFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix libyaml)/include"
$ export LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix libyaml)/lib"
```
