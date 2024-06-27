# Introduction:

This research spec, upgrades our current Flask support to version 1.1.2. 

This spec assume, complete support for initial flask versions specs discussed [here](https://veracode.atlassian.net/wiki/spaces/RES/pages/10917674/Python+Research+Details). We also assume support for Jinja2 templating support discussed [here](https://veracode.atlassian.net/wiki/spaces/RES/pages/10918409/Jinja2+Normalizer+Specs).

# Taint Flow

Flask being a light weight web application framework, one of the most crucial security flaw would be XSS. Like any other classic templating support, we should be flagging these flaws directly in the template where the bug is located, as well as mitigation. 

This would be a 2 step process:

1. Mapping template files to a view function
2. Tainted Data accessible in template files

## Mapping Template files to view functions:

We should assume template files are stored under a dedicated folder called `templates`. All `template` files will be normalized thru the normalizer as per [Jinja2 specs](https://veracode.atlassian.net/wiki/spaces/RES/pages/10918409/Jinja2+Normalizer+Specs).

Different ways view functions can be mapping to template files, starting with most common:

1. Template file specified in `render_template` function as the first parameter:

```
@app.route('/login')
def login():
    return render_template("login.html") 
```

In above example, view function `login()`, accessed at endpoint `/login`, is mapped to template filie login.html.

2. Template files rendered thru functions or decorators

```
@app.route('/login-function')
def login3():
    return template_login('login4.html')

def template_login(template):
    return render_template(template)
```

Testcase: [simple_template_views](https://gitlab.laputa.veracode.io/research-roadmap/python-flask-1.1.2/blob/master/research_testcases/simple_template_views/auth.py)

## Tainted Data accessible in template files

Connecting data flow paths from view functions and templates files is going to be trickiest part but most essential in flagging XSS flaws.




### Tainted data flowing from view functions into template files:

Data can be passed explicitly as part of `render_template` function starting from 2nd parameter. 

**Note:**  Not all parameter passed to template file would be tainted.

```
View Function
=============

@app.route('/login-pojo')
def login2():
    creds  = credentials(request.args['username'],request.args['password'],'clean_data')
    return render_template('login2.html',creds=creds)

Corresponding Template file login2.html
=======================================

Username :  {{ creds['username'] | safe }} # CWEID 80
Password : {{ creds['password'] | safe}} # CWEID 80
Clean Data : {{ creds['clean_data'] | safe }} # FP CWEID 80, clean_data is not tainted from view    
    
```

### Framework objects available directly in the template files:
#### [request](https://flask.palletsprojects.com/en/1.1.x/api/?highlight=request#flask.request): 

Specified in [previous Flask specs](https://veracode.atlassian.net/wiki/spaces/RES/pages/10917674/Python+Research+Details) on how to access various tainted sources from request object. These can be access in template files as well.

```
Template file dealing with request object
=========================================
Username :  {{ request.args['username'] | safe }} # CWEID 80
Password : {{ request.args.get('password') | safe}} # CWEID 80
```

#### [session](https://flask.palletsprojects.com/en/1.1.x/api/?highlight=session#flask.session) and [g](https://flask.palletsprojects.com/en/1.1.x/api/?highlight=g#flask.g) objects 

These objects are available directly in template files. 

**Note:** Just like explicit parameter passing, session and g object data should be checked for taint before flagging. 

```

View function setting session object
=====================================
@app.route('/login-session-obj')
def login5():
    session["user_name"] = request.args['username'] # tainted data
    session['admin'] = 'admin' # clean data
    return render_template('login6.html')


Template file showing session data
===================================

Username :  {{ session['user_name'] | safe }} # CWEID 80
Admin : {{ session['admin'] | safe }} # FP CWEID 80, admin is not tainted

```


Testcase : [simple_template_views](https://gitlab.laputa.veracode.io/research-roadmap/python-flask-1.1.2/blob/master/research_testcases/simple_template_views/auth.py)



# Reference:
* https://flask.palletsprojects.com/en/1.1.x/
* [Python Non-Dataflow Scans](https://veracode.atlassian.net/wiki/spaces/RES/pages/10917669/Python+Non-Dataflow+Scans) - Specs `app.debug # CWEID 489` 
* [Initial Flask Research Specs](https://veracode.atlassian.net/wiki/spaces/RES/pages/10917674/Python+Research+Details) -- [Testcases](https://stash.veracode.local/users/bcreighton/repos/flasktest1/browse)


# ToDo:

 * blueprints
	 * url_map / add_url_rule
 * Templating 
	* flow from view to templates	
 	* template inheritance
 	* context-processor as prop
 	* custom filters ??
 	* macros ??
* class based views
* config object: DEBUG and SECRET_KEY properties, needs to be specc'ed/finely tuned. Cookbook, has a section on different ways for debug : https://learning.oreilly.com/library/view/flask-framework-cookbook/9781789951295/2a51d460-4db8-4772-8735-a30d1a6c14ca.xhtml


- Mapping templates to view files 
	- Template gets free access of request, session and g objects
	- Entry points thru Blueprints
	- template inheritance
	- macros, custom filters, context processor
- Class based views
- Template gets db_tainted objects thru model objects
- Config Object: DEBUG and SECRET_KEY



# Out of Scope:
- sqlalchemy
- Flask-WTF/WTForm extensions
- using bootstrap, react or any other js frameworks.
