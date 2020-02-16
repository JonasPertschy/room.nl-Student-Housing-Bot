Coded in Germany to support my brother during his studies. For educational purposes only.


***tl;dr;***
This script checks the commuting distance of student housing in the Netherlands and checks if criterias are met before applying to the waiting list.
***Warning: This script alone wont help. The allocation is also about the age of your account.***

# Intro
The student housing market in the Netherlands is very competitive. 
The Netherlands is one of the most popular student locations in the world. It is therefore only logical that many people want to live there.

Young students often find it difficult to find a place to live. The first year, therefore, there are special housing offerings from some universities where every student receive a guaranteed place. However space is limited and this is also done on a first come first serve basis. In the second year, it is then up to the students to find a place to stay. The largest provider is Duwo and their room.nl portal. However, a limited supply meets a extensive demand there. Flats are allocated according to the waiting list concept. 

# Waiting List Concept
In my experience, the most influencing factor for allocation is the date when the room.nl account was registered. Registration costs 35 euros and should be completed as early as possible. After that, it is also important to apply for flats on time. 

# Limit
It is only possible to have up to 5 applications open at the same time. It is therefore advisable to check these regularly. The script will automatically exit once the limit is reached.

# Customization / Configuration
## Provide your room.nl credentials here to allow authentication
```
credentials = {'username':'user','password':'password123'}
```

Get a **free** maps api key from Google. There is no costs as Google gives everyone 200 USD in free credits every month. This is necesarry to check the bicycle distance of each location before waiting list application.
```
googlelocation_api_key = 'AIzaSyCV-XqU1xv**'
```

## Configure the region of your university to avoid unnecesarry lookups:
```
region = "Amsterdam"
```
(Regio Amsterdam/ Regio Deventer/ Regio Haaglanden/ Leiden /Regio Wageningen)


## Enter the name of your university for distance calculation
```
university_coordinates = "Hogeschool+Inholland+Diemen"
```
Any string that can be resolved by google maps to coordinates. 
## How long are you willing to commute to university by bike?
```
maximal_commuting_minutes = 25
```
## How many people should be maximum on the waiting list? 
Remember its also about the age of the room.nl account.
```
maximal_reactions = 36
```
## Proxy access
If your internet access requires a proxy, please provide it here:
```
proxies = {
 "http": "http://myproxy:9400",
 "https": "http://myproxy:9400",
}
```
# How to run it
Always hardcode your settings first in the ./src/script.py file!

## Without docker
### Install python3 and pip3 (check google)
### Browse the src folder
```
cd src
```
### Install dependencies
```
pip3 install -r requirements.txt
```
### Run the script
```
python script.py
```
## With docker
###On your machine
```
sh debug.sh
```
### Just build the docker container
```
sh build.sh
```
### Deployment to a remote box (e.g. VPS/Synology)
Change the content of the deploy.sh script. Replace REGISTRY and REMOTE with your parameters
```
sh deploy.sh
```