import os
import requests

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)


def create_tables():
    Service.query.delete()
    if not Service.query.first():
        services = [
            Service(title='Коррекция сколов/царапин', description='Тестовое описание', price=1000),
            Service(title='Чернение резины и пластика', description='', price=500),
            Service(title='Очистка кузова авто', description='', price=1000),
            Service(title='Химическая полировка фар', description='', price=1500),
            Service(title='Химчистка салона авто', description='', price=4000),
            Service(title='Нанесение защитных покрытий', description='', price=4000),
            Service(title='Удаление/полировка притертостей', description='', price=1000),
            Service(title='Полировка фар', description='', price=1000),
            Service(title='Полировка авто', description='', price=6000),
        ]
        db.session.bulk_save_objects(services)
        db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/services')
def services():
    all_services = Service.query.all()
    return render_template('services.html', services=all_services)


@app.route('/promo')
def promo():
    return render_template('promo.html')


@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Получаем данные из формы
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        service = data.get('service')
        comment = data.get('comment', '')
        
        # Валидация данных
        if not name or not phone or not service:
            return jsonify({
                'status': 'error',
                'message': 'Пожалуйста, заполните все обязательные поля'
            }), 400

        # Отправляем уведомление в Telegram
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if telegram_bot_token and telegram_chat_id:
            message = (
                "📬 *Новая заявка с сайта!*\n\n"
                f"*Имя:* {name}\n"
                f"*Телефон:* `{phone}`\n"
                f"*Услуга:* {service}\n"
                f"*Комментарий:* {comment if comment else 'Нет комментария'}"
            )
            
            url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                app.logger.error(f"Ошибка отправки в Telegram: {response.text}")
        
        return jsonify({
            'status': 'success',
            'message': 'Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.'
        })
    
    except Exception as e:
        app.logger.error(f"Ошибка обработки формы: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Произошла ошибка при обработке вашей заявки. Пожалуйста, попробуйте позже.'
        }), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_tables()

    app.run(debug=True)
