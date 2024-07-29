import pandas as pd
from datetime import datetime
import csv

def process_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    print(f"CSV file read: {input_file}")

    # Initialize a dictionary to store the results
    summary = {}

    # Process each row
    for _, row in df.iterrows():
        date = datetime.strptime(row['Date created'], '%d/%m/%Y %H:%M').date()
        shipping_method = row['Shipping Method'].strip() if pd.notna(row['Shipping Method']) and row['Shipping Method'].strip() else "In-Store"
        
        # Process the line items
        line_items = row['Line items'].split(', Name:')
        for item in line_items:
            try:
                # Standardizing the format for the first item
                if not item.startswith('Name:'):
                    item = 'Name:' + item

                # Extracting details
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
                # Log the error or handle it as needed
                print(f"Error processing line item: {item}, error: {e}")
    
    # Write the summary to a new CSV file
    with open(output_file, 'w', newline='') as csvfile:
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
