import pandas as pd

def fractal(data):
    current_leg = False
    determination_candle = False
    hl_situation = False

    before_ignore_idx = 0
    ignored = False
    ignore_case = False

    candle_side_list = []
    candle_side_list.append(0)

    for idx in range(1, len(data)):
        if not ignored:
            #getting features
            high_base = data.iloc[idx-1].high
            low_base = data.iloc[idx-1].low
            high1 = data.iloc[idx].high
            low1 = data.iloc[idx].low
            
            candle_side = 0
            #check for cases
            if high_base >= high1 and low_base <= low1:
                #case 3
                #Inside
                if not current_leg:
                    before_ignore_idx = idx-1
                    determination_candle = idx-1
                    ignored = True
                    
                elif current_leg:
                    before_ignore_idx = idx-1
                    ignored = True
                    determination_candle = idx-1
                ignore_case = 3
                candle_side = 0
            elif high_base < high1 and low_base > low1:
                #case 4
                #Engulf
                ignore_case = 4
                if current_leg:
                    # if ignored:
                    #     high_base = data.iloc[before_ignore_idx].high
                    #     low_base = data.iloc[before_ignore_idx].low

                    determination_candle = idx
                candle_side = 0
            
            elif high_base < high1:
                #case 1
                if not current_leg:
                    current_leg = 'top'
                    candle_side = 'top'
                elif current_leg == 'top':
                        if ignore_case == '4':
                            ignore_case = False
                            candle_side = 0
                        else:
                            candle_side = 0
                elif current_leg == 'bottom':
                    if ignore_case == '4':
                        candle_side = 0
                        candle_side_list[determination_candle] = 'bottom'
                        ignore_case = False
                        current_leg = 'top'
                    else:
                        candle_side = 0
                        candle_side_list[idx-1] = 'bottom'
                        current_leg = 'top'
            elif low_base > low1:
                #case 2
                if not current_leg:
                    current_leg = 'bottom'
                    candle_side = 'bottom'
                elif current_leg == 'top':
                        if ignore_case == '4':
                            candle_side = 0
                            candle_side_list[determination_candle] = 'top'
                            current_leg = 'bottom'
                            ignore_case = False
                        else:
                            candle_side_list[idx-1] = 'top'
                            current_leg = 'bottom'
                            candle_side = 0
                elif current_leg == 'bottom':
                    if ignore_case == '4':
                        candle_side = 0
                        ignore_case = False
                    else:
                        candle_side = 0
                ignored = False
            candle_side_list.append(candle_side)
            continue    
                
        elif ignored:
            high_base = data.iloc[before_ignore_idx].high
            low_base = data.iloc[before_ignore_idx].low
            high1 = data.iloc[idx].high
            low1 = data.iloc[idx].low
            
            candle_side = 0
            #check for cases
            if high_base >= high1 and low_base <= low1:
                #case 3
                #Inside
                # if not current_leg:
                #     before_ignore_idx = idx
                #     determination_candle = idx
                #     ignored = True
                    
                # if current_leg:
                #     before_ignore_idx = idx
                #     ignored = True
                #     determination_candle = idx
                ignore_case = 3
                candle_side = 0
            elif high_base < high1 and low_base > low1:
                #case 4
                #Engulf
                ignore_case = 4
                if not current_leg:
                    before_ignore_idx = idx
                    determination_candle = idx
                    ignored = True
                if current_leg:
                    before_ignore_idx = idx
                    ignored = True
                    determination_candle = idx
                candle_side = 0
            
            elif high_base < high1:
                #case 1
                if not current_leg:
                    current_leg = 'top'
                    candle_side = 'top'
                elif current_leg == 'top':
                        if ignore_case == '4':
                            candle_side = 0
                            current_leg = 'top'
                        else:
                            candle_side = 0
                            current_leg = 'top'
                elif current_leg == 'bottom':
                    if ignore_case == '4':
                        candle_side = 0
                        candle_side_list[determination_candle] = 'bottom'
                        current_leg = 'top'
                    else:
                        candle_side_list[determination_candle] = 'bottom'
                        candle_side = 0
                        current_leg = 'top'
                ignored = False
                ignore_case = False
            elif low_base > low1:
                #case 2
                if not current_leg:
                    current_leg = 'bottom'
                    candle_side = 'bottom'
                elif current_leg == 'top':
                        if ignore_case == '4':
                            candle_side = 0
                            current_leg = 'bottom'
                            candle_side_list[determination_candle] = 'top'
                        else:
                            candle_side_list[determination_candle] = 'top'
                            candle_side = 0
                            current_leg = 'bottom'
                elif current_leg == 'bottom':
                    if ignore_case == '4':
                        candle_side = 0
                    else:
                        candle_side = 0
                ignored = False
                ignore_case = False
            candle_side_list.append(candle_side)
    
    return candle_side_list