# Flask-Static
Task manager similar to [gulp](URL) for the processing of static files.

## Working with Flask-Static
Setting up Flask-Static is quite easy. You only need to add:

```python
from flask.ext.static import Static

static = Static(app)
```

Adding tasks is controlled by a decorator:

```python
@static.task('coffee')
def coffee_task():
    src(r'static/coffee/.*\.coffee$')
        .pipe(coffee(bare=True))
        .pipe(dest(output='static/js/'))
```

The `src` function is provided as a global to the task function scope. The `coffee` and `dest` function are extensions also provided as globals.

As you can see, the workflow is similar to [gulp](URL). The path are currently being readed using regular expressions, in the future, wildcards will be suported.

## The `js` and `css` functions
Inspired by [Flask-Funnel](URL), the `js` and `css` function are provided to the application context in order to generate the corresponding links:

```html+jinja
<head>
    <!-- ... -->
    {{ css('less') }}
</head>
<body>
    <!-- ... -->
    {{ js('coffee', 'cjsx') }}
</body>
```

Each one receives multiple tasks names and generate the links to the compiled files.

## Extensions
Flask-Static comes shiped with two extensions, `coffee` and `dest`. The first executes `coffee` from the `PATH`. To add new extensions use the decorator provided with Flask-Static:

```python
from flask.ext.static.extensions import extension

@extension
def cjsx(filename, data):
    command = ['cjsx', '-c', '-s']
    bare = cjsx.settings.get('bare')
    if bare:
        command += ['-b']

    process = subprocess.Popen(command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = process.communicate(data)
    if process.returncode:
        return None, err
    else:
        dest = replaceExt(filename, '.js')
        return dest, out
```

Each extension must receive the file name and its content. The function must return the result file name and the new data. Returning the new file name as `None` will be interpreted as an error.

The variable `<function_name>.settings` holds a dictionary with the keywords provided in the extension initialization, for instance `cjsx(bare=True)`.
