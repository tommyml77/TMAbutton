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
    <title>Telegram Calendar App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1c1c1c;
            color: white;
            margin: 0;
            padding: 0;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #333;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #888;
            margin-right: 10px;
        }
        .month-year {
            flex-grow: 1;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }
        .today-button {
            width: 40px;
            height: 40px;
            background-color: #555;
            border-radius: 50%;
            border: none;
            cursor: pointer;
        }
        .week-days {
            display: flex;
            overflow-x: auto;
            padding: 10px;
            background-color: #2a2a2a;
        }
        .day {
            flex: 0 0 auto;
            width: 50px;
            text-align: center;
            margin-right: 10px;
            padding: 5px;
        }
        .day.selected {
            background-color: #0088cc;
            border-radius: 5px;
        }
        .events-container {
            padding: 10px;
        }
        .event {
            background-color: #333;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .new-event-button {
            display: block;
            width: 90%;
            margin: 20px auto;
            padding: 15px;
            background-color: #0088cc;
            color: white;
            text-align: center;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="avatar" id="userAvatar"></div>
        <div class="month-year" id="monthYear">October 2024</div>
        <button class="today-button" onclick="goToToday()">🔄</button>
    </div>

    <div class="week-days" id="weekDays">
        <!-- Дни недели будут добавлены динамически -->
    </div>

    <div class="events-container" id="eventsContainer">
        <!-- События будут добавлены динамически -->
    </div>

    <div class="new-event-button" onclick="addNewEvent()">New Event</div>

    <script>
        function getUserDataFromUrl() {
            const params = new URLSearchParams(window.location.search);
            const username = params.get('username');
            console.log('Extracted username from URL:', username);
            return {
                username: username
            };
        }

        function initApp() {
            const userData = getUserDataFromUrl();
            if (userData.username) {
                // Здесь можно добавить логику для получения аватара, если он доступен
                document.getElementById('userAvatar').style.backgroundImage = `url('https://via.placeholder.com/40')`;
                document.getElementById('userAvatar').style.backgroundSize = 'cover';
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
                document.getElementById('monthYear').innerText = 'No username provided in URL.';
            }
        }

        function goToToday() {
            alert("Navigating to today's date!");
        }

        function addNewEvent() {
            alert("Adding a new event!");
        }

        function loadWeekDays() {
            const weekDaysContainer = document.getElementById('weekDays');
            const today = new Date();
            for (let i = -3; i <= 3; i++) {
                const date = new Date();
                date.setDate(today.getDate() + i);
                const dayElement = document.createElement('div');
                dayElement.className = 'day' + (i === 0 ? ' selected' : '');
                dayElement.innerHTML = `<div>${date.getDate()}</div><div>${date.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()}</div>`;
                weekDaysContainer.appendChild(dayElement);
            }
        }

        function loadEvents() {
            const eventsContainer = document.getElementById('eventsContainer');
            for (let i = 0; i < 7; i++) {
                const eventElement = document.createElement('div');
                eventElement.className = 'event';
                eventElement.innerText = 'No events';
                eventsContainer.appendChild(eventElement);
            }
        }

        Telegram.WebApp.ready();
        initApp();
        loadWeekDays();
        loadEvents();
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
