# Saleor

This is an extension for Saleor Project, aiming to improve the test inside the project

## Install with conda
```bash
conda create --name saleor python=3.5
source activate saleor

# Installing nodejs
conda install -c conda-forge nodejs 
# Installing postgres
# conda install -c anaconda postgresql 

# Installing extra requirements
conda install -c anaconda cffi 
conda install -c anaconda cairo
conda install -c conda-forge pango 
conda install -c conda-forge gdk-pixbuf 
conda install -c conda-forge libffi 
conda install -c conda-forge uwsgi 


# Installing pip requirements
pip install -r requirements.txt
```

As much as I like anaconda, somethings really need to be executed with other options, like docker in case for create postgres database and server
for multiplatform configurations

```bash
docker run \
    --name postgres \
    -e POSTGRES_PASSWORD=your_secret_password \
    -v ${PWD}/pgdata:/var/lib/postgresql/data \
    -p 5432:5432 \
    -d postgres:9.6.8-alpine

psql -h localhost -p 5432 -U postgres
# And type your_secret_password from the postgres run command
```

Then configure the database

```SQL
CREATE role saleor noinherit login password 'saleor_password';
CREATE DATABASE saleordb owner saleor;
ALTER USER saleor CREATEDB;
-- For testing purposes this user must be super user, to create and modify databases
ALTER USER saleor superuser;
-- to quit
\q
```

Now Saleor recommends to use a secret key, but the objective of this project is not about securing things, not at this level, therefore we define a default value for `SECRET_KEY` but you can have your own using

```bash
export SECRET_KEY='<mysecretkey>'
```

And also remember to add this variable on `.bashrc`, `.profile` or equivalent.

Now you're safe to migrate

```bash
python manage.py migrate
```

Now we have to build the front end, personally I hate projects merging front end and backend on a single repository, but seems to be a trend using
ReactJS with django, rendering JSX with django directly, don't know, just don't like

```bash
npm install
```

Also usually I recommend to use `npm audit fix` and that could be a static recommendation, but whatsoever

```bash
npm run build-assets
npm run build-emails
```

Now saleor should run smoothly

```bash
python manage.py runserver
```
