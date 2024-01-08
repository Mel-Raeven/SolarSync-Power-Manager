# HiveOS solar mining

## Description
This project was made because I wanted my HiveOS miner to start and stop mining based on the output of my solar panels. Before starting this I already installed KlikAanKlikUit smart switches in my home and plugged a smart p1 meter in the hub, so I wanted to take advantage of what I already had.

## What do you need to use this?

- KlikAanKlikUit smart plug
- IC2000 hub (to my knowledge this will only work with the IC2000)
- Smart P1 meter attatched to your KaKu hub
- HiveOS farm (duh)

## Installation guide

1. rename the `.env-example` to `.env`
2. fill in the fields of the `.env` file
3. (optional) make a pyenv if you want
4. install requirements: ```pip install -r requirements.txt```
5. run `python main.py`