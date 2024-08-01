import pandas as pd
from datetime import datetime
import csv
import logging
import os
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_csv(input_file, output_file):
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        logger.info(f"CSV file read: {input_file}")

        summary = summarize_sales_data(df)
        write_summary_to_csv(summary, output_file)
        logger.info(f"Summary written to {output_file}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")

def summarize_sales_data(df):
    summary = {}

    for _, row in df.iterrows():
        try:
            date = datetime.strptime(row['Date created'], '%d/%m/%Y %H:%M').date()
            shipping_method = row['Shipping Method'].strip() if pd.notna(row['Shipping Method']) and row['Shipping Method'].strip() else "In-Store"
            
            line_items = row['Line items'].split(', Name:')
            for item in line_items:
                if not item.startswith('Name:'):
                    item = 'Name:' + item

                parts = item.split('Total:')
                if len(parts) < 2:
                    continue
                total = float(parts[1].strip())

                name_parts = parts[0].split('Quantity:')
                if len(name_parts) < 2:
                    continue

                quantity = int(name_parts[1].strip())
                name = name_parts[0].split('Name:')[1].strip()

                if date not in summary:
                    summary[date] = {}
                if name not in summary[date]:
                    summary[date][name] = {'quantity': 0, 'total': 0, 'shipping_methods': {}}

                summary[date][name]['quantity'] += quantity
                summary[date][name]['total'] += total

                if shipping_method not in summary[date][name]['shipping_methods']:
                    summary[date][name]['shipping_methods'][shipping_method] = {'quantity': 0, 'total': 0}

                summary[date][name]['shipping_methods'][shipping_method]['quantity'] += quantity
                summary[date][name]['shipping_methods'][shipping_method]['total'] += total
        except (IndexError, ValueError) as e:
            logger.error(f"Error processing line item: {item}, error: {e}")

    return summary

def write_summary_to_csv(summary, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Date', 'Product Name', 'Shipping Method', 'Total Quantity', 'Total Amount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for date, products in summary.items():
            for name, data in products.items():
                for shipping_method, ship_data in data['shipping_methods'].items():
                    writer.writerow({
                        'Date': date,
                        'Product Name': name,
                        'Shipping Method': shipping_method,
                        'Total Quantity': ship_data['quantity'],
                        'Total Amount': ship_data['total']
                    })

def process_filtered_csv(input_file, output_file):
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        logger.info(f"CSV file read: {input_file}")

        df_filtered = df[(df['Status'] != 'Cancelled') & ~df['Line items'].str.contains("Innkeeper's", case=False, na=False)]
        summary = summarize_sales_data(df_filtered)
        write_summary_to_csv(summary, output_file)
        logger.info(f"Filtered summary written to {output_file}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Error processing filtered CSV: {e}")

def process_additional_csv(output_file):
    try:
        summary_df = pd.read_csv('output_summary.csv', encoding='utf-8')
        additional_df = pd.read_csv('additional_data.csv', encoding='utf-8')

        merged_df = pd.merge(summary_df, additional_df, left_on='Product Name', right_on='Name', how='left')
        output_df = merged_df[['Product Name', 'Type', 'Stock quantity', 'Price', 'Supplier Price']]

        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"Mapped CSV written to {output_file}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Error processing additional CSV: {e}")

def process_filtered_additional_csv(output_file):
    try:
        summary_df = pd.read_csv('filtered_sales_data.csv', encoding='utf-8')
        additional_df = pd.read_csv('additional_data.csv', encoding='utf-8')

        merged_df = pd.merge(summary_df, additional_df, left_on='Product Name', right_on='Name', how='left')
        output_df = merged_df[['Product Name', 'Type', 'Stock quantity', 'Price', 'Supplier Price']]

        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"Filtered Mapped CSV written to {output_file}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Error processing filtered additional CSV: {e}")

# New functions to load processed data and aggregate it for visualization

def load_processed_data(file_path):
    """Load the processed CSV data."""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)

def aggregate_data(df, value_column, period, group_by_product=False):
    """
    Aggregate data by the specified period and optionally by product name.
    
    Parameters:
    df - pandas DataFrame containing the data
    value_column - the column to aggregate (e.g., 'Total Quantity' or 'Total Amount')
    period - aggregation period ('day', 'week', 'month', 'year')
    group_by_product - whether to group by product name
    
    Returns:
    Dictionary with keys 'x', 'y', and optionally 'product', where 'x' is the list of time periods,
    'y' is the list of aggregated values for each period, and 'product' is the product name if grouping by product.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    if period == 'day':
        df['Period'] = df['Date'].dt.date
    elif period == 'week':
        df['Period'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    elif period == 'month':
        df['Period'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time)
    elif period == 'year':
        df['Period'] = df['Date'].dt.to_period('Y').apply(lambda r: r.start_time)
    else:
        raise ValueError('Invalid period specified')
    
    if group_by_product:
        df_grouped = df.groupby(['Period', 'Product Name']).sum(numeric_only=True).reset_index()
    else:
        df_grouped = df.groupby('Period').sum(numeric_only=True).reset_index()
    
    data = {
        'x': df_grouped['Period'].astype(str).tolist(),
        'y': df_grouped[value_column].tolist()
    }
    
    if group_by_product:
        data['product'] = df_grouped['Product Name'].tolist()
    
    return data

def aggregate_data_by_product(df, value_column, period):
    """
    Aggregate data by the specified period and group by product name.
    
    Parameters:
    df - pandas DataFrame containing the data
    value_column - the column to aggregate (e.g., 'Total Quantity' or 'Total Amount')
    period - aggregation period ('day', 'week', 'month', 'year')
    
    Returns:
    Dictionary with keys 'x', 'data', where 'x' is the list of time periods,
    'data' is a dictionary of product names with their corresponding y values.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    if period == 'day':
        df['Period'] = df['Date'].dt.date
    elif period == 'week':
        df['Period'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    elif period == 'month':
        df['Period'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time)
    elif period == 'year':
        df['Period'] = df['Date'].dt.to_period('Y').apply(lambda r: r.start_time)
    else:
        raise ValueError('Invalid period specified')
    
    df_grouped = df.groupby(['Period', 'Product Name']).sum(numeric_only=True).reset_index()
    
    periods = df_grouped['Period'].unique().tolist()
    products = df_grouped['Product Name'].unique().tolist()

    data = {
        'x': [str(period) for period in periods],
        'data': {product: [] for product in products}
    }

    for period in periods:
        period_data = df_grouped[df_grouped['Period'] == period]
        for product in products:
            value = period_data[period_data['Product Name'] == product][value_column].sum()
            if isinstance(value, np.int64):
                value = int(value)
            elif isinstance(value, np.float64):
                value = float(value)
            data['data'][product].append(value)

    return data

def aggregate_shipping_methods(df):
    """
    Aggregate shipping methods data for visualization as a pie chart.
    
    Parameters:
    df - pandas DataFrame containing the data

    Returns:
    Dictionary with keys 'labels' and 'values', suitable for a pie chart.
    """
    shipping_methods = df['Shipping Method'].fillna('In-Store')
    shipping_summary = shipping_methods.value_counts()

    data = {
        'labels': shipping_summary.index.tolist(),
        'values': shipping_summary.values.tolist()
    }

    return data

def clean_price_column(column):
    """Remove non-numeric characters from a price column and convert to float."""
    return column.replace('[\€,]', '', regex=True).astype(float)

def map_stock_csv_to_summary(summary_csv, stock_csv):
    try:
        summary_df = load_processed_data(summary_csv)
        stock_df = pd.read_csv(stock_csv)

        # Log the initial data
        logger.info(f"Initial Stock Data:\n{stock_df.head()}")

        # Clean 'Price' and 'Supplier Price' columns
        stock_df['Price'] = clean_price_column(stock_df['Price'])
        stock_df['Supplier Price'] = clean_price_column(stock_df['Supplier Price'])

        # Log the data after cleaning
        logger.info(f"Stock Data after cleaning:\n{stock_df[['Name', 'Price', 'Supplier Price']].head()}")

        # Map 'Name' to 'Product Name' and add new columns
        merged_df = pd.merge(summary_df, stock_df[['Name', 'Categories', 'Price', 'Supplier Price']],
                             left_on='Product Name', right_on='Name', how='left')

        # Drop 'Name' column from the merged dataframe
        merged_df.drop(columns=['Name'], inplace=True)

        # Calculate Margin and Margin Percentage, handle missing values gracefully
        merged_df['Margin'] = merged_df['Price'] - merged_df['Supplier Price']
        merged_df['Margin Percentage'] = np.ceil((merged_df['Margin'] / merged_df['Price']) * 100)

        # Handle cases where Price or Supplier Price is NaN
        merged_df['Margin'].fillna(0, inplace=True)
        merged_df['Margin Percentage'].fillna(0, inplace=True)

        # Log the final merged data
        logger.info(f"Final Merged Data:\n{merged_df.head()}")

        # Save the updated dataframe to the summary CSV
        merged_df.to_csv(summary_csv, index=False, encoding='utf-8-sig')
        logger.info(f"Mapped CSV written to {summary_csv}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Error processing stock CSV: {e}")

def aggregate_categories(df):
    """
    Aggregate categories data for visualization as a pie chart.
    
    Parameters:
    df - pandas DataFrame containing the data

    Returns:
    Dictionary with keys 'labels' and 'values', suitable for a pie chart.
    """
    categories = df['Categories'].dropna().replace('', np.nan).dropna()
    categories_summary = categories.value_counts()

    data = {
        'labels': categories_summary.index.tolist(),
        'values': categories_summary.values.tolist()
    }

    return data