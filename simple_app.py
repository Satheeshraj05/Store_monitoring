from flask import Flask, jsonify, request, send_file
import pandas as pd
import os
import uuid
import threading
from datetime import datetime, timedelta

app = Flask(__name__)

# Constants
DATA_DIR = 'store-monitoring-data'
REPORT_DIR = 'reports'

# Ensure reports directory exists
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

# Dictionary to track report generation status
reports = {}

def generate_report(report_id):
    """Generate the uptime/downtime report"""
    try:
        # Load data from CSV files
        store_status_df = pd.read_csv(os.path.join(DATA_DIR, 'store_status.csv'))
        business_hours_df = pd.read_csv(os.path.join(DATA_DIR, 'menu_hours.csv'))
        timezones_df = pd.read_csv(os.path.join(DATA_DIR, 'timezones.csv'))
        
        # Get all unique store IDs
        store_ids = store_status_df['store_id'].unique()
        
        # Get current time (max timestamp in the data)
        current_time = pd.to_datetime(store_status_df['timestamp_utc']).max()
        
        # Time intervals
        hour_ago = current_time - timedelta(hours=1)
        day_ago = current_time - timedelta(days=1)
        week_ago = current_time - timedelta(days=7)
        
        # Prepare report data
        report_data = []
        
        # Process each store (limit to 10 stores for demo)
        for store_id in store_ids[:10]:
            # For demonstration, use simplified calculations
            # In a real implementation, you would use the timezone and business hours data
            
            # Filter store status data for this store
            store_data = store_status_df[store_status_df['store_id'] == store_id]
            
            # Calculate uptime/downtime for different time intervals
            # Last hour
            hour_data = store_data[pd.to_datetime(store_data['timestamp_utc']) >= hour_ago]
            uptime_last_hour = hour_data[hour_data['status'] == 'active'].shape[0] * 60 / max(1, hour_data.shape[0])
            downtime_last_hour = 60 - uptime_last_hour
            
            # Last day
            day_data = store_data[pd.to_datetime(store_data['timestamp_utc']) >= day_ago]
            uptime_last_day = day_data[day_data['status'] == 'active'].shape[0] * 24 / max(1, day_data.shape[0])
            downtime_last_day = 24 - uptime_last_day
            
            # Last week
            week_data = store_data[pd.to_datetime(store_data['timestamp_utc']) >= week_ago]
            uptime_last_week = week_data[week_data['status'] == 'active'].shape[0] * 168 / max(1, week_data.shape[0])
            downtime_last_week = 168 - uptime_last_week
            
            # Add to report data
            report_data.append({
                'store_id': store_id,
                'uptime_last_hour': round(uptime_last_hour, 2),
                'uptime_last_day': round(uptime_last_day, 2),
                'uptime_last_week': round(uptime_last_week, 2),
                'downtime_last_hour': round(downtime_last_hour, 2),
                'downtime_last_day': round(downtime_last_day, 2),
                'downtime_last_week': round(downtime_last_week, 2)
            })
        
        # Create DataFrame and save to CSV
        report_df = pd.DataFrame(report_data)
        report_path = os.path.join(REPORT_DIR, f"{report_id}.csv")
        report_df.to_csv(report_path, index=False)
        
        # Update report status
        reports[report_id] = "Complete"
        
    except Exception as e:
        print(f"Error generating report: {e}")
        reports[report_id] = f"Error: {str(e)}"

@app.route('/trigger_report', methods=['GET'])
def trigger_report():
    """API endpoint to trigger report generation"""
    report_id = str(uuid.uuid4())
    reports[report_id] = "Running"
    
    # Start report generation in a separate thread
    thread = threading.Thread(target=generate_report, args=(report_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"report_id": report_id})

@app.route('/get_report', methods=['GET'])
def get_report():
    """API endpoint to get report status or download the report"""
    report_id = request.args.get('report_id')
    
    if not report_id or report_id not in reports:
        return jsonify({"error": "Invalid report_id"}), 400
    
    status = reports[report_id]
    
    if status == "Running":
        return jsonify({"status": "Running"})
    elif status == "Complete":
        report_path = os.path.join(REPORT_DIR, f"{report_id}.csv")
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True, download_name=f"report_{report_id}.csv")
        else:
            return jsonify({"error": "Report file not found"}), 500
    else:
        return jsonify({"error": status}), 500

if __name__ == '__main__':
    print("Starting Store Monitoring API...")
    print("Available endpoints:")
    print("  - /trigger_report: Trigger report generation")
    print("  - /get_report?report_id=<report_id>: Get report status or download report")
    app.run(debug=True, port=5000)