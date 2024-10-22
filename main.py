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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Telegram Calendar App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1c1c1c;
            color: white;
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
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
            background-size: cover;
            background-position: center;
        }
        .month-year {
            flex-grow: 1;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
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
            padding: 10px;
            background-color: #2a2a2a;
            overflow-x: auto;
        }
        .day {
            flex: 0 0 auto;
            text-align: center;
            padding: 5px;
            font-size: 12px;
            font-weight: bold;
            position: relative;
        }
        .day.past {
            color: #777;
        }
        .day::after {
            content: '';
            position: absolute;
            right: -5px;
            height: 100%;
            width: 1px;
            background-color: transparent;
        }
        .day.selected, .day.current {
            background-color: #0088cc;
            border-radius: 5px;
            color: white;
        }
        .events-container {
            padding: 10px;
            height: calc(100% - 240px);
            overflow-y: auto;
        }
        .event {
            display: flex;
            align-items: center;
            background-color: #333;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .event .event-date {
            font-weight: bold;
            color: #0088cc;
            font-size: 12px;
            margin-right: 15px;
            min-width: 50px;
            text-align: left;
        }
        .event .event-description {
            flex-grow: 1;
            font-size: 14px;
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
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="avatar" id="userAvatar"></div>
        <div class="month-year" id="monthYear" onclick="openMonthPicker()">October 2024</div>
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
                document.getElementById('userAvatar').style.backgroundImage = `url('https://ui-avatars.com/api/?name=${userData.username}&background=random')`;
                document.getElementById('userAvatar').style.backgroundSize = 'cover';
                document.getElementById('userAvatar').style.backgroundPosition = 'center';
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
            const today = new Date();
            highlightCurrentDay(today);
        }

        function addNewEvent() {
            alert("Adding a new event!");
        }

        function loadWeekDays() {
            const weekDaysContainer = document.getElementById('weekDays');
            const today = new Date();
            const startDate = new Date(2024, 0, 1);
            const endDate = new Date(2033, 11, 31);
            let currentDate = new Date(startDate);

            while (currentDate <= endDate) {
                const dayElement = document.createElement('div');
                dayElement.className = 'day';
                dayElement.innerHTML = `<div>${currentDate.getDate()}</div><div>${currentDate.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()}</div>`;
                if (currentDate < today) {
                    dayElement.classList.add('past');
                }
                if (currentDate.toDateString() === today.toDateString()) {
                    dayElement.classList.add('current');
                }
                weekDaysContainer.appendChild(dayElement);
                currentDate.setDate(currentDate.getDate() + 1);
            }
        }

        function openMonthPicker() {
            Telegram.WebApp.showPopup({
                title: "Choose Month and Year",
                message: "Scroll to choose the desired month and year.",
                buttons: [
                    { id: "month", type: "select", options: [
                        { text: "January", value: "0" },
                        { text: "February", value: "1" },
                        { text: "March", value: "2" },
                        { text: "April", value: "3" },
                        { text: "May", value: "4" },
                        { text: "June", value: "5" },
                        { text: "July", value: "6" },
                        { text: "August", value: "7" },
                        { text: "September", value: "8" },
                        { text: "October", value: "9" },
                        { text: "November", value: "10" },
                        { text: "December", value: "11" }
                    ]},
                    { id: "year", type: "select", options: [
                        { text: "2024", value: "2024" },
                        { text: "2025", value: "2025" },
                        { text: "2026", value: "2026" },
                        { text: "2027", value: "2027" },
                        { text: "2028", value: "2028" },
                        { text: "2029", value: "2029" },
                        { text: "2030", value: "2030" },
                        { text: "2031", value: "2031" },
                        { text: "2032", value: "2032" },
                        { text: "2033", value: "2033" }
                    ]},
                    { id: "confirm", text: "Apply" }
                ],
                onResult: function(buttonId, result) {
                    if (buttonId === "confirm") {
                        const selectedMonth = parseInt(result.month);
                        const selectedYear = parseInt(result.year);
                        const selectedDate = new Date(selectedYear, selectedMonth, 1);
                        document.getElementById('monthYear').innerText = `${selectedDate.toLocaleString('en-US', { month: 'long' })} ${selectedYear}`;
                        document.getElementById('weekDays').innerHTML = '';
                        loadWeekDaysFrom(selectedDate);
                    }
                }
            });
        }

        function loadWeekDaysFrom(startDate) {
            const weekDaysContainer = document.getElementById('weekDays');
            const endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0);
            let currentDate = new Date(startDate);

            while (currentDate <= endDate) {
                const dayElement = document.createElement('div');
                dayElement.className = 'day';
                dayElement.innerHTML = `<div>${currentDate.getDate()}</div><div>${currentDate.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()}</div>`;
                if (currentDate < new Date()) {
                    dayElement.classList.add('past');
                }
                if (currentDate.toDateString() === new Date().toDateString()) {
                    dayElement.classList.add('current');
                }
                weekDaysContainer.appendChild(dayElement);
                currentDate.setDate(currentDate.getDate() + 1);
            }
        }

        function highlightCurrentDay(date) {
            const weekDaysContainer = document.getElementById('weekDays');
            Array.from(weekDaysContainer.children).forEach(dayElement => {
                const day = parseInt(dayElement.firstChild.textContent, 10);
                if (day === date.getDate() && dayElement.classList.contains('current')) {
                    dayElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        }

        Telegram.WebApp.ready();
        Telegram.WebApp.expand();
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
