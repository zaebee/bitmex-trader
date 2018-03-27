# Bitmix trader
Bitmix strategy trade implementation

## How to get setup
0. run `sudo apt-get install postgresql-server-dev-9.5 redis-server binutils python3-dev`
1. run `sudo apt-get install gettext python3.5 python-setuptools python-pip python-virtualenv virtualenvwrapper`
2. run `echo source /usr/share/virtualenvwrapper/virtualenvwrapper.sh >> ~/.bashrc`
3. run `git clone -b develop https://github.com/alarstudios/whatwhere.git`
4. run `mkvirtualenv bitmex_rate -p /usr/bin/python3` (supports 3.4, 3.5, 3.6 versions or 2.7)
5. run `workon bitmex_rate`
6. run `cd bitmex_rate`
7. run `pip install -r requirements.txt`
8. Change `API_KEY/API_SECRET` in settings file with your values.
9. run `python manage.py migrate`
10. run `python manage.py createsuperuser`

### Frontend assets
    run `sudo apt-get install nodejs-dev npm`
    You need install `lessc` compilator `sudo npm install -g less`
    After that you can run `python manage.py collectstatic`

### Run developer server
`python manage.py runserver`

## How to run trader
`python manage.py runscript rent`

