# Literable

Literable is a web interface for your ebook collection. I built it because I wanted an easy way to browse and download books into iBooks, but it should work equally well for other use cases.

## Demo
[Click here to check out a demo of literable](http://literabledemo.dhwebco.com).

## Screenshot

![literable screenshot](/demo/screenshot.png "Oooh, pretty...")

## What about Calibre?

Calibre is great for desktop ebook management, but it's a kitchen-sink sort of application. It's huge and unwieldy, and good luck installing it on a headless server. It can be done, but it's not easy. literable is designed specifically to be a web front-end for your ebook collection.

## How do I install it?
At the moment, you can clone literable into a directory and run:

    pip install -r requirements.txt
    python manage.py migrate upgrade head
    python manage.py runserver

This will start literable on port 5000, and create an SQLite database in the literable directory.

To add a user, use the following command:

    python manage.py add_user username password

A better way is something like the following:

    mkdir instance
    cp literable/config.py instance/application.cfg
    
And change configuration settings as necessary to connect to a database, set the library path, etc. Then run the commands above.

## Deploying

literable is built on [Flask](http://flask.pocoo.org/), so any WSGI server will work. See the [Flask docs on deploying](http://flask.pocoo.org/docs/deploying/) for more information.

I am using [Gunicorn](http://gunicorn.org/), [nginx](http://nginx.org/en/), [Upstart](http://upstart.ubuntu.com/), and [gevent](http://www.gevent.org/) for running my literable library.
