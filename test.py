with open('./test.csv', 'r') as f:
    # read headline
    headline = f.readline()
    keys = headline.strip().split(',')
    print(keys)

    # read lines
    lines = f.readlines()

for line in lines:
    vals = line.strip().split(',')
    print(vals)
    elements = {}
    prev_key = ''
    for key in keys:
        val = vals.pop(0)
        if key == 'function':
            func_mux = [val]
        elif key != '' and prev_key == 'function':
            elements[prev_key] = func_mux
        if key == 'name':
            elements[key] = val
        if key == '' and prev_key == 'function':
            func_mux.append(val)
        if key != '':
            prev_key = key
    if key == '':
        elements['function'] = func_mux
    print('elements')
    print(elements)
