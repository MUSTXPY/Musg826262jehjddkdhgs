import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bots.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# نموذج قاعدة البيانات
class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Stopped")

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# الصفحة الرئيسية
@app.route('/')
def index():
    bots = Bot.query.all()
    return render_template('index.html', bots=bots)

# رفع الملفات
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "لم يتم اختيار ملف"
    
    file = request.files['file']
    if file.filename == '':
        return "اسم الملف فارغ"
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # إضافة للسجل
    new_bot = Bot(filename=filename)
    db.session.add(new_bot)
    db.session.commit()

    return redirect(url_for('index'))

# تشغيل البوت
@app.route('/start/<int:bot_id>')
def start_bot(bot_id):
    bot = Bot.query.get(bot_id)
    if bot:
        bot.status = "Running"
        db.session.commit()
        subprocess.Popen(["python", os.path.join(app.config['UPLOAD_FOLDER'], bot.filename)])
    return redirect(url_for('index'))

# إيقاف البوت (لن يعمل إلا إذا كان البوت داخل Docker مثلاً)
@app.route('/stop/<int:bot_id>')
def stop_bot(bot_id):
    bot = Bot.query.get(bot_id)
    if bot:
        bot.status = "Stopped"
        db.session.commit()
        # لا يمكن إيقاف العملية بسهولة بدون تتبع PID (تحسين مستقبلي)
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)