# Items Catalog

## About
This is the fourth project in Udacity Full-Stack Developer Nanodegree.  In this project, a python module is written using Flask framework to get a list of categories from SQLite database and present it in a web interface. Users can login using their Google+ accounts and add new items to category, update or delete the items that they have created. The pages that allow CRUD operations are protected so that only authenticated and authorized users can access and perform changes.

## Technologies used
1. Python
2. Virtual Machine
3. Flask framework
4. HTML and CSS
5. SQLite database

## Prerequisites
1. Python version 2 and above
2. Vagrant 
3. Virtual Machine

## Installation
1. Install Vagrant and VM
2. Download [fullstack-nanodegree-vm]( https://github.com/udacity/fullstack-nanodegree-vm)
4. Fork this repository or download this project and place it inside the "vagrant/catalog" directory. SQlite is already installed in the virtual machine

## To Execute
1. Open terminal and navigate to the directory where you have placed vagrant and execute "vagrant up"
2. Log in using "vagrant ssh"
3. Change into directory /vagrant/catalog
4. Execute "python application.py"
5. Open a browser and go to "localhost:5000/"

## To use the application
1. List of catgeories will be provided. Users can click on a category to view the items in that category and click on each item and view the description without logging in. Only read access is provided
2. Inorder to add new items users have to login with Google+ account
3. Once logged in, add new items option will be provided
4. Clicking on the item that the user has created will further give the options to either edit or delete the item. These options will not be provided for other users who are not authorised
5. Clicking on the logout button will logout the user from the application

## JSON endpoints
1. To get the JSON data from the application, go to 
localhost:5000/catalog.json





