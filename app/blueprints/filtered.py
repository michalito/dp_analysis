from flask import Blueprint, render_template, send_file, flash, redirect, url_for, session, current_app, jsonify, request
from flask_login import login_required
from app.utils.processing import process_filtered_additional_csv, load_processed_data, aggregate_data_by_product, aggregate_data, aggregate_shipping_methods
import os

filtered = Blueprint('filtered', __name__)

@filtered.route('/filtered')
@login_required
def filtered_index():
    return render_template('filtered.html', uploaded_file=session.get('uploaded_file_name'))

@filtered.route('/download_filtered_summary')
@login_required
def download_filtered_summary():
    file_path = os.path.join(current_app.root_path, 'filtered_sales_data.csv')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found")
        return redirect(url_for('filtered.filtered_index'))

@filtered.route('/download_filtered_mapped')
@login_required
def download_filtered_mapped():
    output_file = os.path.join(current_app.root_path, 'filtered_mapped_output.csv')
    process_filtered_additional_csv(output_file)
    
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        flash("File not found")
        return redirect(url_for('filtered.filtered_index'))
    
@filtered.route('/api/filtered_visualization')
@login_required
def api_filtered_visualization():
    data_type = request.args.get('type')
    period = request.args.get('period')
    csv_path = os.path.join(current_app.root_path, 'filtered_sales_data.csv')
    
    df = load_processed_data(csv_path)
    
    if data_type not in ['Total Quantity', 'Total Amount']:
        return jsonify({'error': 'Invalid type specified'}), 400
    
    value_column = 'Total Quantity' if data_type == 'Total Quantity' else 'Total Amount'
    data = aggregate_data(df, value_column, period)
    
    return jsonify(data)

@filtered.route('/api/filtered_visualization_by_product')
@login_required
def api_filtered_visualization_by_product():
    data_type = request.args.get('type')
    period = request.args.get('period')
    csv_path = os.path.join(current_app.root_path, 'filtered_sales_data.csv')
    
    df = load_processed_data(csv_path)
    
    if data_type not in ['Total Quantity', 'Total Amount']:
        return jsonify({'error': 'Invalid type specified'}), 400
    
    value_column = 'Total Quantity' if data_type == 'Total Quantity' else 'Total Amount'
    data = aggregate_data_by_product(df, value_column, period)
    
    return jsonify(data)

@filtered.route('/api/filtered_shipping_methods')
@login_required
def api_filtered_shipping_methods():
    csv_path = os.path.join(current_app.root_path, 'filtered_sales_data.csv')
    df = load_processed_data(csv_path)
    
    data = aggregate_shipping_methods(df)
    
    return jsonify(data)