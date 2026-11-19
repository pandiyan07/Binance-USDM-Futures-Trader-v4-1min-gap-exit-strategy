import logging
from misc_bin_func import *
from new_order_placer import *

logger = logging.getLogger()

def OC(client, quantity_precision, tsl_order_id, input, sl_response_id, close_side,all_orders_status_dict, ids, ids_name):
    close_order = None
    
    print('BEFORE CLOSING & CANCELING THE ORDERS, CHECKING ONCE MORE FOR THE ORDER STATUSES...!!')
    all_orders_status_dict = CHECK_ORDER_STATUS(client, input[0], ids, ids_name)
    
    if sl_response_id and tsl_order_id and all_orders_status_dict['sl_response_ID'] == 'NEW' and all_orders_status_dict['tsl_order_ID'] == 'NEW':
        try:
            close_order =  NEW_ODR_PLCR(client,close_side,input,quantity_precision)
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
    else:
        print('\n\n as the the order has hit the sl/tsl, CLOSING ORDER IS NOT PLACED DUDEEEEEEEEEEEEEEEEEEEE..................')
        print(tsl_order_id," = tsl_order_id")
        print(sl_response_id," = sl_response_id")
        print(all_orders_status_dict['sl_response_ID']," = all_orders_status_dict['sl_response_ID']")
        print(all_orders_status_dict['tsl_order_ID']," = all_orders_status_dict['tsl_order_ID']")
        print ('\n\n\n')
    
    if sl_response_id:
        logger.info(f'the current SL ORDER STATUS is =')
        logger.info(all_orders_status_dict['sl_response_ID'])
        if all_orders_status_dict['sl_response_ID'] == 'NEW':
            logger.info(f'OC :- {sl_response_id} = sl_response_id FALLBACK STOP LOSS ORDER CANCELED')
            try:
                client.cancel_order(symbol=input[0], orderId=sl_response_id)
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
        else:
            logger.info(f'the SL ORDER {sl_response_id} seems to be filled ALREADY so NOT placing a cancel order for the FILLED SL ORDER')
    else:
        logger.info(f"NO FALLBACK STOP-LOSS ORDER TO CANCEL = {sl_response_id}")
        
    if tsl_order_id:
        logger.info(f'the current TSL ORDER STATUS is =')
        logger.info(all_orders_status_dict['tsl_order_ID'])
        if all_orders_status_dict['tsl_order_ID'] == 'NEW':
            logger.info(f'OC :- {tsl_order_id} = tsl_order_id TRAILING STOP LOSS ORDER CANCELED')
            try:
                client.cancel_order(symbol=input[0], orderId=tsl_order_id)
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
        else:
            logger.info(f'the TSL ORDER {tsl_order_id} seems to be filled ALREADY')
    else:
        logger.info(f"NO TRIALING-STOP-LOSS ORDER TO CANCEL = {tsl_order_id}")
    
    return close_order,all_orders_status_dict


def CLOSE_ORDER_PLACER(client, quantity_precision, tsl_order_id, input, sl_response_id, close_side, all_orders_status_dict, ids, ids_name, Initital_trade_lock):
    
    logger.info('PLACING A CLOSE ORDERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR...........')
    
    close_order_resposnse, all_orders_status_dict = OC(client, quantity_precision, tsl_order_id, input, sl_response_id, close_side, all_orders_status_dict, ids, ids_name)
    
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
    
    if live_position:
        print('\nEVEN AFTER CLOSING THE CURRENT POSITION, LIVE POSITIONS ARE THERE = \n',live_position,'\n\n')
        UNWANTED_POSITION_CLOSER(client,input,quantity_precision,live_position,ids,all_orders)
        live_pos = CHECK_FOR_ACTIVE_POSITIONS(client,input[0])
        if live_pos:
            print('\nEVEN AFTER CLOSING THE CURRENT POSITION, LIVE POSITIONS ARE THERE = \n',live_pos,'\n\n')
        else:
            print('\nall the open positions are CLOSED, NO LIVE POSITIONS TO BE CLOSED CURRENTLY = ',live_pos,'\n\n')
            Initital_trade_lock = False
    else:
        print('\nall the open positions are CLOSED, NO LIVE POSITIONS TO BE CLOSED CURRENTLY = ',live_position,'\n\n')
        Initital_trade_lock = False
    
    if close_order_resposnse:
        ids.append(close_order_resposnse['orderId'])
        ids_name.append('close_order_ID')
        logger.info(f'CLOSE ORDER PLACED SUCCESSFULLY = ')
        logger.info(close_order_resposnse['orderId'])
        logger.info(close_order_resposnse)
    else:
        logger.info('NO CLOSE ORDERS PLACED')
        close_order_resposnse = None
    
    print ('*'*130)
    print ('*'*130)
    print ('\nThe ids =\n',ids,'\nThe ids_name =\n',ids_name,'\n')
    all_orders_status_dict = CHECK_ORDER_STATUS(client, input[0], ids, ids_name)
    logger.info(f'THE FINAL CLOSE ORDER STATUS = {all_orders_status_dict}')
    print ('*'*130)
    print ('*'*130)
                        
    return close_order_resposnse,all_orders_status_dict, Initital_trade_lock
