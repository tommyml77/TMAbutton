from flask import Flask, render_template_string
import random
import os

app = Flask(__name__)

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
    <button id="colorButton" onclick="changeColor()">Change Color</button>

    <script>
        function changeColor() {
            fetch('/change_color')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('colorButton').style.backgroundColor = data.color;
                });
        }

        // Initialize the Telegram Mini App
        Telegram.WebApp.ready();
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

if __name__ == '__main__':
    # Запуск Flask приложения
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
