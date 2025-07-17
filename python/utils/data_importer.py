import pandas as pd
import mysql.connector
from datetime import datetime
import json
import os

class BusinessDataImporter:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = self._connect_db()

    def _connect_db(self):
        return mysql.connector.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database']
        )

    def import_business_data(self, file_path):
        """
        Import business data from Excel/CSV file
        Expected columns:
        - business_name
        - business_type
        - registration_date
        - latitude
        - longitude
        - address
        - barangay
        - contact_number (optional)
        - email (optional)
        """
        try:
            # Read the file based on its extension
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                raise ValueError("Unsupported file format. Please use .xlsx or .csv")

            # Clean and prepare the data
            df = self._clean_data(df)

            # Insert data into database
            self._insert_businesses(df)

            print(f"Successfully imported {len(df)} business records")
            return True

        except Exception as e:
            print(f"Error importing data: {str(e)}")
            return False

    def _clean_data(self, df):
        """Clean and standardize the data"""
        # Convert column names to lowercase
        df.columns = df.columns.str.lower()

        # Ensure required columns exist
        required_columns = ['business_name', 'business_type', 'registration_date', 
                          'latitude', 'longitude', 'address', 'barangay']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Convert registration_date to datetime
        df['registration_date'] = pd.to_datetime(df['registration_date'])

        # Clean coordinates
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

        # Remove rows with invalid coordinates
        df = df.dropna(subset=['latitude', 'longitude'])

        # Ensure coordinates are within Pasig City bounds
        df = df[
            (df['latitude'] >= 14.5) & (df['latitude'] <= 14.6) &
            (df['longitude'] >= 121.0) & (df['longitude'] <= 121.1)
        ]

        return df

    def _insert_businesses(self, df):
        """Insert business data into the database"""
        cursor = self.conn.cursor()

        insert_query = """
        INSERT INTO businesses 
        (business_name, business_type, registration_date, latitude, longitude, 
         address, barangay, contact_number, email, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            values = (
                row['business_name'],
                row['business_type'],
                row['registration_date'].date(),
                float(row['latitude']),
                float(row['longitude']),
                row['address'],
                row['barangay'],
                row.get('contact_number', None),
                row.get('email', None),
                'active'
            )
            
            try:
                cursor.execute(insert_query, values)
            except mysql.connector.Error as err:
                print(f"Error inserting business {row['business_name']}: {err}")

        self.conn.commit()
        cursor.close()

    def generate_sample_data(self, output_file='sample_business_data.csv'):
        """Generate sample business data for testing"""
        sample_data = {
            'business_name': [
                'Sample Restaurant 1',
                'Sample Retail Store 1',
                'Sample Service Business 1'
            ],
            'business_type': [
                'Restaurant',
                'Retail',
                'Service'
            ],
            'registration_date': [
                '2020-01-15',
                '2021-06-20',
                '2022-03-10'
            ],
            'latitude': [
                14.5764,
                14.5780,
                14.5750
            ],
            'longitude': [
                121.0851,
                121.0860,
                121.0840
            ],
            'address': [
                '123 Main St, Pasig City',
                '456 Market St, Pasig City',
                '789 Service Rd, Pasig City'
            ],
            'barangay': [
                'San Antonio',
                'San Miguel',
                'San Nicolas'
            ],
            'contact_number': [
                '09123456789',
                '09234567890',
                '09345678901'
            ],
            'email': [
                'restaurant1@example.com',
                'retail1@example.com',
                'service1@example.com'
            ]
        }

        df = pd.DataFrame(sample_data)
        df.to_csv(output_file, index=False)
        print(f"Sample data generated and saved to {output_file}")

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'pasig_business_analytics'
    }
    
    importer = BusinessDataImporter(db_config)
    try:
        # Generate sample data if needed
        importer.generate_sample_data()
        
        # Import actual data
        # importer.import_business_data('path_to_your_business_data.csv')
    finally:
        importer.close() 