import csv
from collections import defaultdict

class Stock:
    """
    Represents a single stock with its data and computed return.
    """
    def __init__(self, stock, sector, price_start, price_end):
        self.stock = stock
        self.sector = sector
        self.price_start = float(price_start)
        self.price_end = float(price_end)
        self.return_pct = self.compute_return()
    
    def compute_return(self):
        """
        Computes percentage return.
        """
        if self.price_start > 0:
            return round(((self.price_end - self.price_start) / self.price_start) * 100, 2)
        return 0.0
    
    def to_dict(self):
        """
        Returns stock data as a dictionary for export/reporting.
        """
        return {
            'Stock': self.stock,
            'Sector': self.sector,
            'PriceStart': self.price_start,
            'PriceEnd': self.price_end,
            'Return': self.return_pct
        }

class StockAnalyzer:
    """
    Handles loading, validating, analyzing, and reporting stock data.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.stocks = []
        self.load_data()
    
    def load_data(self):
        """
        Loads and validates CSV data, creating Stock objects for valid rows.
        """
        try:
            with open(self.filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        stock_name = row['Stock'].strip()
                        sector = row['Sector'].strip()
                        price_start = float(row['PriceStart'])
                        price_end = float(row['PriceEnd'])
                        if price_start > 0 and price_end > 0:
                            self.stocks.append(Stock(stock_name, sector, price_start, price_end))
                        else:
                            print(f"Warning: Skipping {stock_name} - prices must be > 0")
                    except (ValueError, KeyError):
                        print(f"Warning: Skipping invalid row: {row}")
        except FileNotFoundError:
            print(f"Error: File '{self.filepath}' not found.")
    
    def get_all_results(self):
        """
        Returns a list of dictionaries for all stocks.
        """
        return [stock.to_dict() for stock in self.stocks]
    
    def get_top_stocks(self, n=5):
        """
        Returns the top N stocks by return, sorted descending.
        """
        sorted_stocks = sorted(self.stocks, key=lambda s: s.return_pct, reverse=True)
        return sorted_stocks[:n]
    
    def aggregate_by_sector(self):
        """
        Aggregates average return and count per sector.
        Returns a dict: {sector: {'avg_return': float, 'count': int}}
        """
        sector_data = defaultdict(lambda: {'total_return': 0.0, 'count': 0})
        for stock in self.stocks:
            sector_data[stock.sector]['total_return'] += stock.return_pct
            sector_data[stock.sector]['count'] += 1
        
        summary = {}
        for sector, data in sector_data.items():
            avg_return = data['total_return'] / data['count'] if data['count'] > 0 else 0.0
            summary[sector] = {'avg_return': round(avg_return, 2), 'count': data['count']}
        return summary
    
    def printdetails(self):
        """
        Prints the console report.
        """
        results = self.get_all_results()
        top5 = self.get_top_stocks()
        sector_summary = self.aggregate_by_sector()
        
        print("\n=== All Stock Details ===")
        print(f"{'Stock':<15} | {'Sector':<20} | {'PriceStart':<12} | {'PriceEnd':<10} | {'Return(%)':<10}")
        print("-" * 80)
        for result in results:
            print(f"{result['Stock']:<15} | {result['Sector']:<20} | {result['PriceStart']:<12.2f} | {result['PriceEnd']:<10.2f} | {result['Return']:<10.2f}")
        
        print("\n=== Top 5 Best-Performing Stocks ===")
        for i, stock in enumerate(top5, 1):
            print(f"{i}. {stock.stock} ({stock.sector}) - Return: {stock.return_pct}%")
        
        print("\n=== Per-Sector Summary ===")
        print(f"{'Sector':<20} | {'Avg Return(%)':<15} | {'Count':<5}")
        print("-" * 45)
        best_sector = max(sector_summary, key=lambda x: sector_summary[x]['avg_return'])
        for sector, data in sector_summary.items():
            highlight = " <-- BEST SECTOR" if sector == best_sector else ""
            print(f"{sector:<20} | {data['avg_return']:<15.2f} | {data['count']:<5}{highlight}")
        
        print(best_sector," <--- ")
    
    def export_csv(self, filename='stock_returns.csv'):
       
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

# Main
if __name__ == "__main__":
 
    filepath = 'E:\PYTHON\miniproject\AviStock.csv'  
    analyzer = StockAnalyzer(filepath)
    if not analyzer.stocks:
        print("No valid data to process.")
    else:
        analyzer.printdetails()
        analyzer.export_csv()
