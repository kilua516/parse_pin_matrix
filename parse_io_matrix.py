def attr_match(title_line, attr_line, def_attr_line = ''):
    if def_attr_line == '':
        def_attr_line = attr_line
    keys     = title_line.strip().split(',')
    vals     = attr_line.strip().split(',')
    def_vals = def_attr_line.strip().split(',')

    element = {}
    prev_key = ''
    prev_val_is_list = 0
    for key in keys:
        val     = vals.pop(0)
        def_val = def_vals.pop(0)
        if val == '':
            val = def_val
        if key != '':
            if prev_val_is_list:
                element[prev_key] = attr_list
            prev_key = key
            element[key] = val
            attr_list = [val]
            prev_val_is_list = 0
        else:
            attr_list.append(val)
            prev_val_is_list = 1
    if key == '':
        element[prev_key] = attr_list
    return element

with open('./io_matrix.csv', 'r') as f:
    # read title_line
    title_line = f.readline()
    keys = title_line.strip().split(',')

    # read lines
    lines = f.readlines()
    for line in lines:
        element = attr_match(title_line, line)
        print('matrix element')
        print(element)

with open('./io_mux_cfg.csv', 'r') as f:
    # read lines
    lines = f.readlines()
    def_line = ''
    for line in lines:
        keys = line.strip().split(',')
        if keys[0][0:9] == 'iomux_cfg':
            reg_name = keys[0]
            print('reg_name:', reg_name)
            continue
        elif keys[3] == '':
            print('skip an empty line')
            continue
        elif keys[0] == 'bits':
            title_line = line
            continue
        elif keys[0] != '':
            element = attr_match(title_line, line)
            def_line = line
        else:
            element = attr_match(title_line, line, def_line)
        print('mux element')
        print(element)
