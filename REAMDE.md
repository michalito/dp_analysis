# Sales Data Visualization Application

## Overview

This project is a Dockerized Flask application designed for visualizing sales data. The application includes features such as file upload and processing, various data visualizations, user authentication, and SSL support using Let's Encrypt. It supports both development and production modes.

## Features

1. **Upload and Process Sales Data CSV**: Users can upload CSV files containing sales data. The application processes the uploaded data and generates summaries for visualization.
2. **Visualize Sales Data**: The application provides visualizations for:
   - Sales quantity per day, week, month, and year
   - Sales amount per day, week, month, and year
   - Distribution of shipping methods
3. **Authentication**: Users must log in to access the application.
4. **SSL Support**: In production mode, the application uses Let's Encrypt to provide SSL certificates and secure communication.
5. **Automatic SSL Certificate Renewal**: Certbot is used to automatically renew SSL certificates.
6. **Development and Production Modes**: The application can run in development mode without SSL or in production mode with SSL.

## How to Use

### Prerequisites

- Docker
- A domain name pointing to your server's IP address
- An email address for SSL certificate registration

### Environment Variables

- `ADMIN_PASSWORD`: Password for the admin user.
- `ENV`: Set to `production` for production mode, or `development` for development mode.

### Setup Instructions

1. **Clone the Repository**

```sh
git clone https://github.com/your-repo/sales-data-visualization.git
cd sales-data-visualization
```

2. **Build the Docker Image**

Build the Docker image, passing the admin password as a build argument.

```sh
docker build -t sales-app --build-arg ADMIN_PASSWORD=your_admin_password .
```

3. **Run the Docker Container**

#### For Production

Run the Docker container in production mode, exposing ports 80 and 443.

```sh
docker run -e ENV=production -p 80:80 -p 443:443 sales-app
```

#### For Development

Run the Docker container in development mode, exposing port 5000.

```sh
docker run -e ENV=development -p 5000:5000 sales-app
```

Replace `your_admin_password` with the desired password for the admin user.

### Accessing the Application

- **Production Mode**: Access the application at `https://yourdomain.com`.
- **Development Mode**: Access the application at `http://localhost:5000`.

### Using the Application

1. **Login**: Navigate to the login page and enter the admin credentials.
   - **Username**: `admin`
   - **Password**: The password you set in the `ADMIN_PASSWORD` environment variable.
2. **Upload CSV**: Upload a CSV file containing sales data.
3. **Visualize Data**: Use the provided buttons to view various visualizations of the sales data.
4. **Download Processed Data**: Download the processed summary CSV.
5. **Filtered Data**: Access the filtered page to view data excluding cancelled orders and products with "Innkeeper's" in the name.

## Features Recap

1. **File Upload and Processing**: 
   - Users can upload CSV files.
   - The application processes the data and generates summaries.

2. **Data Visualizations**: 
   - Sales quantity and amount by day, week, month, and year.
   - Shipping methods distribution.

3. **Authentication**: 
   - Users must log in to access the application.

4. **SSL Support**: 
   - Uses Let's Encrypt for SSL certificates.
   - Automatic renewal of SSL certificates using Certbot.

5. **Modes**: 
   - **Development Mode**: Runs without SSL.
   - **Production Mode**: Runs with SSL.

## Future Expansions

1. **Enhanced User Management**: 
   - Add roles and permissions to manage different types of users (e.g., admin, viewer).
   - Implement user registration and password reset functionalities.

2. **Advanced Data Filtering**: 
   - Allow users to filter data by more criteria (e.g., date range, product categories).

3. **Dashboard**: 
   - Create a dashboard with multiple visualizations and summary statistics.

4. **Export Options**: 
   - Allow users to export visualizations as images or PDFs.

5. **Integration with External Data Sources**: 
   - Integrate with external data sources (e.g., databases, APIs) for real-time data visualization.

6. **Improved UI/UX**: 
   - Enhance the user interface with responsive design and better interactivity.

Certainly! Here's a section for the `README.md` file that describes the structure of the app and the codebase in a clear, concise, and organized markup format.

### Project Structure

The project is organized as follows:

```
app/
├── blueprints/
│   ├── __init__.py
│   ├── main.py
│   └── filtered.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── filtered.html
│   ├── login.html
├── utils/
│   ├── __init__.py
│   └── processing.py
├── user_management.py
└── __init__.py
run.py
Dockerfile
default.conf
entrypoint.sh
nginx.conf
requirements.txt
README.md
```

### Codebase Overview

#### `app/`

The main directory containing the Flask application.

- **`app/blueprints/`**: Contains the blueprint modules for organizing routes.
  - **`__init__.py`**: Initializes the blueprint.
  - **`main.py`**: Main routes for the application, including file uploads, downloads, and visualizations.
  - **`filtered.py`**: Routes for handling filtered data, including visualizations and downloads.

- **`app/static/`**: Contains static files such as CSS.
  - **`css/styles.css`**: The main stylesheet for the application.

- **`app/templates/`**: Contains HTML templates for the application.
  - **`base.html`**: The base template that other templates extend.
  - **`index.html`**: Template for the home page with visualizations and file operations.
  - **`filtered.html`**: Template for the filtered data page with visualizations and file operations.
  - **`login.html`**: Template for the login page.

- **`app/utils/`**: Contains utility modules for data processing.
  - **`__init__.py`**: Initializes the utils module.
  - **`processing.py`**: Functions for processing and aggregating CSV data.

- **`app/user_management.py`**: Handles user management and authentication.

- **`app/__init__.py`**: Initializes the Flask application, registers blueprints, and sets up configurations.

#### `Dockerfile`

This file contains the instructions to build a Docker image for the application.

#### `default.conf`

Nginx configuration file for serving the application.

#### `entrypoint.sh`

Entrypoint script for starting the application.

#### `nginx.conf`

Main Nginx configuration file.

#### `requirements.txt`

A list of Python dependencies for the project.

### Usage

To run the application:

1. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```sh
   python run.py
   ```

3. **Access the Application**:
   Open your browser and go to `http://localhost:5000`.

### Running with Docker

1. **Build the Docker Image**:
   ```sh
   docker build -t sales-app --build-arg ADMIN_PASSWORD=dragonphoenix --build-arg FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') .
   ```

2. **Run the Docker Container**:
   ```sh
   docker run -e ADMIN_PASSWORD=your_admin_password -e FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') -p 80:80 -p 443:443 sales-app
   ```
   ***Development Run**
   ```sh
   docker run -e ENV=development -e FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') -p 5000:5000 sales-app
   ```

## Conclusion

This Sales Data Visualization Application provides a robust foundation for visualizing sales data with features like SSL support, user authentication, and flexible deployment modes. The application is designed to be extendable and can be enhanced with additional features and integrations in the future.