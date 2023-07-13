from flask import Flask, redirect, render_template, url_for, request
app = Flask(__name__)

# @app.route("/")
# def home():
#     return redirect("/login")

# @app.route('/success/<name>')
# def success(name):
#     return 'welcome %s' % name


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         if(request.form['nm'] == None):
#             return render_template('login.html')
#         else:
#             user = request.form['nm']
#             return redirect(url_for('success',name=user))
#     else:
#         if(request.args.get('num') == None):
#             return render_template('login.html')
#         else:
#             user = request.args.get('nm')
#             return redirect(url_for('success', name=user))

@app.route('/', methods=['POST', 'GET'])
def root():
    return redirect('/home')

@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method=='POST':
        if request.form['user']!=None and request.form['user']!=None:
            user=request.form['user']
            return redirect(url_for('video',name=user))
        else:
            return render_template('home.html')
    return render_template('home.html')
    
@app.route('/<name>/video')
def video(name):
    return render_template('video.html',user=name)

if __name__ == '__main__':
    app.run(debug=True)
