# Trader-Monorepo

## What is this?

Trader-Monorepo is a third iteration of my Python and ML-based custom trading terminal,
an experiment in building a rather data-intensive fullstack application to prove a hypothesis for algorithmic cryptocurrency trading.

## What does it do?

It is being developed to have a full-fledged trading terminal web application, and three backends:
ETL (Extract-Transform-Load), Backtesting and Trading.

## What data sources are supported?

I have implementations that read data from Cryptowatch and kuna.io, and can write data
(i.e. perform actual, livewire, fully unattended algorithmic trading) to kuna.io.

## Can I reproduce it or contribute?

Not yet, but probably yes somewhere in 2020Q3. This project isn't even in alpha, it needs its goals and system design figured out
before it can have any public attention.

Currently it's basically a very flaky hypothesis proving testbed with no compatibility in any direction.

## Installation

Clone the monorepo.



```
sudo apt install libpq-dev python3-dev
```

## Local Development

This assumes you want to have a local virtualenv matching the dockerized environment for ease of VS Code usage, etc.

Get your Python and Node.js development environments ready up to the point of a pyenv virtualenv available and active and yarn installed.

For `api`:

```
pyenv virtualenv 3.9.1 trader-api
sudo apt install libpq-dev python3-dev
sudo apt-get install python3-psycopg2
poetry install
```

For `frontend`:

Install nvm, node, and yarn, then in `/frontend`:

```
yarn install
```
