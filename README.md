# IP Proxy Pool


## Preparing Environment
Clone the repo into your local environment 
```bash
git clone https://github.com/Kugelbrecher/IP-Proxy-Pool.git
```

Create a virtual environment (assuming you have virtualenv installed)
```bash
python3 -m venv venv
```

Activate the virtual environment
```bash
source venv/bin/activate
```

Install dependencies
```bash
python3 -m pip install -r requirements.txt
```


## Connecting to MongoDB
```bash
brew services start mongodb/brew/mongodb-community

# open a new terminal(command + n)
mongosh
show dbs
use proxies_pool
show collections

db.proxies.find()
db.proxies.countDocuments() 

brew services stop mongodb/brew/mongodb-community
```