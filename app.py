from flask import Flask, render_template, request
from model import DocstringGenerator

app = Flask(__name__)
comment_generator = DocstringGenerator()

GENERATED_COMMENT_SIZE = 200
LINE_BREAK_WORDS = ['Returns:', 'Args:', 'Parameters:', 'Returns -', 'Args -', 'Parameters -']

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        code = request.form['code']
        if code:
            generated_comment = comment_generator.generate(code, GENERATED_COMMENT_SIZE)
            for item in LINE_BREAK_WORDS:
                generated_comment = generated_comment.replace(item, '\n' + item)
            return render_template('index.html', comment=generated_comment)
        else:
            return render_template('index.html', error='Empty code input')
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
