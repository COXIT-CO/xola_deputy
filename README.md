# xola_deputy
Xola, Deputy, and Google Sheets API Integration

#Requirments
Python 3.9

#Deputy API set up
Users have to generate `deputy_access_token` in deputy web site.
For more detailed instruction read Zoho CRM API Documentation: https://www.deputy.com/api-doc/API/Authentication

#XOLA API set up
Users just need sing up in xola.com. This programe need e-mail and password

#First start
When you clone this repo and want to start programme:
First of all u have to run 'setup.py' file with parameters:
`-ex`: email of XOLA user
`-px`: password of XOLA user
`-dat`: deputy access token,which generated on deputy.com
`-did`: deputy id with your sub-address like `1234567678.eu.deputy.com`
`-url`: your public address
`-logmode`: mode of logging handling. To enable logging to console pass 'console'. By default it's 'file'

After ending, in `xola_deputy` folder created `Settings.ini` file with all your data. So next time u have not to input all of them

#Run The Script
Just run `xola_deputy.py` file.


 

