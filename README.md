FP Live Chat
==============
This application is part of recruitment process. It's about making asynchronous chat. For creating this I used following things:

  - `python2.7` as main programming language.
  - `flask` as main web framework.
  - `mongoDB` as database.
  - `mongoengine` and `pymongo` for handle database.
  - `flask-SocketIO` for asynchronous communication.
  - `materializecss` main frontend css framework.
  - `knockoutjs` main js framework.

In `config.py` there is configuration for database connection.

Application was created and tested on Xubuntu 12.04.5 LTS. For testing purposes I used Chromium(version 37.0.2062.120) and firefox(33.0). 

### Screens
![Landingpage](https://raw.githubusercontent.com/Fajkowsky/LiveChat/master/static/img/screen_1.png)
![Chat screen](https://raw.githubusercontent.com/Fajkowsky/LiveChat/master/static/img/screen_2.png)

### Installation
Before installation this application need have python 2.7.X, pip, virtualenv in your operating system, after eventual installation you can perform below steps:

Create virtual enviromenmt:

    virtualenv -p python2.7 venv

Now you must activate virtual environment:

    source venv/bin/activate

Then you can install all libraries from requirements.txt:

    pip install -r requirements.txt
    
### Usage
To run application you must only type:

    python run.py
    
After that you can open web browser on this address:

    http://127.0.0.1:5000

### Testing

For testing purposes you will have to need account. For filling unique username and valid password in form on main site you create new account. 
 
Left side of communicator is for managing rooms and contacts. Right side is for messaging and status updates.
