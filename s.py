from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://drajdeep.github.io"}})

DATABASE = 'ip_data.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ip_addresses (
                id INTEGER PRIMARY KEY, 
                ip TEXT, 
                type TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                tests_count INTEGER DEFAULT 1
            )
        ''')
    conn.close()

@app.route('/save-ip', methods=['POST'])
def save_ip():
    data = request.json
    ip = data['ip']
    ip_type = data['type']
    location = data['location']  # Extract location data

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM ip_addresses WHERE ip = ?', (ip,))
        existing_entry = cursor.fetchone()

        if existing_entry is None:
            conn.execute('''
                INSERT INTO ip_addresses (ip, type, country, region, city, latitude, longitude, tests_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ip, ip_type, location['country_name'], location['state_prov'], location['city'], 
                  location['latitude'], location['longitude'], 1))
        else:
            conn.execute('UPDATE ip_addresses SET tests_count = tests_count + 1 WHERE ip = ?', (ip,))
        conn.commit()

    return jsonify({'status': 'success'})

@app.route('/stats', methods=['GET'])
def get_stats():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT ip, type, country, region, city, latitude, longitude FROM ip_addresses')
        results = cursor.fetchall()
    stats = [{'ip': row[0], 'type': row[1], 'country': row[2], 'region': row[3], 'city': row[4], 
              'latitude': row[5], 'longitude': row[6]} for row in results]
    return jsonify(stats)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
