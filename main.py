# File: main.py

from flask import Flask, render_template_string, request
import random
import os
import threading
import json

app = Flask(__name__)

# Сохранение данных пользователей
user_data = {}

html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Telegram Mini App</title>
    <style>
        #colorButton {
            width: 200px;
            height: 50px;
            font-size: 20px;
            background-color: #0088cc;
            color: white;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h3>Welcome to your personal calendar!</h3>
    <p id="userInfo"></p>
    <button id="colorButton" onclick="changeColor()">Change Color</button>

    <script>
        function changeColor() {
            fetch('/change_color')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('colorButton').style.backgroundColor = data.color;
                });
        }

        // Получение информации о пользователе из URL
        function getUserDataFromUrl() {
            const params = new URLSearchParams(window.location.search);
            const username = params.get('username');
            console.log('Extracted username from URL:', username);
            return {
                username: username
            };
        }

        // Инициализация приложения и передача данных о пользователе на сервер
        function initApp() {
            const userData = getUserDataFromUrl();
            if (userData.username) {
                document.getElementById('userInfo').innerText = `Username: ${userData.username}
Date: ${new Date().toLocaleDateString()}`;
                // Отправка данных на сервер
                fetch('/save_user_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                }).then(response => response.json()).then(data => {
                    console.log('Server response:', data);
                }).catch(error => {
                    console.error('Error sending user data:', error);
                });
            } else {
                document.getElementById('userInfo').innerText = 'No username provided in URL.';
            }
        }

        // Initialize the Telegram Mini App
        Telegram.WebApp.ready();
        initApp();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/change_color')
def change_color():
    random_color = "#%06x" % random.randint(0, 0xFFFFFF)
    return {"color": random_color}

@app.route('/save_user_data', methods=['POST'])
def save_user_data():
    try:
        data = request.get_json()
        username = data.get('username')
        if username:
            user_data[username] = {
                'username': username
            }
            print(f"Received user data: {user_data[username]}")  # Отладочный вывод
            return {"status": "success"}, 200
        else:
            print("Username not provided in the request.")  # Отладочный вывод
            return {"status": "error", "message": "Username not provided"}, 400
    except Exception as e:
        print(f"Error processing user data: {e}")  # Отладочный вывод
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
