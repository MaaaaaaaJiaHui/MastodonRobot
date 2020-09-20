# MastodonRobot

## Project Description

Based on Mashtodon, this project implements a BOT, aiming to help teachers and provide help for the daily study and life of school students to improve their learning efficiency.

## Environment Preparation

### Basic environmental preparation

1. Install Python 3.8
2. Install MySQL 5.7

### Preparation of the Python library

After installing Python, it is necessary to install the following Python libraries by run the command:

```
pip3 install -r requirements.txt
```
It would install packages:

1. Django
2. Ananas
3. pymysql
4. bs4
5. Mysqlclient

### Basic Data Preparation
After installing the python dependencies above, perform the following Django migration operation and create a new backend table:
1. Create a database in the MYSQL database named mastodon_bot, and set the account name is root, password is null.
2. Enter the project directory.
3. Execute command:
```
python manage.py migrate
```

> You could change the database settings by editing next files:
> 
> `bot.py`
> 
> `mastodonrobot\mastodonrobot\settings.py`

### Mashtodon Account

To use bot client, it is necessary to make sure that user can connect locally to bot
on the remote server.
To achieve this, the following points need to be implemented:

1. Copy the `config.cfg.example` to a new file `config.cfg`.
2. Select a service provider and set up an account.
3. Fill the domain name of the service provider into the domain of the local project file config.cfg.
4. Log in and switch to account settings.
5. Check the box "This is a robot account" in the general column.
6. Switch to the Development TAB and add an application with any name.
7. After adding the application, it can be seen in the Development TAB. Then, click the application and enter the detail page.
8. Fill in client_id, client_secret and token in config.cfg from the detail page.

```
# config.cfg should looks like this:
[HELLOBOT]
class = bot.HelloBot
domain = <your instance name here>
client_id = <your client key here>
client_secret = <your client secret here>
access_token = <your access token here>
```

## Run the server

### Run the backend server

Enter the project directory and perform the following operations to start the background manager program: 
```
python manage.py runserver
```
After the successful start, according to the command line instruction access to the specified link, it can enter the background management system and operate the data in the database.

### Run the bot server

At first, you need to start the MySQL server, because the bot need connect to the database at the next steps.

Enter the project directory and execute the following command to start the bot client: 
```
ananas config.cfg
```
After successful startup, the bot account can be put into use.