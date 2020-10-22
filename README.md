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
python main.py -h
```

### Load testing
```bash
python main.py -m='GET'\
                    -u='https://some.url.com/'\
                    -head='{"Content-Type": "application/json"}'\
                    -p='{"some": "params"}'\
                    -n=100

python main.py -m='GET'\
                    -u='https://some.url.com/'\
                    -head='{"Content-Type": "application/json"}'\
                    -n=100
```
