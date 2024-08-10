from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://drajdeep.github.io"}})

DATABASE = 'ip_data.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ip_addresses';")
        if cursor.fetchone() is None:
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
        cursor = conn.execute('SELECT id, ip, type, country, region, city, latitude, longitude, tests_count FROM ip_addresses')
        results = cursor.fetchall()

    stats = [{
        'id': row[0], 'ip': row[1], 'type': row[2], 'country': row[3], 
        'region': row[4], 'city': row[5], 'latitude': row[6], 'longitude': row[7],
        'tests_count': row[8]
    } for row in results]

    return jsonify({
        'entries': stats,
        'total_tests': sum(row[8] for row in results),
        'ipv4_count': sum(1 for row in results if row[2] == 'IPv4'),
        'ipv6_count': sum(1 for row in results if row[2] == 'IPv6')
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
