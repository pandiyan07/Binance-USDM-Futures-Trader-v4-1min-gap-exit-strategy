import logging
from binance.error import ClientError


def NEW_ODR_PLCR(client,pos_side,input,quantity_precision):
    
    rounded_qty = round(input[2], quantity_precision)
    
    order_response = client.new_order(
        symbol=input[0],
        side=pos_side, 
        type=input[1],
        quantity=rounded_qty
        )
    
    return order_response



def UNWANTED_POSITION_CLOSER(client,input,quantity_precision,live_position,ids,all_orders):

    #   CLOSING THE OPEN POSITIONS
    
    if live_position:
        if float(live_position['positionAmt']) < 0:
            close_side = 'BUY'
        elif float(live_position['positionAmt']) > 0:
            close_side = 'SELL'
        
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
            close_order = None

        if close_order:
            print('UNWANTED OPEN POSITIONS HAS BEEN CLOSED = \n',close_order)
        else:
            print('UNWANTED OPEN POSITIONS NOT CLOSED = \n',close_order)
    else:
        print('UNWANTED_POSITION_CLOSER =\nxxxxx    THERE ARE NO LIVE POSITIONS CURRENTLY     xxxxx')
        close_order = None
    
    
    
    z = 0
    #   CANCELLING THE OPEN ORDERS
    cancelled_new_orders = []
    
    if all_orders:
        for order in all_orders:    
            if order['status'] == 'NEW':
                z+=1
                print ('='*100)
                print ('BELOW IS THE ORDER DETAILS THAT IS NEW STATUS FROM THE PREVIOUS SESSION\n')
                print (order)
                print ('='*100)
                cancelled_new_orders.append(order)
                try:
                    client.cancel_order(symbol=input[0], orderId=order['orderId'])
                    order_status = client.get_orders(symbol=input[0], orderId=order['orderId'])
                    if order_status:
                        for os in order_status:
                            print(f"THE ORDER STATUS of => ORDER ID = {os['orderId']} is = {os['status']}")
                    else:
                        print(order_status,' a EMPTY LIST RESPONSE from the order_status variable\n It seems the sl/tsl has been cancelled successfully maplaaaaaaaaaaaaaaaaaaaa = \n\n')
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
                print('IT IS NOT A NEW ORDER....!!!! = ',order['status'])
        if z == 0:
            all_orders = None
    else:
        print('UNWANTED_POSITION_CLOSER =  ',all_orders,'NO RESPONSE FROM all_orders & ids maplaaaaaaaaaaaaaaaaaaaa = \n\n', ids)
        cancelled_new_orders = None
    
    
    return close_order, cancelled_new_orders, all_orders