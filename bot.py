import os
import logging
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

# (Logging and .env setup is the same)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()])
load_dotenv()
api_key = os.getenv('BINANCE_TESTNET_API_KEY')
api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        # (Initialization is the same)
        self.api_key = api_key
        self.api_secret = api_secret
        if testnet:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            logging.info("Connecting to Binance Futures Testnet...")
        else:
            self.client = Client(self.api_key, self.api_secret)
            logging.info("Connecting to Binance Live...")
        try:
            self.client.get_server_time()
            logging.info("Successfully connected to Binance.")
        except Exception as e:
            logging.error(f"Error connecting to Binance: {e}")
            raise

    # (get_user_order_details and place_order methods remain the same)
    def get_user_order_details(self):
        print("\nPlease provide the details for your order.")
        symbol = input("Enter the trading symbol (e.g., BTCUSDT): ").upper()
        while True:
            order_type = input("Enter order type ('market', 'limit', or 'stop-limit'): ").lower()
            if order_type in ['market', 'limit', 'stop-limit']: break
            print("Invalid order type.")
        while True:
            side = input("Enter order side ('buy' or 'sell'): ").lower()
            if side in ['buy', 'sell']: break
            print("Invalid order side.")
        while True:
            try: quantity = float(input("Enter the quantity: ")); break
            except ValueError: print("Invalid quantity.")
        price = None
        stop_price = None
        if order_type in ['limit', 'stop-limit']:
            while True:
                try: price = float(input(f"Enter the limit price: ")); break
                except ValueError: print("Invalid price.")
        if order_type == 'stop-limit':
            while True:
                try: stop_price = float(input(f"Enter the stop price: ")); break
                except ValueError: print("Invalid stop price.")
        return {'symbol': symbol, 'order_type': 'STOP' if order_type == 'stop-limit' else order_type.upper(), 'side': side.upper(), 'quantity': quantity, 'price': price, 'stop_price': stop_price}

    def place_order(self, order_details):
        try:
            logging.info(f"Attempting to place {order_details['side']} {order_details['order_type']} order for {order_details['quantity']} {order_details['symbol']}")
            params = {'symbol': order_details['symbol'], 'side': order_details['side'], 'type': order_details['order_type'], 'quantity': order_details['quantity']}
            if params['type'] == 'LIMIT':
                params['price'] = order_details['price']
                params['timeInForce'] = 'GTC'
            elif params['type'] == 'STOP':
                params['price'] = order_details['price']
                params['stopPrice'] = order_details['stop_price']
                params['timeInForce'] = 'GTC'
            order = self.client.futures_create_order(**params)
            logging.info(f"Successfully placed order: {order}")
            print(f"\n--- Order Successfully Placed ---\nOrderID: {order['orderId']}, Status: {order['status']}\n---------------------------------")
            return order
        except BinanceAPIException as e:
            logging.error(f"Binance API Error: {e.status_code} - {e.message}")
            print(f"\nError placing order: {e.message}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print(f"\nAn unexpected error occurred: {e}")

    def get_account_balance(self):
        """Fetches and displays the USDT account balance."""
        try:
            logging.info("Fetching account balance...")
            balance_info = self.client.futures_account_balance()
            usdt_balance = next((item for item in balance_info if item['asset'] == 'USDT'), None)
            if usdt_balance:
                print("\n--- Account Balance ---")
                print(f"Asset: USDT, Balance: {usdt_balance['balance']}")
                print("-----------------------")
            else:
                print("USDT balance not found.")
            logging.info("Balance fetched successfully.")
        except BinanceAPIException as e:
            logging.error(f"Binance API Error fetching balance: {e.message}")
            print(f"\nError fetching balance: {e.message}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while fetching balance: {e}")
            print(f"\nAn unexpected error occurred: {e}")

    def run(self):
        """The main execution loop for the bot with a user menu."""
        print("--- Simplified Trading Bot ---")
        while True:
            print("\n--- Main Menu ---")
            print("1. Place a new order")
            print("2. Check USDT balance")
            print("3. Exit")
            choice = input("Please select an option: ")

            if choice == '1':
                user_order = self.get_user_order_details()
                print(f"\n--- Confirm Order Details ---\nSymbol: {user_order['symbol']}, Type: {user_order['order_type']}, Side: {user_order['side']}, Quantity: {user_order['quantity']}", end="")
                if user_order['price']: print(f", Price: {user_order['price']}", end="")
                if user_order['stop_price']: print(f", Stop Price: {user_order['stop_price']}", end="")
                print("\n---------------------------")
                confirm = input("Do you want to place this order? (yes/no): ").lower()
                if confirm == 'yes':
                    self.place_order(user_order)
                else:
                    print("Order cancelled by user.")
            elif choice == '2':
                self.get_account_balance()
            elif choice == '3':
                print("Exiting bot. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option.")

# --- Main execution part ---
if __name__ == "__main__":
    if not api_key or not api_secret:
        logging.error("API key and/or secret not found in .env file.")
    else:
        try:
            bot = BasicBot(api_key, api_secret, testnet=True)
            bot.run()
        except Exception as e:
            logging.critical(f"Bot failed to start or run: {e}")