# Pasig City Business Analytics and Mapping System

A comprehensive system for analyzing and predicting business trends in Pasig City, Philippines, featuring geographical mapping and predictive analytics.

## Features

- Interactive geographical map of Pasig City with business location markers
- Database of registered businesses (2020-2025)
- Predictive analytics using ARIMA and Moving Average models
- Business growth pattern forecasting
- Emerging business hotspot identification

## Technology Stack

- Frontend: HTML5, CSS3, JavaScript, Leaflet.js (for mapping)
- Backend: PHP
- Database: MySQL
- Analytics: Python (pandas, statsmodels, scikit-learn)
- Additional Libraries: 
  - PHP: Composer for dependency management
  - Python: Required packages listed in requirements.txt

## Project Structure

```
bploop/
├── public/              # Publicly accessible files
│   ├── index.php       # Main entry point
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── assets/         # Images and other assets
├── src/                # Source code
│   ├── config/         # Configuration files
│   ├── models/         # Database models
│   ├── controllers/    # Business logic
│   └── views/          # View templates
├── python/             # Python scripts for analytics
│   ├── models/         # ARIMA and Moving Average models
│   └── utils/          # Utility functions
├── database/           # Database schemas and migrations
└── docs/              # Documentation
```

## Setup Instructions

1. Clone the repository
2. Set up the database using the schema in `database/schema.sql`
3. Install PHP dependencies using Composer
4. Install Python dependencies using pip
5. Configure the database connection in `src/config/database.php`
6. Start the web server

## Requirements

- PHP 7.4 or higher
- Python 3.8 or higher
- MySQL 5.7 or higher
- Web server (Apache/Nginx)

## License

[Your License Here] 