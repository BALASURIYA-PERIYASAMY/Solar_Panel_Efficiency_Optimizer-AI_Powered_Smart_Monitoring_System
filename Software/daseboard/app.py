from flask import Flask, render_template, jsonify, request
import mysql.connector
from datetime import datetime
import json

app = Flask(__name__, template_folder='templates')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="solar_optimizer"
    )

@app.route('/')
def index():
    """Main dashboard route"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch the latest record
        cursor.execute("SELECT * FROM sensor_logs ORDER BY id DESC LIMIT 1")
        latest_data = cursor.fetchone()
        
        # Fetch statistics
        cursor.execute("""
            SELECT 
                AVG(actual_power) as avg_power,
                MAX(actual_power) as max_power,
                MIN(actual_power) as min_power,
                AVG(temperature) as avg_temp,
                MAX(temperature) as max_temp,
                AVG(dust_level) as avg_dust,
                COUNT(*) as total_records
            FROM sensor_logs
        """)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return render_template('dashboard.html', latest=latest_data, stats=stats)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', latest=None, stats=None)

@app.route('/api/hourly-data')
def get_hourly_data():
    """API endpoint for hourly aggregated data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE_FORMAT(timestamp, '%H:00') as hour,
                AVG(actual_power) as actual_power,
                AVG(predicted_power) as predicted_power,
                AVG(temperature) as temperature,
                AVG(dust_level) as dust_level,
                COUNT(*) as records
            FROM sensor_logs
            GROUP BY DATE_FORMAT(timestamp, '%H:00')
            ORDER BY hour
            LIMIT 24
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/latest')
def get_latest():
    """API endpoint for latest sensor reading"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM sensor_logs ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """API endpoint for aggregated statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                AVG(actual_power) as avg_actual_power,
                MAX(actual_power) as max_actual_power,
                MIN(actual_power) as min_actual_power,
                AVG(predicted_power) as avg_predicted_power,
                AVG(efficiency_gap) as avg_efficiency_gap,
                AVG(temperature) as avg_temperature,
                MAX(temperature) as max_temperature,
                AVG(dust_level) as avg_dust_level,
                MAX(dust_level) as max_dust_level
            FROM sensor_logs
        """)
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health')
def get_health():
    """API endpoint for system health status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM sensor_logs ORDER BY id DESC LIMIT 1")
        latest = cursor.fetchone()
        
        # Determine health status
        if latest['efficiency_gap'] > 2:
            status = 'CRITICAL'
            message = 'High efficiency gap detected. Panel cleaning required.'
        elif latest['efficiency_gap'] > 1:
            status = 'WARNING'
            message = 'Moderate efficiency gap. Check environmental conditions.'
        elif latest['dust_level'] > 0.4:
            status = 'WARNING'
            message = 'High dust accumulation detected.'
        else:
            status = 'HEALTHY'
            message = 'System operating optimally.'
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'system_status': status,
            'message': message,
            'latest': latest
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/performance-history')
def get_performance_history():
    """API endpoint for real-time performance history (AI prediction vs actual power)"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(f"""
            SELECT 
                timestamp,
                predicted_power,
                actual_power
            FROM sensor_logs
            ORDER BY id DESC
            LIMIT {limit}
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'history': data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_status')
def get_status():
    """API endpoint for pump control based on efficiency gap threshold"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT efficiency_gap FROM sensor_logs ORDER BY id DESC LIMIT 1")
        latest = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # If gap is more than 1.5 Watts, send "1" (Turn on Pump), else "0"
        if latest and latest['efficiency_gap'] > 1.5:
            return "1" 
        return "0"
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔆 AI SOLAR PANEL DASHBOARD SERVER")
    print("="*70)
    print("\n📊 Dashboard: http://localhost:5000")
    print("📈 API Endpoints:")
    print("   - http://localhost:5000/api/latest")
    print("   - http://localhost:5000/api/hourly-data")
    print("   - http://localhost:5000/api/statistics")
    print("   - http://localhost:5000/api/health")
    print("   - http://localhost:5000/api/performance-history")
    print("   - http://localhost:5000/get_status (Pump Control)")
    print("\n✅ Server starting... (Press Ctrl+C to stop)")
    print("="*70 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)