Flyaps load testing.

### Getting started
```bash
sudo apt-get update
sudo apt-get install python3.7
sudo apt-get install python-virtualenv

cd load-testing/
virtualenv --python=python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
python -m load_testing -h
```

### Usage
Simple GET
```bash
python -m load_testing -u https://httpbin.org/get -n 10
```


POST a JSON document
```bash
python -m load_testing -m='POST'\
                       -u='https://httpbin.org/post'\
                       -head='{"Content-Type": "application/json"}'\
                       -p='{"some": "params"}'\
                       -n=10\
                       -t=60
```
