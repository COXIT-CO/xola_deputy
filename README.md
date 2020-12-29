# xola_deputy
Xola, Deputy, and Google Sheets API Integration

# Requirments
Python 3.9

Run `pip install -r requirements.txt` to install all required libraries.

Deputy account, with access token (permanent token)

Xola account ( seller )

Public url ( You can use ngrok )

mapping.csv ( see in step by step )

credentials.json (google account, see in step by step )

token.pickle  (google account, see in step by step )


# Deputy API set up
Users have to generate `deputy_access_token` in deputy web site.
For more detailed instruction read Deputy API Documentation: https://www.deputy.com/api-doc/API/Authentication

# XOLA API set up
Users just need sing up in xola.com. This programme need api-key and user id

# First start
When you clone this repo and want to start programme:
First of all u have to run 'setup.py' file with parameters:

`-xak`: XOLA api-key ( token )

`-ui`: XOLA user id 

`-dat`: deputy access token,which generated on deputy.com

`-did`: deputy id with your sub-address like `1234567678.eu.deputy.com`

`-url`: your public address

`-logmode`: mode of logging handling. To enable logging to console pass 'console'. By default it's 'file'

`-spid` : id of google spreadsheet file


After ending, in `xola_deputy` folder created `Settings.ini` file with all your data. So next time u have not to input all of them

# Run The Script
Just run `xola_deputy.py` file.

# Step by step
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

`python setup.py -xak 57YSB333_U29-333fAsp2xw04_LZkzfemv5o-rCgYO0 -ui 5fbe33dc5333ed24da1e3333 -dat efnjwe23jfnj3d32dn3oir -did 1234567678.eu.deputy.com -url http://60243e0591b0.ngrok.io -logmode console -spid 33333uoirlxXaVVbbsTWtW8JbjglusqArqvtaMDdn_YM  `

You have to have .csv file `mapping.csv` in directory `xola_deputy/`. This file have a headlines:

`experience_id,experience_name,Area,Possible Area Nicknames in Production,Shifts logic`

Where:

`experience_id` - id experience in xola

`experience_name` - title of experience in xola

`Area` - id location in deputy

`Possible Area Nicknames in Production` - title of google sheets list

`Shifts logic` - determine number of shifts 

File for connect google sheets: `credentials.json`, `token.pickle`

`credentials.json`: CLIENT CONFIGURATION, 

`token.pickle`: stores the user's access and refresh tokens

see google sheets documentation https://developers.google.com/sheets/api
