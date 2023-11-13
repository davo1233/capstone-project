Tested on VirtualBox - Lubuntu

MUST USE THESE COMMANDS BEFORE STARTING:
$ sudo apt update
$ sudo apt upgrade

Setting up MySQL (https://www.mysql.com/):
In terminal, use commands:
$ sudo apt-get install mysql-server
After installation, start the mysql server with command:
$ sudo systemctl start mysql.service
Setup a mysql username and password:
$ sudo mysql
mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
Verify that the account is setup correctly:
mysql> exit
$ sudo mysql -u root -p
When prompted to enter password, enter 'root' (without quotes).
Then set up the database in MySQL:
mysql> CREATE DATABASE chadgpt;


Unzip the zipped folder (capstone-project-3900w14achadgpt) to wherever you want.

Next steps are to setup and start the backend and frontend.
Use one terminal each.

Setting up backend:
Install python3:
$ sudo apt install python3
$ sudo apt install python3-pip
Note: The following steps assumes python 3.7+ and pip is installed and working (https://www.python.org/)
Open terminal to the capstone-project folder.
Install the required python modules:
$ pip install fastapi
$ pip install "uvicorn[standard]"
$ pip install mysql-connector-python
$ pip install SQLAlchemy
$ pip install -r requirements.txt
Once installed, move to the backend folder:
$ cd project
Start the backend with:
$ python3 -m uvicorn main:app --reload


Setting up frontend:
Install nodejs and npm:
$ sudo apt-get install curl
$ curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
$ sudo apt-get install -y nodejs
Note: The following assumes nodejs and npm is installed and running correctly (https://nodejs.org/en) (https://www.npmjs.com/)
Open terminal to the capstone-project folder.
Move to the frontend folder:
$ cd my-app
Install required modules:
$ npm install
Start the frontend:
$ npm start

Once the frontend starts up, it should open a tab in the browser.
Otherwise, in a browser, head to 'http://localhost:3000/'.

If a page fails to load the correct data, the backend needs to be restarted.

The backend docs can be accessed with in 'http://localhost:8000/docs'
