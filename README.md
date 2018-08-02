# Item Catalog - udacuty project 4

#### Description 
Application that allow to the user to create retrieve update delete (crud) movies from database and
 authentication app users by google auth

#### install
+ python3
+ virtual box 
+ vagrant
+ flask

#### google auth integration 
1. goto http://console.developers.google.com
2. Login 
3. click on ``Credentials`` tab
4. Create Crendentials
5. Select `` OAuth client id``
6. Add project url ``http://127.0.0.1:5000`` and redirecturl is ``http://127.0.0.1:5000/oauth2callback``
7. Create your web app
8. Copy client id and client seceret to line 19 and 20 on ``app.py`` folder

#### How to run ?
-from the command line excute :
1. Install Vagrant and VirtualBox
2. Clone the fullstack-nanodegree-vm : https://github.com/udacity/fullstack-nanodegree-vm
3. clone the project file into ``fullstack-nanodegree-vm/vagrant/catalog``
4. open cli at project directory
4. ``vagrant up`` to launch your VM
5. ``vagrant ssh`` to login 
6. ``cd /vagrant/catalog`` to open shared folder
7. run ``sudo pip install -r requirements``
7. ``python app.py`` to excute the program
8. app run at http://127.0.0.1:5000

### Notes
Add category form it's only for seeding the project
