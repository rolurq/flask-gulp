# Flask-Gulp
Task manager similar to [gulp](URL) for the processing of static files.

## Working with Flask-Gulp
Setting up Flask-Gulp is quite easy. Here is an example:

```python
from flask.ext.gulp import Static

static = Static(app)
```

This allows to add tasks with the `task` decorator:

```python
@static.task('coffee')
def coffee_task():
    src(r'static/coffee/**/*.coffee')\
        .pipe(coffee(bare=True))\
        .pipe(dest(output='static/js/'))
```

The `src` function is provided as a global to the task function scope along with all the extensions.

As you can see, the workflow is similar to [gulp](URL).

## The `js` and `css` functions
Inspired by [Flask-Funnel](URL), the `js` and `css` functions are provided to the application context in order to generate the corresponding links:

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

Each one receives multiple tasks names and generate the links to the generated files.

## Extensions
Flask-Gulp comes shiped with four extensions, `coffee`, `cjsx`, `less` and `dest`. The first ones accept an `executable` setting, which holds the corresponding binary location, the default is to call it directly.

To add new extensions use the decorator provided with Flask-Gulp:

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
