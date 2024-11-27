# File: main.py

from flask import Flask, render_template_string, request
import random
import os
import threading
import json

app = Flask(__name__)

# Сохранение данных пользователей
user_data = {}

event_form_template = '''
<div class="event-form">
    <div class="form-group">
        <label for="eventName">Название события</label>
        <input type="text" id="eventName" placeholder="Введите название события">
    </div>
    <div class="form-group">
        <label for="eventStartDate">Начало</label>
        <input type="date" id="eventStartDate">
        <input type="time" id="eventStartTime">
    </div>
    <div class="form-group">
        <label for="eventEndDate">Конец</label>
        <input type="date" id="eventEndDate">
        <input type="time" id="eventEndTime">
    </div>
    <div class="form-group">
        <label for="eventRepeat">Повтор</label>
        <select id="eventRepeat">
            <option value="none">Не повторять</option>
            <option value="daily">Ежедневно</option>
            <option value="weekly">Еженедельно</option>
            <option value="monthly">Ежемесячно</option>
        </select>
    </div>
    <div class="form-group">
        <label for="eventReminder">Напоминание</label>
        <select id="eventReminder">
            <option value="15">За 15 минут</option>
            <option value="30">За 30 минут</option>
            <option value="60">За 60 минут</option>
        </select>
    </div>
    <div class="form-group">
        <label for="eventInvite">Приглашение участников</label>
        <input type="text" id="eventInvite" placeholder="Введите участников">
    </div>
    <div class="form-group">
        <label for="eventLocation">Локация или ссылка на звонок</label>
        <input type="text" id="eventLocation" placeholder="Введите локацию или ссылку на звонок">
    </div>
    <div class="form-group">
        <label for="eventDescription">Описание</label>
        <textarea id="eventDescription" placeholder="Введите описание"></textarea>
    </div>
    <button class="save-event-button" onclick="saveEvent()">Добавить событие</button>
</div>
'''

calendar_template = '''
<div class="week-days" id="weekDays">
    <!-- Дни недели будут добавлены динамически -->
</div>
<div class="events-container" id="eventsContainer">
    <!-- События будут добавлены динамически -->
</div>
<button class="new-event-button" onclick="openEventForm()">Добавить событие</button>
'''

games_template = '''
<div style="text-align: center; margin-top: 20px;">Coming soon...</div>
'''

settings_template = '''
<div style="text-align: center; margin-top: 20px;">Coming soon...</div>
'''

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
            scroll-snap-type: x mandatory;
            scrollbar-width: none; /* Hide scrollbar for Firefox */
        }
        .week-days::-webkit-scrollbar {
            display: none; /* Hide scrollbar for Chrome, Safari, Opera */
        }
        .day {
            flex: 0 0 calc(100% / 7);
            text-align: center;
            padding: 5px;
            font-size: 12px;
            font-weight: bold;
            position: relative;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            scroll-snap-align: center;
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
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
        }
        .tabs {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #333;
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
        }
        .tab {
            flex-grow: 1;
            text-align: center;
            color: white;
            cursor: pointer;
        }
        .tab.active {
            background-color: #0088cc;
        }
        .tab-icon {
            font-size: 24px;
            display: block;
        }
        .week-divider {
            border-left: 1px solid #555;
            margin-left: -1px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: none;
            box-sizing: border-box;
        }
        .save-event-button {
            background-color: #0088cc;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="avatar" id="userAvatar"></div>
        <div class="month-year" id="monthYear" onclick="openMonthPicker()">October 2024</div>
        <button class="today-button" onclick="goToToday()">📅</button>
    </div>

    <div id="contentContainer">
        <!-- Контент вкладок будет добавлен динамически -->
    </div>

    <div class="tabs">
        <div class="tab" id="calendarTab" onclick="openTab('calendar')">
            <span class="tab-icon">📅</span>
            Calendar
        </div>
        <div class="tab" id="gamesTab" onclick="openTab('games')">
            <span class="tab-icon">🎮</span>
            Games
        </div>
        <div class="tab" id="settingsTab" onclick="openTab('settings')">
            <span class="tab-icon">⚙️</span>
            Settings
        </div>
    </div>

    <script>
        function getUserDataFromUrl() {
            const params = new URLSearchParams(window.location.search);
            const userId = params.get('id');
            const firstName = params.get('first_name');
            const lastName = params.get('last_name');
            const username = params.get('username');
            const languageCode = params.get('language_code');
            const avatarUrl = params.get('avatar');
            console.log('Extracted user data from URL:', {
                userId, firstName, lastName, username, languageCode, avatarUrl
            });
            return {
                id: userId,
                first_name: firstName,
                last_name: lastName,
                username: username,
                language_code: languageCode,
                avatar: avatarUrl
            };
        }

        function initApp() {
            const userData = getUserDataFromUrl();
            if (userData.avatar) {
                document.getElementById('userAvatar').style.backgroundImage = `url(${userData.avatar})`;
            } else if (userData.username) {
                document.getElementById('userAvatar').style.backgroundImage = `url('https://ui-avatars.com/api/?name=${userData.username}&background=random')`;
            }
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
        }

        function goToToday() {
            const today = new Date();
            highlightCurrentWeek(today);
        }

        function openMonthPicker() {
            Telegram.WebApp.showDatePicker({
                title: "Choose Month and Year",
                min_date: new Date(2024, 0, 1).toISOString(),
                max_date: new Date(2033, 11, 31).toISOString(),
                on_result: function(date) {
                    const selectedDate = new Date(date);
                    const selectedMonth = selectedDate.getMonth();
                    const selectedYear = selectedDate.getFullYear();
                    document.getElementById('monthYear').innerText = `${selectedDate.toLocaleString('en-US', { month: 'long' })} ${selectedYear}`;
                    document.getElementById('weekDays').innerHTML = '';
                    loadWeekDaysFrom(selectedDate);
                }
            });
        }

        function openTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + 'Tab').classList.add('active');

            const contentContainer = document.getElementById('contentContainer');
            const headerElements = document.querySelectorAll('.month-year, .today-button');

            if (tabName === 'calendar') {
                contentContainer.innerHTML = `{{ calendar_template | safe }}`;
                headerElements.forEach(el => el.style.display = 'block');
                loadWeekDays();
            } else if (tabName === 'games') {
                contentContainer.innerHTML = `{{ games_template | safe }}`;
                headerElements.forEach(el => el.style.display = 'none');
            } else if (tabName === 'settings') {
                contentContainer.innerHTML = `{{ settings_template | safe }}`;
                headerElements.forEach(el => el.style.display = 'none');
            }
        }

        function loadWeekDays() {
            const weekDaysContainer = document.getElementById('weekDays');
            const today = new Date();
            const startDate = new Date(2024, 0, 1);
            const endDate = new Date(2033, 11, 31);
            let currentDate = new Date(startDate);

            let weekCounter = 0;
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

                if (currentDate.getDay() === 1 && weekCounter > 0) {
                    dayElement.classList.add('week-divider');
                }

                weekDaysContainer.appendChild(dayElement);
                currentDate.setDate(currentDate.getDate() + 1);
                weekCounter++;
            }
            // Прокрутка к текущей неделе
            document.querySelector('.current').scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' });
        }

        function highlightCurrentWeek(startDate) {
            const weekDaysContainer = document.getElementById('weekDays');
            const days = weekDaysContainer.getElementsByClassName('day');
            for (let i = 0; i < days.length; i++) {
                const day = days[i];
                const currentDate = new Date(startDate);
                currentDate.setDate(currentDate.getDate() + (i % 7));

                if (i % 7 === 0) {
                    // Начало новой недели
                    day.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' });
                }
            }
        }

        function openEventForm() {
            const contentContainer = document.getElementById('contentContainer');
            contentContainer.innerHTML = `{{ event_form_template | safe }}`;
        }

        document.querySelector('.week-days').addEventListener('wheel', function(evt) {
            evt.preventDefault();
            this.scrollLeft += evt.deltaY;
        });

        Telegram.WebApp.ready();
        Telegram.WebApp.expand();
        initApp();
        openTab('calendar');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template, calendar_template=calendar_template, games_template=games_template, settings_template=settings_template, event_form_template=event_form_template)

@app.route('/change_color')
def change_color():
    random_color = "#%06x" % random.randint(0, 0xFFFFFF)
    return {"color": random_color}

@app.route('/save_user_data', methods=['POST'])
def save_user_data():
    try:
        data = request.get_json()
        user_id = data.get('id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        language_code = data.get('language_code')
        avatar = data.get('avatar')
        if user_id:
            user_data[user_id] = {
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'language_code': language_code,
                'avatar': avatar
            }
            print(f"Received user data: {user_data[user_id]}")  # Отладочный вывод
            return {"status": "success"}, 200
        else:
            print("User ID not provided in the request.")  # Отладочный вывод
            return {"status": "error", "message": "User ID not provided"}, 400
    except Exception as e:
        print(f"Error processing user data: {e}")  # Отладочный вывод
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
