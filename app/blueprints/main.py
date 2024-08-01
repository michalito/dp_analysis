import os
import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app, session, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.utils.processing import process_csv, process_filtered_csv, process_additional_csv, load_processed_data, aggregate_data, aggregate_data_by_product, aggregate_shipping_methods
from app.utils.processing import map_stock_csv_to_summary, aggregate_categories
from app.user_management import load_user, users

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html', uploaded_file=session.get('uploaded_file_name'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.info(f"Attempting login for user: {username}")
        user = load_user(username)
        if user and check_password_hash(users.get(username).get('password'), password):
            logger.info(f"Login successful for user: {username}")
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            logger.warning(f"Login failed for user: {username}")
            flash('Invalid username or password')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        file_path = os.path.join(current_app.root_path, 'input_sales_data.csv')
        try:
            file.save(file_path)
            session['uploaded_file_name'] = file.filename
            session['current_file'] = file_path
            print(f"File saved to {file_path}")

            if os.path.exists(file_path):
                print(f"Processing {file_path}")
                process_csv(file_path, os.path.join(current_app.root_path, 'output_summary.csv'))
                print("Processing complete")
                process_filtered_csv(file_path, os.path.join(current_app.root_path, 'filtered_sales_data.csv'))
                print("Filtered processing complete")
                flash("File uploaded and processed successfully")
            else:
                flash("File not found after saving")
                print("File not found after saving")
        except Exception as e:
            flash(f"File upload failed: {e}")
            current_app.logger.error(f"File upload failed: {e}")
    return redirect(url_for('main.index'))

@main.route('/upload_stock', methods=['GET', 'POST'])
@login_required
def upload_stock_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        file_path = os.path.join(current_app.root_path, 'additional_data.csv')
        try:
            file.save(file_path)
            flash("Stock CSV uploaded successfully")
        except Exception as e:
            flash(f"Stock CSV upload failed: {e}")
            current_app.logger.error(f"Stock CSV upload failed: {e}")
    return redirect(url_for('main.index'))

@main.route('/download')
@login_required
def download_file():
    file_path = os.path.join(current_app.root_path, 'output_summary.csv')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found")
        return redirect(url_for('main.index'))

@main.route('/download_mapped')
@login_required
def download_mapped_file():
    output_file = os.path.join(current_app.root_path, 'mapped_output.csv')
    process_additional_csv(output_file)
    
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        flash("File not found")
        return redirect(url_for('main.index'))

@main.route('/api/visualization')
@login_required
def api_visualization():
    data_type = request.args.get('type')
    period = request.args.get('period')
    csv_path = os.path.join(current_app.root_path, 'output_summary.csv')
    
    df = load_processed_data(csv_path)
    
    if data_type not in ['Total Quantity', 'Total Amount']:
        return jsonify({'error': 'Invalid type specified'}), 400
    
    value_column = 'Total Quantity' if data_type == 'Total Quantity' else 'Total Amount'
    data = aggregate_data(df, value_column, period)
    
    return jsonify(data)

@main.route('/api/visualization_by_product')
@login_required
def api_visualization_by_product():
    data_type = request.args.get('type')
    period = request.args.get('period')
    csv_path = os.path.join(current_app.root_path, 'output_summary.csv')
    
    df = load_processed_data(csv_path)
    
    if data_type not in ['Total Quantity', 'Total Amount']:
        return jsonify({'error': 'Invalid type specified'}), 400
    
    value_column = 'Total Quantity' if data_type == 'Total Quantity' else 'Total Amount'
    data = aggregate_data_by_product(df, value_column, period)
    
    return jsonify(data)

@main.route('/api/shipping_methods')
@login_required
def api_shipping_methods():
    csv_path = os.path.join(current_app.root_path, 'output_summary.csv')
    df = load_processed_data(csv_path)
    
    data = aggregate_shipping_methods(df)
    
    return jsonify(data)

@main.route('/upload_stock_csv', methods=['GET', 'POST'])
@login_required
def upload_stock_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        stock_csv_path = os.path.join(current_app.root_path, 'stock_data.csv')
        summary_csv_path = os.path.join(current_app.root_path, 'output_summary.csv')
        filtered_csv_path = os.path.join(current_app.root_path, 'filtered_sales_data.csv')

        try:
            file.save(stock_csv_path)
            logger.info(f"Stock CSV saved to {stock_csv_path}")

            # Update the main summary CSV
            map_stock_csv_to_summary(summary_csv_path, stock_csv_path)
            logger.info("Mapping stock CSV to main summary complete")

            # Update the filtered CSV
            map_stock_csv_to_summary(filtered_csv_path, stock_csv_path)
            logger.info("Mapping stock CSV to filtered summary complete")

            flash("Stock CSV uploaded and mapped successfully")
        except Exception as e:
            flash(f"File upload failed: {e}")
            logger.error(f"File upload failed: {e}")

    return redirect(url_for('main.index'))

@main.route('/api/categories')
@login_required
def api_categories():
    csv_path = os.path.join(current_app.root_path, 'output_summary.csv')
    df = load_processed_data(csv_path)
    
    data = aggregate_categories(df)
    
    return jsonify(data)

