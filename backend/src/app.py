from flask import Flask, render_template

app = Flask(__name__,
            static_folder = "../../dist/static",
            template_folder = "../../dist")

@app.route('/api/')

@app.route('/')
def index():
    return render_template("index.html")