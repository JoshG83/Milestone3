import os
from flask import Flask, render_template
import sass

## We need to import Flask and SASS in order for our web app to work.

app = Flask(__name__)

def compile_scss_if_needed():
    scss = os.path.join(app.root_path, 'static', 'css', 'formpage.scss')
    css = os.path.join(app.root_path, 'static', 'css', 'formpage.css')
    try:
        if not os.path.exists(css) or os.path.getmtime(scss) > os.path.getmtime(css):
            compiled = sass.compile(filename=scss, output_style='expanded')
            with open(css, 'w', encoding='utf-8') as f:
                f.write(compiled)
    except Exception as e:
        app.logger.error('SCSS compile error: %s', e)

@app.before_request
def maybe_compile_assets():
    # Only compile automatically in debug mode (development)
    if app.debug:
        compile_scss_if_needed()

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)