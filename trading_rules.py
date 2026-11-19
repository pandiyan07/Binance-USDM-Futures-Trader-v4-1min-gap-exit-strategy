def CONDITION_VERIFIER(df):
    long_gap = 0.5
    short_gap = 0.5
    long_length = 0
    short_length = 0
    ema34_long_length = 100
    ema34_short_length = 100
    
    last_5ema_value = float(df['ema_5'].iloc[-1])
    last_34ema_value = float(df['ema_34'].iloc[-1])
    fifth_34ema_value = float(df['ema_34'].iloc[-5])
    
    # Long Trading conditions
    l1 = last_5ema_value > last_34ema_value
    #l2 = (last_5ema_value - last_34ema_value) > long_length
    l3 = (last_34ema_value - fifth_34ema_value) > ema34_long_length
    
    # Short Trading conditions
    s1 = last_5ema_value < last_34ema_value
    #s2 = (last_34ema_value - last_5ema_value) > short_length
    s3 = (fifth_34ema_value - last_34ema_value) > ema34_short_length
    
    long_entry_condition = l1 and l3 
    short_entry_condition = s1 and s3 
    
    return long_entry_condition, short_entry_condition, long_gap, short_gap