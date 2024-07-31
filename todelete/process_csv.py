import pandas as pd
from datetime import datetime
import csv

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"CSV file read: {input_file}")

    summary = {}

    for _, row in df.iterrows():
        date = datetime.strptime(row['Date created'], '%d/%m/%Y %H:%M').date()
        shipping_method = row['Shipping Method'].strip() if pd.notna(row['Shipping Method']) and row['Shipping Method'].strip() else "In-Store"
        
        line_items = row['Line items'].split(', Name:')
        for item in line_items:
            try:
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
                print(f"Error processing line item: {item}, error: {e}")
    
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
    
    print(f"Summary written to {output_file}")

def process_filtered_csv(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"CSV file read: {input_file}")

    df_filtered = df[(df['Status'] != 'Cancelled') & ~df['Line items'].str.contains("Innkeeper's", case=False, na=False)]
    
    process_csv_df(df_filtered, output_file)
    
    print(f"Filtered summary written to {output_file}")

def process_csv_df(df, output_file):
    summary = {}

    for _, row in df.iterrows():
        date = datetime.strptime(row['Date created'], '%d/%m/%Y %H:%M').date()
        shipping_method = row['Shipping Method'].strip() if pd.notna(row['Shipping Method']) and row['Shipping Method'].strip() else "In-Store"
        
        line_items = row['Line items'].split(', Name:')
        for item in line_items:
            try:
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
                print(f"Error processing line item: {item}, error: {e}")
    
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

    print(f"Summary written to {output_file}")

def process_additional_csv(output_file):
    try:
        summary_df = pd.read_csv('output_summary.csv', encoding='utf-8')
        additional_df = pd.read_csv('additional_data.csv', encoding='utf-8')

        merged_df = pd.merge(summary_df, additional_df, left_on='Product Name', right_on='Name', how='left')
        output_df = merged_df[['Product Name', 'Type', 'Stock quantity', 'Price', 'Supplier Price']]
        
        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Mapped CSV written to {output_file}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Error processing additional CSV: {e}")

def process_filtered_additional_csv(output_file):
    try:
        summary_df = pd.read_csv('filtered_sales_data.csv', encoding='utf-8')
        additional_df = pd.read_csv('additional_data.csv', encoding='utf-8')

        merged_df = pd.merge(summary_df, additional_df, left_on='Product Name', right_on='Name', how='left')
        output_df = merged_df[['Product Name', 'Type', 'Stock quantity', 'Price', 'Supplier Price']]
        
        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Filtered Mapped CSV written to {output_file}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Error processing filtered additional CSV: {e}")
