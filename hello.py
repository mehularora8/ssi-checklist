from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class checklist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    assigned_to = db.Column(db.String(50), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    person_completing = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return str(self.__dict__)

@app.route('/', methods = ['POST', 'GET'])
def index():
	if request.method == 'POST':
		task_name = request.form['task']
		assigned_to = request.form['assigned']
		new_task = checklist(content = task_name, assigned_to = assigned_to) 

		try:
			db.session.add(new_task)
			db.session.commit()
			return redirect('/')
		except:
			return "Internal Failure"
		
	else: 
		tasks = checklist.query.all()
		return render_template('index.html', tasks = tasks)

@app.route('/complete/<int:id>')
def complete(id):
	task = checklist.query.get_or_404(id)
	return render_template('person_completing.html', task = task)

@app.route('/completing/<int:id>', methods = ["POST"])
def completing(id):
	task_to_complete = checklist.query.get_or_404(id)

	if request.method == 'POST':
		task_to_complete.person_completing = request.form['pc']
		task_to_complete.completed = True
		with open("completed.txt", "a") as f:
			f.write("Task: " + task_to_complete.content + ", Completed by: " + task_to_complete.person_completing + "\n")
		f.close()

		try: 
			db.session.commit()

		except:
			return "Internal error"
		
		return redirect('/')


	else:
		return render_template('person_completing.html', task = task_to_complete)


@app.route('/update/<int:id>', methods = ["GET", "POST"])
def update(id):
	task_to_edit = checklist.query.get_or_404(id)

	if request.method == 'POST':
		task_to_edit.content = request.form['task']
		task_to_edit.assigned_to = request.form['assigned']

		try:
			db.session.commit()
			return redirect('/')

		except:
			return "Internal error"

	else:
		return render_template('update.html', task = task_to_edit)

@app.route('/gethc')
def write():
	tasks = checklist.query.all()
	with open("checklist.txt", "w") as f:
		for task in tasks:
			f.write("Task: " + task.content + ", Assigned to: " + task.assigned_to)
			f.write('\n')

	f.close()
	return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
	task_to_delete = checklist.query.get_or_404(id)
	
	try:
		db.session.delete(task_to_delete)
		db.session.commit()
	except: 
		return "Internal error"

	return redirect('/')

@app.route('/clear')
def clear():
	tasks = checklist.query.all()
	for task in tasks:
		db.session.delete(task)
		db.session.commit()

	return redirect('/')

@app.route('/cleartxtfiles')
def cleartxtfiles():
	open("checklist.txt", "w").close()
	open("completed.txt", "w").close()
	return redirect('/clear')

if __name__ == "__main__":
	app.run(debug = True)
