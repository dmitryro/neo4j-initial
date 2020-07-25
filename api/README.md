# lab-flask-swagger

[![Build Status](https://travis-ci.org/nyu-devops/lab-flask-swagger.svg?branch=master)](https://travis-ci.org/nyu-devops/lab-flask-swagger)
[![Codecov](https://img.shields.io/codecov/c/github/nyu-devops/lab-flask-swagger.svg)]()

**NYU DevOps** lab that demonstrates how to use [Flasgger](https://github.com/rochacbruno/flasgger) to generate [Swagger](http://swagger.io) documentation for your Python [Flask](http://flask.pocoo.org) application. This repository is part of lab for the NYU DevOps class  [CSCI-GA.3033-013](http://cs.nyu.edu/courses/spring17/CSCI-GA.3033-013/) for Spring 2017.

## Introduction

When developing microservices with API's that others are going to call, it is critically important to provide the proper API documentation. Swagger has become a defacto standard for documenting APIs. This lab shows you how to use a Flask plug-in called **Flasgger** to imbed Swagger documentatio into your Python Flask microservice so that the Swagger docs are generated for you.

I feel that it is much better to include the documentation with the code because programmers are more likely to update the docs if it's right there above the code they are working on. (...at least that's the therory and I'm sticking to it) ;-)

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/nyu-devops/ab-flask-tdd.git
    cd lab-flask-tdd
    vagrant up && vagrant ssh
    cd /vagrant

## Prerequisite Installation using Virtualenv

Since this lab has no database (it's just an in memory array) you can use **Virtualenv** to setup your Python environment instead of **Vagrant**.

**Note:** _If you are using a Mac, this will work right out-of-the-box becasue the Mac has everything you need to do software development right from Apple. If you are using Windows, you will need to install [Python 2.7](https://www.python.org/downloads/release/python-2712/) and `pip` first becasue Windows does not ship with any development tools. :( I strongly recommend that Windows users use the Vagrant approach above._

To use `virtualenv` follow these commands:

If you don't already have `virtualenv` you must install it at least once:

    pip install virtualenv

To create a virtual environment to run the code use the following:

    git clone https://github.com/nyu-devops/ab-flask-tdd.git
    cd lab-flask-tdd
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

That will install all of the required Python packages using `pip` into a virtual environment that isolates any library conflicts.

You can deactivate the virtual environment at any time with the command:

    deactivate

To `activate` the virtual envirnment again just change into the directory and use:

    source venv/bin/activate

If you ever run the server or the tests and you are getting an error that packages are not found, check to make sure that you have activated the virtual environment.

## Running the code

You can now run `nosetests` to run the tests and make sure that everything works as expected.

    nosetests
    coverage report -m

You can then run the server with:

    python server.py

Finally you can see the microservice at: [http://localhost:5000/](http://localhost:5000/)

The Swagger docs can be accessed at: [http://localhost:5000/apidocs/index.html](http://localhost:5000/apidocs/index.html)

The raw Swagger specification JSON can be found at: [http://localhost:5000/v1/spec](http://localhost:5000/v1/spec)

When you are done, you can exit and shut down the VM with:

    exit
    vagrant halt

If the VM is no longer needed you can remove it with:

    vagrant destroy


## What's featured in the project?

    * server.py -- the main Service using Python Flask and Swagger
    * test_server.py -- test cases using unittest for the microservice
    * test_pets.py -- test cases using unittest for the Pet model
