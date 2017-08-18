from flask import Flask, render_template
import tempInversion2
app = Flask(__name__)

@app.route('/')
def homepage():
	results = tempInversion2.main()
	return render_template('index2.html', results=results)

if __name__ == '__main__':
	app.run()
