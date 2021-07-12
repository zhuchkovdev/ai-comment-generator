from flask import Flask, render_template, request
from model import DocstringGenerator

app = Flask(__name__)
comment_generator = DocstringGenerator()

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        code = request.form['code']
        if code:
            generated_comment = comment_generator.generate(code, 25)
            return render_template('index.html', comment=generated_comment)
        else:
            return render_template('index.html', error='Empty code input')
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
