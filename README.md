#Your Home Library

##Requirements
Make sure your computer have installed and activated **python3.10** or above, **pip**, **venv**, **nodejs**. 

## Clone
Clone this repository to your local computer.
```shell script
https://github.com/hytnht/ur-home-lib.git
cd ur-hone-lib
```
##Configuration
Create and activate virtualenv:
```shell script
python3 -m venv venv
source .venv/bin/activate
```
Create environment variables `.env`:
```shell script
$touch .env
```
Assign your email and passwords to variables in file `.env `:
```shell script
import os
def setVar():
    os.environ['MAIL_USERNAME'] = 'your_email'
    os.environ['MAIL_PASSWORD'] = 'password'
    os.environ['MAIL_DEFAULT_SENDER'] = 'your_email'

```
##Install dependencies
Install python requirements in root folder:
```shell script
python3 -m pip install -r requirements.tx
```
Instal **nodejs** package in `static` folder:
```shell script
cd static
npm install
```
## Compile SCSS:
Compile `scss` to `css` stylesheet:
```shell script
sass --watch style.scss style.css
```
## Create database
Create table using **sqlite3**:
```shell script
sqlite3 database.db < create.sql
```
## Run
Run project using Flask in root folder:
```shell script
cd ..
flask run 
```



