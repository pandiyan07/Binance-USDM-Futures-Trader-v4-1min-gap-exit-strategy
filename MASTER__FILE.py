from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from pytz import timezone
import sys
from binance.um_futures import UMFutures
import pandas as pd


from data_fetcher import *
from emailer import *
from trading_journal import *
from indicator_calculation import *
from order_closer import *
from order_placer import *
from misc_bin_func import *
from trading_logic import *
from trading_rules import *
from tsl_setter import *


all_orders_status_dict = {}
ids = []
ids_name = []


binance_btcusdt_futures_app = Flask(__name__)
a = 0
action = None
df = pd.DataFrame()
trade_log_df = pd.DataFrame()
my_client = None
ohlc_data = None
logger = logging.getLogger()


pyramid_threshhold = 40
max_profit_price = 0
current_profit_made = 0
entry_price = 0
no_of_trade = 0
max_gap = 0
status = None
position = None
close_position = None
price_precision = None
quantity_precision = None
tsl_order_id = None
bal_amnt = None
Initital_trade_lock = False
market_order_response = None

Order_limiter = 0
sl_response_id = 0
close_side = None

# Load environment variables from .env file
load_dotenv()

# Access the Binance API keys
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Sample check to confirm variables loaded correctly
if not API_KEY or not SECRET_KEY:
    raise ValueError("API keys not found. Please set them in the environment or .env file.")

client = UMFutures(API_KEY, SECRET_KEY)

# Set a custom timeout (e.g., 30 seconds)
client.request_kwargs = {"timeout": 30}

# Initial 1 order with 50 usdt with 5 times leverage
# 10 pyramid orders with 10 usdt with 20 times leverage
input = ("BTCUSDT" ,"MARKET" ,0.002 ,90 ,70 ,'ISOLATED',5)
#input = (symbol, order type, tsl, tsl, quantity, margin type, leverage)


def TRADING_ALGO_BOT():
    global Order_limiter, df, my_client, ohlc_data, order_status, status, position, action, Initital_trade_lock, max_profit_price, current_profit_made, max_gap, entry_price, no_of_trade, trade_log_df,market_order_response, quantity_precision, price_precision, tsl_order_id, sl_response_id, close_side, close_position, ids, ids_name, all_orders_status_dict

    try:
        if not df.empty:
            #   TRADE CONDITION CHECKING
            long_entry_condition, short_entry_condition, long_gap, short_gap = CONDITION_VERIFIER(df)
            
            Order_limiter, action, status, position, max_profit_price, current_profit_made, entry_price, no_of_trade, max_gap, Initital_trade_lock, long_gap, short_gap = TRADING_LOGIC(Order_limiter, df, action, status, long_entry_condition, short_entry_condition, pyramid_threshhold, max_profit_price, current_profit_made, entry_price, no_of_trade, max_gap, Initital_trade_lock, long_gap, short_gap, position)
            print ('Order_limiter = ',Order_limiter)
            

            #   ORDER PLACEMENT
            if action == 'ENTER_TRADE' and Initital_trade_lock == False:
                logger.info('setting the action == ENTER_TRADE')
                market_order_response, avg_fill_price, all_ord_stat, sl_response, Initital_trade_lock = OPEN_ORDER_PLACER(input, client, price_precision, quantity_precision, status, position, Initital_trade_lock)
                
                if sl_response:
                    sl_response_id = sl_response['orderId']
                else:
                    sl_response_id = None
                
                if position == "LONG":
                    tsl = input[3]
                elif position == "SHORT":
                    tsl = input[4]
                
                if all_ord_stat == 'FILLED':
                    tsl_response = TSL_ORDER_PLACER(input, position, tsl_order_id, tsl, client, avg_fill_price)
                    if tsl_response:
                        tsl_order_id = tsl_response['orderId']
                    else:
                        tsl_order_id = None
                    
                    action = 'POSITION_IS_LIVE'
                    order_email_argument = []
                    order_email_argument.append(position)
                    order_email_argument.append(market_order_response)
                    order_email_argument.append(sl_response)
                    order_email_argument.append(tsl_response)
                    order_email_argument.append(df)
                    EMAIL_SENDER("ORDER PLACED",order_email_argument)
                
                ids.append(market_order_response['orderId'])
                ids_name.append('market_order_response_ID')
                ids.append(sl_response_id)
                ids_name.append('sl_response_ID')
                ids.append(tsl_order_id)
                ids_name.append('tsl_order_ID')
            
            
            if action == 'POSITION_IS_LIVE':
                logger.info('setting the action == POSITION_IS_LIVE')
                print ('='*130)
                print ('='*130)
                
                live_position = CHECK_FOR_ACTIVE_POSITIONS(client,input[0])
                if live_position:
                    print('AVAILABLE LIVE POSITIONS TO BE CLOSED ARE = \n',live_position)
                else:
                    print (live_position,' = NO LIVE POSITIONS TO BE CLOSED CURRENTLY, so setting the action to EXIT_TRADE')
                    action = 'EXIT_TRADE'
                
                logger.info('The ids =')
                logger.info(ids)
                logger.info('The ids_name')
                logger.info(ids_name)
                all_orders_status_dict = CHECK_ORDER_STATUS(client, input[0], ids, ids_name)
                print ('='*130)
                print ('='*130)
                
                
            if action == 'EXIT_TRADE' and Initital_trade_lock == True:
                logger.info('setting the action == EXIT_TRADE')
                
                if position == 'LONG' or position == 'SHORT':
                    close_position = position
                    position = None
                    print ('The close_position variable has been SET TO = ',close_position)
                
                if close_position == 'LONG':
                    close_side = 'SELL'
                elif close_position == 'SHORT':
                    close_side = 'BUY'
                
                if all_orders_status_dict['market_order_response_ID'] == 'FILLED':
                    print ('SINCE ITS A ',close_position,' POSITION, SO PLACING A ',close_side,' ORDER')
                    close_order_resposnse,all_orders_status_dict, Initital_trade_lock = CLOSE_ORDER_PLACER(client, quantity_precision, tsl_order_id, input, sl_response_id, close_side, all_orders_status_dict, ids, ids_name, Initital_trade_lock)
                    
                    order_email_argument = []
                    order_email_argument.append(position)
                    order_email_argument.append(close_order_resposnse)
                    order_email_argument.append(all_orders_status_dict)
                    order_email_argument.append(df)
                    
                    close_position = None
                    status = None
                    action = None
                    market_order_response = None
                    max_profit_price = 0
                    current_profit_made = 0
                    entry_price = 0
                    no_of_trade = 0
                    max_gap = 0
                    
                    all_orders_status_dict = {}
                    ids = []
                    ids_name = []
                    
                    EMAIL_SENDER("ORDER CLOSED",order_email_argument)
                else:
                    logger.info('Market order seems to be NOT FILLED, the MO order status is = ')
                    logger.info(all_orders_status_dict['market_order_response_ID'])
                
                
                trade_log_df = FETCH_ACCOUNT_TRADES(client,pd)
                print('ONE lOOP DONE')
            print('TRADING_ALGO_BOT has finished running, 1 minute over......',action)
        else:
            logger.info('df dataframe is still EMPTY')
    except Exception as e:
        logger.info(f"Error fetching data: {e}")
        error_list = []
        error_list.append(e)
        ERROR_FLOWCHART(e)
        EMAIL_SENDER('ERROR',error_list)
        scheduler.shutdown()
        STOPPING_WEBSOCKET_STREAMING(my_client)
        sys.exit(1)




def DATA_DUMPER(position_side):
    try:
        global trade_log_df
        print('The position side is = ',position_side,', so DUMPING THE DATA TO THE EMAIL accordingly')
        if position_side == None:
            print(trade_log_df)
            todays_date = datetime.now().date()
            filtered_df = trade_log_df[trade_log_df['time'].dt.date == todays_date]
            #filtered_df = trade_log_df['time'].dt.date == todays_date
            print('THIS IS THE filtered_df = \n',filtered_df)
            if filtered_df.empty:
                print("The DataFrame is empty.")
                filtered_df = None
            else:
                print("The DataFrame is NOT AT ALL empty.")
            dumper_list = []
            dumper_list.append(filtered_df)
            EMAIL_SENDER("DUMP",dumper_list)
            # trade_log_df = pd.DataFrame()          # No need to do this since the table is fetched directly from binance
        else:
            logger.info('there is a live order running currently so TODAYS TRADING REPORT HAS NOT BEEN SENT..........!!!!!!')
        logger.info(f'{position_side} Since the TODAYS TRADING REPORT EMAIL has been sent, exiting the DATA_DUMPER() function')
    except Exception as e:
        error_list = []
        error_list.append(e)
        ERROR_FLOWCHART(e)
        EMAIL_SENDER('ERROR',error_list)

def SCHEDULED_TASKS():
    global df, bal_amnt
    try:
        logger.info ('SCHEDULED_TASKS   --->   RUNNING  SCHEDULED  PROGRAM')
        ohlc_data = CHOOSY_PICKY_DATA_FETCHER()
        df.drop(df.head(1).index, inplace=True)
        df = pd.concat([df, ohlc_data], ignore_index=True)
        df = INDICATOR_CALCULATOR( df, 13, 5, 34)
        TRADING_ALGO_BOT()
    except Exception as e:
        logger.info(f"Error fetching data: {e}")
        error_list = []
        error_list.append(e)
        ERROR_FLOWCHART(e)
        EMAIL_SENDER('ERROR',error_list)
        scheduler.shutdown()
        STOPPING_WEBSOCKET_STREAMING(my_client)
        sys.exit(1)


ist = timezone('Asia/Kolkata')
scheduler = BackgroundScheduler(timezone=ist)
scheduler.add_job(SCHEDULED_TASKS, 'interval', seconds=60)
print('SCHEDULED_TASKS function has been scheduled SUCCESSFULLY')
scheduler.add_job(DATA_DUMPER, 'cron', hour=23, minute=35, args=[position])
print('DATA_DUMPER function has been scheduled SUCCESSFULLY')


@binance_btcusdt_futures_app.route('/')
def HOME_PAGE():
    global a, df, my_client, ohlc_data, position,quantity_precision, price_precision, client, tsl_order_id, input, sl_response_id,close_side,all_orders_status_dict, ids, ids_name,trade_log_df
    if a==0:
        GET_ACCOUNT_BALANCE(client)
        
        my_client = WEBSOCKET_STREAMING_DATFET()
        
        df = REST_API_DATFET()
        df = INDICATOR_CALCULATOR(df, 13, 5, 34)
        price_precision = GET_PRICE_PRECISION(client, input)
        quantity_precision = GET_QUANTITY_PRECISION(client, input)
        
        # Set leverage 
        SET_LEVERAGE(client,input[0],input[6])
        
        
        try:
            live_position = CHECK_FOR_ACTIVE_POSITIONS(client,input[0])
            all_orders = client.get_all_orders(symbol=input[0])
        except ClientError as error:
            print ('='*100)
            logging.error(
                "Found an error ===> STATUS = '{}', ERROR CODE = '{}', ERROR MESSAGE = '{}'".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
            print ('='*100)
            print(error)
            print ('='*100)
            all_orders = None
        
        
        order_email_argument = []
        order_email_argument.append(live_position)
        order_email_argument.append(all_orders)
        EMAIL_SENDER("START",order_email_argument)
        
        
        if live_position or all_orders:
            logger.info('YES, there are a few positions which are ALIVE or else OPEN to be filled = ')
            logger.info(live_position)
            close_order, cancelled_new_orders, all_orders = UNWANTED_POSITION_CLOSER(client, input, quantity_precision, live_position, ids, all_orders)
            #close_order = CLOSE_ORDER_PLACER(client, quantity_precision, tsl_order_id, input, sl_response_id, close_side, all_orders_status_dict, ids, ids_name)
            #print('CLOSE ORDER PLACED FOR THE PRE-EXISTED ORDERS = \n',close_order)
            if live_position or all_orders:
                order_email_argument = []
                order_email_argument.append(close_order)
                order_email_argument.append(cancelled_new_orders)
                EMAIL_SENDER("PRE-EXISTING ORDER CLOSED",order_email_argument)
        else:
            logger.info('LIVE & OPEN ORDERS CHECKING DONE !!')
            logger.info('{live_position} = NO LIVE ORDERS AVAILABLE RIGHT NOW')
            logger.info(all_orders)
        scheduler.start()
        SCHEDULED_TASKS()
        ids = []
        ids_name = []
        trade_log_df = FETCH_ACCOUNT_TRADES(client,pd)
        
    
    a+=1
    if position == 'LONG' or position == 'SHORT':
        trading_status = "<h2>ENTERED A POSITION</h2>"
    else:
        trading_status = "<h2>NO LIVE POSITIONS CURRENTLY</h2>"
    
    print ('REFRESHED the pageeeeeeeeeeeeeeeee.............')      
    
    
    
    if trade_log_df.empty:
        return render_template('btcusdt_binance_futures_dummy_homepage.html', message=trading_status)
    else:
        todays_date = datetime.now().date()
        filtered_df = trade_log_df[trade_log_df['time'].dt.date == todays_date]
        return render_template(
            'btcusdt_binance_futures_homepage.html', 
            message=trading_status,
            filtered_table=filtered_df.to_html(classes='data'),
            filtered_titles=filtered_df.columns.values,
            trade_table=trade_log_df.to_html(classes='data'),
            trade_titles=trade_log_df.columns.values
        ) 
        
# Main loop
if __name__ == "__main__":
    try:
        binance_btcusdt_futures_app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        logger.info('SOME ERROR HAS OCCURED IN THE ================= binance_btcusdt_futures_app')
        scheduler.shutdown()
        STOPPING_WEBSOCKET_STREAMING(my_client)