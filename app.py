from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_name = db.Column(db.String(100), nullable=False) 
    score = db.Column(db.Float, nullable=False) 

with app.app_context():
    db.create_all()

ALLOWED_SCORES = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
MEMBERS = ["คนที่ 1", "คนที่ 2", "คนที่ 3", "คนที่ 4", "คนที่ 5", "คนที่ 6", "คนที่ 7"]
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # วนลูปตามรายชื่อเพื่อนเพื่อดึงคะแนนที่ถูกส่งมาทีละคน
        for member in MEMBERS:
            score_str = request.form.get(member) # ดึงคะแนนโดยใช้ชื่อเพื่อนเป็น Key
            
            if score_str: # ถ้ามีการส่งคะแนนของคนนี้มา
                score = float(score_str)
                if score in ALLOWED_SCORES:
                    new_vote = Vote(target_name=member, score=score)
                    db.session.add(new_vote) # เตรียมบันทึก
        
        db.session.commit() # บันทึกคะแนนของทุกคนลงฐานข้อมูลพร้อมกัน
        return redirect(url_for('results'))
            
    return render_template('index.html', members=MEMBERS, allowed_scores=ALLOWED_SCORES)

@app.route('/results')
def results():
    avg_scores = db.session.query(
        Vote.target_name, 
        func.avg(Vote.score).label('average_score'),
        func.count(Vote.id).label('vote_count')
    ).group_by(Vote.target_name).all()
    
    return render_template('results.html', avg_scores=avg_scores)

if __name__ == '__main__':
    app.run(debug=True)