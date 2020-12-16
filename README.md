# xola_deputy
Xola, Deputy, and Google Sheets API Integration

#Requirments
Python 3.9

Run `pip install -r requirements.txt` to install all required libraries.

Deputy account, with access token (permanent token)

Xola account ( seller )

Public url ( You can use ngrok )

data_file.json ( see in step by step )

#Deputy API set up
Users have to generate `deputy_access_token` in deputy web site.
For more detailed instruction read Deputy API Documentation: https://www.deputy.com/api-doc/API/Authentication

#XOLA API set up
Users just need sing up in xola.com. This programe need e-mail and password

#First start
When you clone this repo and want to start programme:
First of all u have to run 'setup.py' file with parameters:

`-xap`: XOLA api-key ( token )

`-ui`: XOLA user id 

`-dat`: deputy access token,which generated on deputy.com

`-did`: deputy id with your sub-address like `1234567678.eu.deputy.com`

`-url`: your public address

`-logmode`: mode of logging handling. To enable logging to console pass 'console'. By default it's 'file'


After ending, in `xola_deputy` folder created `Settings.ini` file with all your data. So next time u have not to input all of them

#Run The Script
Just run `xola_deputy.py` file.

#Step by step
First of all , you have to create a seller XOLA account.

Also have to create deputy account.Then:

Login to Deputy

Go to your account

Change the URL path to /exec/devapp/oauth_clients . E.g https://{your subdomain}.deputy.com/exec/devapp/oauth_clients

Create a dummy client of yours and get an Access Token from there

Now you have Permanent Token

You have to have a public IP. You can using web services like ngrok.

Run `pip install -r requirements.txt`
First, start `setup,py` with parameters. E.g 

`python setup.py -xak 57YSB333_U29-333fAsp2xw04_LZkzfemv5o-rCgYO0 -ui 5fbe33dc5333ed24da1e3333 -dat efnjwe23jfnj3d32dn3oir -did 1234567678.eu.deputy.com -url http://60243e0591b0.ngrok.io -logmode console `

You have to have json file `data_file.json` in directory `xola_deputy/`. This file have a structure:

`[{"experience_id": "5b58a24fc481e1a2168b456a", "area": {"area_id": 1, "shift_count": 1}},]`

 This is a list of dictionary. Where key 
 
 `experience_id` - id of experience in XOLA ;
  
 `area` - dictionary with 2 keys: 
 
    `area_id` - id location in deputy, 
 
     `shift_count` - determine number of shifts 

That is all, now you can run xola_deputy.py