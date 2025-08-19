# Store Monitoring System

This application monitors restaurant uptime/downtime and generates reports based on store status data.

## Features

- Import store status, business hours, and timezone data from CSV files
- Generate reports on store uptime/downtime for different time intervals
- RESTful API endpoints for triggering and retrieving reports
- Background processing for report generation

## Requirements

- Python 3.7+
- Flask
- Pandas
- SQLAlchemy
- PyTZ
- Celery (for background tasks)
- Redis (for Celery backend)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Ensure the CSV data files are in the `store-monitoring-data` directory

## Usage

1. Start the application:
   ```
   python simple_app.py
   ```

2. Trigger a report:
   ```
   GET /trigger_report
   ```
   This will return a report_id that can be used to check the status and retrieve the report.

3. Get report status or download the report:
   ```
   GET /get_report?report_id=<report_id>
   ```
   If the report is still being generated, this will return "Running".
   If the report is complete, this will return the CSV file.

## API Endpoints

### /trigger_report

Triggers the generation of a new report.

- Method: GET
- Response: JSON with report_id
  ```json
  {
    "report_id": "uuid-string"
  }
  ```

### /get_report

Retrieves the status or content of a report.

- Method: GET
- Parameters:
  - report_id: The ID of the report to retrieve
- Response:
  - If report is running: JSON with status
    ```json
    {
      "status": "Running"
    }
    ```
  - If report is complete: CSV file download
  - If error: JSON with error message

## Report Format

The generated report includes the following columns:

- store_id: Unique identifier for the store
- uptime_last_hour: Uptime in the last hour (in minutes)
- uptime_last_day: Uptime in the last day (in hours)
- uptime_last_week: Uptime in the last week (in hours)
- downtime_last_hour: Downtime in the last hour (in minutes)
- downtime_last_day: Downtime in the last day (in hours)
- downtime_last_week: Downtime in the last week (in hours)

## Implementation Details

- The application uses pandas for data processing
- Report generation is performed in a background thread
- Business hours are considered when calculating uptime/downtime
- If business hours data is missing for a store, it's assumed to be open 24/7
- If timezone data is missing for a store, America/Chicago is used as the default
- The current time is considered to be the maximum timestamp in the store status data

## Potential Improvements

1. **Performance Optimization**:
   - Implement database indexing for faster queries
   - Use batch processing for large datasets
   - Implement caching for frequently accessed data

2. **Scalability Enhancements**:
   - Replace threading with a proper task queue (Celery)
   - Use a more robust database (PostgreSQL)
   - Implement horizontal scaling with load balancing

3. **Code Quality Improvements**:
   - Add comprehensive unit and integration tests
   - Implement proper logging
   - Add input validation and error handling
   - Use type hints for better code readability

4. **Feature Additions**:
   - Add authentication and authorization
   - Implement rate limiting
   - Add pagination for large reports
   - Create a dashboard for visualizing uptime/downtime metrics
   - Add email notifications when reports are complete

5. **Data Processing Enhancements**:
   - Implement more sophisticated interpolation logic
   - Add anomaly detection for identifying unusual patterns
   - Provide more granular time interval options (custom date ranges)
   - Add trend analysis over time