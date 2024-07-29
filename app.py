from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from process_csv import process_csv, process_filtered_csv
import pandas as pd
import os
import plotly.express as px

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Read admin password from environment variable
admin_password = os.environ.get('ADMIN_PASSWORD', 'default_password')

# Mock user database
users = {
    'admin': {
        'password': generate_password_hash(admin_password)
    }
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id not in users:
        return None
    return User(user_id)

# Initialize global variables
uploaded_file_name = None
current_file = 'input_sales_data.csv'
filtered_file = 'filtered_sales_data.csv'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', uploaded_file=uploaded_file_name)

@app.route('/filtered')
@login_required
def filtered():
    return render_template('filtered.html', uploaded_file=uploaded_file_name)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    global uploaded_file_name, current_file, filtered_file
    if 'file' not in request.files:
        print("No file part")
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return redirect(request.url)
    
    if file:
        file_path = 'input_sales_data.csv'
        file.save(file_path)
        uploaded_file_name = file.filename
        current_file = file_path
        print(f"File saved to {file_path}")
        
        if os.path.exists(file_path):
            print(f"Processing {file_path}")
            process_csv(file_path, 'output_summary.csv')
            print("Processing complete")
            process_filtered_csv(file_path, filtered_file)
            print("Filtered processing complete")
            return redirect(url_for('index'))
        else:
            print("File not found after saving")

    return redirect(request.url)

@app.route('/download')
@login_required
def download_file():
    file_path = 'output_summary.csv'
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/download_filtered')
@login_required
def download_filtered_file():
    if os.path.exists(filtered_file):
        return send_file(filtered_file, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/visualize_sales/<metric>/<period>')
@login_required
def visualize_sales(metric, period):
    df = pd.read_csv('output_summary.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    if period == 'day':
        df_grouped = df.groupby(['Date', 'Product Name']).agg({metric: 'sum'}).reset_index()
    elif period == 'week':
        df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['Week', 'Product Name']).agg({metric: 'sum'}).reset_index()
        df_grouped.rename(columns={'Week': 'Date'}, inplace=True)
    elif period == 'month':
        df['Month'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['Month', 'Product Name']).agg({metric: 'sum'}).reset_index()
        df_grouped.rename(columns={'Month': 'Date'}, inplace=True)
    elif period == 'year':
        df['Year'] = df['Date'].dt.to_period('Y').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['Year', 'Product Name']).agg({metric: 'sum'}).reset_index()
        df_grouped.rename(columns={'Year': 'Date'}, inplace=True)
    else:
        return "Invalid period specified", 400
    
    fig = px.bar(df_grouped, x='Date', y=metric, color='Product Name', title=f'{metric.replace("_", " ").title()} per {period.capitalize()}', barmode='stack')
    graph_json = fig.to_json()
    return jsonify(graph_json)

@app.route('/visualize_sales_filtered/<metric>/<period>')
@login_required
def visualize_sales_filtered(metric, period):
    df = pd.read_csv(filtered_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    if period == 'day':
        df_grouped = df.groupby(['Date', 'Product Name']).agg({metric: 'sum'}).reset_index()
    elif period == 'week':
        df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['Week', 'Product Name']).agg({metric: 'sum'}).reset_index()
        df_grouped.rename(columns={'Week': 'Date'}, inplace=True)
    elif period == 'month':
        df['Month'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['Month', 'Product Name']).agg({metric: 'sum'}).reset_index()
        df_grouped.rename(columns={'Month': 'Date'}, inplace=True)
    elif period == 'year':
        df['Year'] = df['Date'].dt.to_period('Y').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['Year', 'Product Name']).agg({metric: 'sum'}).reset_index()
        df_grouped.rename(columns={'Year': 'Date'}, inplace=True)
    else:
        return "Invalid period specified", 400
    
    fig = px.bar(df_grouped, x='Date', y=metric, color='Product Name', title=f'{metric.replace("_", " ").title()} per {period.capitalize()}', barmode='stack')
    graph_json = fig.to_json()
    return jsonify(graph_json)

@app.route('/visualize_shipping_methods')
@login_required
def visualize_shipping_methods():
    df = pd.read_csv('output_summary.csv')
    
    df_grouped = df.groupby('Shipping Method').size().reset_index(name='Counts')
    
    fig = px.pie(df_grouped, names='Shipping Method', values='Counts', title='Shipping Methods Distribution')
    graph_json = fig.to_json()
    return jsonify(graph_json)

@app.route('/visualize_shipping_methods_filtered')
@login_required
def visualize_shipping_methods_filtered():
    df = pd.read_csv(filtered_file)
    
    df_grouped = df.groupby('Shipping Method').size().reset_index(name='Counts')
    
    fig = px.pie(df_grouped, names='Shipping Method', values='Counts', title='Shipping Methods Distribution')
    graph_json = fig.to_json()
    return jsonify(graph_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
