import logging
from datetime import datetime


logger = logging.getLogger()

def ENTRY_WORK(last_close, no_of_trade, action, entry_price, max_profit_price):
    no_of_trade += 1
    action = 'ENTER_TRADE'
    entry_price = last_close
    max_profit_price = last_close
    return no_of_trade, action, entry_price,max_profit_price
def EXITING_WORK(action, max_profit_price, current_profit_made):
    action = 'EXIT_TRADE'
    max_profit_price = 0
    current_profit_made = 0
    return action, max_profit_price, current_profit_made



def TRADING_LOGIC(Order_limiter, df, action, status, long_entry_condition, short_entry_condition, pyramid_threshhold, max_profit_price, current_profit_made, entry_price, no_of_trade, max_gap, Initital_trade_lock, long_gap, short_gap, position):
    
    last_5ema_value = float(df['ema_5'].iloc[-1])
    last_34ema_value = float(df['ema_34'].iloc[-1])
    current_candle_close = float(df["hl2"].iloc[-1])
    
    if last_5ema_value is not None and last_34ema_value is not None:
        last_close = float(current_candle_close) 
        logger.info(f'current position = {position}')
        
        if long_entry_condition: 
            logger.info('YES THERE IS A LONG TRADE AVAILABLE')
        
        if short_entry_condition: 
            logger.info('YES THERE IS A SHORT TRADE AVAILABLE')
            
        if position is None and Initital_trade_lock == False:
            if long_entry_condition: 
                position = 'LONG'
                status = 'Long trade'
                no_of_trade, action, entry_price, max_profit_price = ENTRY_WORK(last_close,no_of_trade, action, entry_price,max_profit_price)
                max_gap = last_5ema_value - last_34ema_value
            elif short_entry_condition:
                position = 'SHORT'
                status = 'Short trade'
                no_of_trade, action, entry_price, max_profit_price = ENTRY_WORK(last_close,no_of_trade, action, entry_price,max_profit_price)
                max_gap = last_34ema_value - last_5ema_value
            
            logger.info(f'================== >>>  Status, Action = {status}, {action}')
        
        
        if position == 'LONG' and Initital_trade_lock == True:
            current_gap = last_5ema_value - last_34ema_value
            max_gap = max(max_gap, current_gap) 
            if current_gap < (max_gap * long_gap ) or current_candle_close < last_34ema_value: 
                status = 'Exit crossover'
                logger.info(f'LONG TRADE EXIT CROSSOVER  = current_gap({current_gap}) < ({max_gap * long_gap}) max_gap({max_gap}) * long_gap({long_gap})')                
                logger.info(f'LONG TRADE EXIT CROSSOVER  = current_candle_close({current_candle_close}) < last_34ema_value ({last_34ema_value})')
                action, max_profit_price, current_profit_made = EXITING_WORK(action, max_profit_price, current_profit_made)
            
            logger.info(f'================== >>>  Status, Action = {status}, {action} at {datetime.now()}')


        elif position == 'SHORT' and Initital_trade_lock == True:
            current_gap = last_34ema_value - last_5ema_value
            max_gap = max(max_gap, current_gap)
            if current_gap < (max_gap * short_gap) or current_candle_close > last_34ema_value:
                status = 'Exit crossover'
                logger.info(f'SHORT TRADE EXIT CROSSOVER  = current_gap({current_gap}) < ({max_gap * long_gap}) max_gap({max_gap}) * long_gap({long_gap})')                
                logger.info(f'SHORT TRADE EXIT CROSSOVER  = current_candle_close({current_candle_close}) > last_34ema_value ({last_34ema_value})')
                action, max_profit_price, current_profit_made = EXITING_WORK(action, max_profit_price, current_profit_made)
            
            logger.info(f'================== >>>  Status, Action = {status}, {action} at {datetime.now()}')
        
        '''
        #   PYRAMIDING order placement with MAXIMUM LEVERAGE
        if current_profit_made > pyramid_threshhold and position is not None:
            if position == 'LONG' and last_close > last_5ema_value and last_close >= max_profit_price and Initital_trade_lock:
                no_of_trade, action, entry_price,max_profit_price = ENTRY_WORK(last_close,no_of_trade, action, entry_price,max_profit_price)
                logger.info(f'-----------------> Entered PYRAMIDING LONG position with CURRENT PROFIT amount = {current_profit_made}')
                status = 'Long lvg & pyr'
                logger.info(f'================== >>>  PYRAMIDING LONG TRADE ORDER Status, Action = {status}, {action}')
                
            elif position == 'SHORT' and last_close < last_5ema_value and last_close <= max_profit_price and Initital_trade_lock:
                no_of_trade, action, entry_price,max_profit_price = ENTRY_WORK(last_close,no_of_trade, action, entry_price,max_profit_price)
                logger.info(f'-----------------> Entered PYRAMIDING SHORT position with CURRENT PROFIT amount = {current_profit_made}')
                status = 'Short lvg & pyr'
                logger.info(f'================== >>>  PYRAMIDING SHORT TRADE ORDER Status, Action = {status}, {action}')
        '''
        
        return Order_limiter, action, status, position, max_profit_price, current_profit_made, entry_price, no_of_trade, max_gap, Initital_trade_lock, long_gap, short_gap