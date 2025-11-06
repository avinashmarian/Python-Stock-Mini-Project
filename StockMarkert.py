import csv
import argparse  # Added for CLI options
from collections import defaultdict

class Stock:
    
    # Represents a single stock with its data and computed return.
    
    def __init__(self, stock, sector, price_start, price_end):
        self.stock = stock
        self.sector = sector
        self.price_start = float(price_start)
        self.price_end = float(price_end)
        self.return_pct = self.compute_return()
    
    def compute_return(self):
    
       # Computes the percentage return for the stock.
       # Formula: ((price_end - price_start) / price_start) * 100
       # Returns 0.0 if price_start is not positive.
        
        if self.price_start > 0:
            return round(((self.price_end - self.price_start) / self.price_start) * 100, 2)
        return 0.0
    
    def to_dict(self):
    
       # Converts the stock data into a dictionary for easy export or reporting.

        return {
            'Stock': self.stock,
            'Sector': self.sector,
            'PriceStart': self.price_start,
            'PriceEnd': self.price_end,
            'Return': self.return_pct
        }

class StockAnalyzer:
    
    # Handles loading, validating, analyzing, and reporting stock data from a CSV file.

    def __init__(self, filepath):
        self.filepath = filepath
        self.stocks = []
        self.invalid_rows = []  # Added to track invalid rows
        self.load_data()
    
    def load_data(self):
        #
      # Loads and validates data from the CSV file.
      #   Creates Stock objects for valid rows where prices are positive.
      #  Skips invalid rows and collects them for reporting.
    
        try:
            with open(self.filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        stock_name = row['Stock'].strip()
                        sector = row['Sector'].strip()
                        price_start_str = row['PriceStart'].strip()
                        price_end_str = row['PriceEnd'].strip()
                        price_start = float(price_start_str)
                        price_end = float(price_end_str)
                        if price_start > 0 and price_end > 0:
                            self.stocks.append(Stock(stock_name, sector, price_start, price_end))
                        else:
                            reason = "Prices must be > 0"
                            if price_start <= 0:
                                reason += f" (PriceStart: {price_start})"
                            if price_end <= 0:
                                reason += f" (PriceEnd: {price_end})"
                            print(f"Warning: Skipping {stock_name} - {reason}")
                            self.invalid_rows.append({
                                'Stock': stock_name,
                                'Sector': sector,
                                'PriceStart': price_start_str,
                                'PriceEnd': price_end_str,
                                'Reason': reason
                            })
                    except (ValueError, KeyError) as e:
                        reason = "Invalid data format"
                        if isinstance(e, ValueError):
                            # Check for alphabets or invalid characters in prices
                            if any(c.isalpha() for c in price_start_str) or any(c.isalpha() for c in price_end_str):
                                reason = "Invalid alphabets in PriceStart or PriceEnd"
                            else:
                                reason = "Invalid numeric format in PriceStart or PriceEnd"
                        print(f"Warning: Skipping invalid row: {row} - {reason}")
                        self.invalid_rows.append({
                            'Stock': stock_name if 'Stock' in row else 'N/A',
                            'Sector': sector if 'Sector' in row else 'N/A',
                            'PriceStart': price_start_str if 'PriceStart' in row else 'N/A',
                            'PriceEnd': price_end_str if 'PriceEnd' in row else 'N/A',
                            'Reason': reason
                        })
        except FileNotFoundError:
            print(f"Error: File '{self.filepath}' not found.")
    
    def get_all_results(self):
    
       #  Returns a list of dictionaries containing data for all stocks.
       # Each dictionary includes stock details and computed return.
    
        return [stock.to_dict() for stock in self.stocks]
    
    def get_top_stocks(self, n=5):
    
     #   Returns the top N stocks sorted by return percentage in descending order.
        
        sorted_stocks = sorted(self.stocks, key=lambda s: s.return_pct, reverse=True)
        return sorted_stocks[:n]
    
    def aggregate_by_sector(self):
        
      #  Aggregates data by sector: computes average return and count of stocks per sector.
      #  Returns a dictionary: {sector: {'avg_return': float, 'count': int}}
        
        sector_data = defaultdict(lambda: {'total_return': 0.0, 'count': 0})
        for stock in self.stocks:
            sector_data[stock.sector]['total_return'] += stock.return_pct
            sector_data[stock.sector]['count'] += 1
        
        summary = {}
        for sector, data in sector_data.items():
            avg_return = data['total_return'] / data['count'] if data['count'] > 0 else 0.0
            summary[sector] = {'avg_return': round(avg_return, 2), 'count': data['count']}
        return summary
    
    def print_invalid_entries(self):
        # Prints a list of invalid entries (rows skipped due to invalid start/end prices or data format).
        if not self.invalid_rows:
            print("\n=== No Invalid Entries ===")
            return
        
        print("\n=== Invalid Entries ===")
        print(f"{'Stock':<15} | {'Sector':<20} | {'PriceStart':<12} | {'PriceEnd':<10} | {'Reason':<30}")
        print("-" * 100)
        for entry in self.invalid_rows:
            print(f"{entry['Stock']:<15} | {entry['Sector']:<20} | {entry['PriceStart']:<12} | {entry['PriceEnd']:<10} | {entry['Reason']:<30}")
    
    def print_details(self):
        
       # Prints a detailed report to the console, including all stocks, top performers, sector summaries, and invalid entries.
       # Separates computation (via helper methods) from printing for better modularity.
       # Compute data separately from printing

        results = self.get_all_results()
        top5 = self.get_top_stocks()
        sector_summary = self.aggregate_by_sector()
        
        # Print all stock details
        print("\n=== All Stock Details ===")
        print(f"{'Stock':<15} | {'Sector':<20} | {'PriceStart':<12} | {'PriceEnd':<10} | {'Return(%)':<10}")
        print("-" * 80)
        for result in results:
            print(f"{result['Stock']:<15} | {result['Sector']:<20} | {result['PriceStart']:<12.2f} | {result['PriceEnd']:<10.2f} | {result['Return']:<10.2f}")
        
        # Print top 5 best-performing stocks
        print("\n=== Top 5 Best-Performing Stocks ===")
        for i, stock in enumerate(top5, 1):
            print(f"{i}. {stock.stock} ({stock.sector}) - Return: {stock.return_pct}%")
        
        # Print per-sector summary, highlighting the best sector
        print("\n=== Per-Sector Summary ===")
        print(f"{'Sector':<20} | {'Avg Return(%)':<15} | {'Count':<5}")
        print("-" * 45)
        best_sector = max(sector_summary, key=lambda x: sector_summary[x]['avg_return'])
        for sector, data in sector_summary.items():
            highlight = " <-- BEST SECTOR" if sector == best_sector else ""
            print(f"{sector:<20} | {data['avg_return']:<15.2f} | {data['count']:<5}{highlight}")
        
        # Print invalid entries
        self.print_invalid_entries()
    
    def export_csv(self, filename='stock_returns.csv'):
        
        # Exports the stock results to a CSV file.
        
        results = self.get_all_results()
        try:
            with open(filename, 'w', newline='') as file:
                fieldnames = ['Stock', 'Sector', 'PriceStart', 'PriceEnd', 'Return']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"\nResults exported to {filename}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

# Main execution with CLI support
if __name__ == "__main__":



    # Set up argument parser for CLI options
    parser = argparse.ArgumentParser(description="Analyze stock data from a CSV file.")
    parser.add_argument('filepath', help="Path to the CSV file (e.g., E:\\PYTHON\\miniproject\\AviStock.csv)")
    parser.add_argument('--export', default='stock_returns.csv', help="E:\PYTHON\miniproject\Stocks.csv")
    args = parser.parse_args()
    
    # Initialize analyzer with provided filepath
    analyzer = StockAnalyzer(args.filepath)
    if not analyzer.stocks:
        print("No valid data to process.")
    else:
        analyzer.print_details()  # Updated method name for alignment
        analyzer.export_csv(args.export)

        # In Concole type the location {python e:/PYTHON/miniproject/minipro.py E:\PYTHON\miniproject\AviStock.csv }
