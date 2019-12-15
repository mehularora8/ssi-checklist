from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checklist.db'
db = SQLAlchemy(app)

class checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return str(self.__dict__)

@app.route('/', methods = ['POST', 'GET'])
def index():
	if request.method == 'POST':
		task_name = request.form['task']
		new_task = checklist(content = task_name) 

		try:
			db.session.add(new_task)
			db.session.commit()
			return redirect('/')

		except:
			return "There was an internal issue adding the task"
		
	else: 
		tasks = checklist.query.order_by(checklist.date_created).all()
		return render_template('index.html', tasks = tasks)

@app.route('/delete/<int:id>')
def delete_task(id):
	task_to_delete = checklist.query.get_or_404(id)
	try:
		db.session.delete(task_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return "There was a problem deleting your task"

@app.route('/update/<int:id>', methods = ["GET", "POST"])
def update(id):
	task_to_edit = checklist.query.get_or_404(id)

	if request.method == 'POST':
		task_to_edit.content = request.form['task']

		try:
			db.session.commit()
			return redirect('/')

		except:
			return "There was an internal issue updating the task"

	else:
		return render_template('update.html', task = task_to_edit)

@app.route('/gethc')
def write():
	tasks = checklist.query.order_by(checklist.date_created).all()
	with open("checklist.txt", "w") as f:
		for task in tasks:
			f.write(task.__repr__())
			f.write('\n')

	f.close()
	return redirect('/')

if __name__ == "__main__":
	app.run(debug = True)
