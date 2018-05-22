## Whitepaper
https://hackmd.io/C-DvwDSfSxuh-Gd4WKE_ig?view

## Installation: (will be improved soon)

#### Tested in macOS High Sierra

1) Install python 3 and upgrade pip (requires [Homebrew](https://brew.sh/))
```
$ xcode-select --install (if needed)
$ brew install python3
$ brew install pkg-config autoconf automake libyaml
$ brew install gmp
```

2) Clone Uniswap repo
```
$ git clone https://github.com/Uniswap/contracts-vyper
$ cd contracts-vyper
```

3) Setup virtual environment (recommended)
```
$ pip3 install --upgrade pip
$ pip3 install virtualenv
$ virtualenv uniswap_env
$ source uniswap_env/bin/activate
```

4) [Install Vyper](https://vyper.readthedocs.io/en/latest/installing-vyper.html)
```
$ export CFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix libyaml)/include"
$ export LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix libyaml)/lib"
$ pip install scrypt
$ git clone https://github.com/ethereum/vyper.git
$ cd vyper
$ git reset --hard 89ef7c38e4678b7a49ff1da82bf1045638ce0f12
$ make
$ make test
$ cd ..
```

5) Install other dependencies
```
$ pip install pytest
$ pip install ethereum
```

6) Run tests
```
$ cd tests
$ pytest -v
```
