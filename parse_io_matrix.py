import datetime

FUNCTION = 'function'

def valid_chk(value):
    if value == '':
        return False
    elif value == '-':
        return False
    else:
        return True

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

def func_chk(io_name, io_item):
    for func_item in io_item['func_mux']:
        if valid_chk(func_item['func']) and func_item['func'] not in io_item[FUNCTION]:
            print('*********************************************')
            print('function list not match')
            print(io_name)
            print('function: ', func_item['func'])
            print('function list: ', io_item[FUNCTION])
            print('*********************************************')
            return 0
    return 1

def gen_func_con(func_item):
    if not valid_chk(func_item['func']):
        fun_ie    = '1\'b0'
        fun_i     = '/*floating*/'
        fun_oe    = '1\'b0'
        fun_o     = '1\'b0'
        default_i = '1\'b0'
    else:
        [io_in, io_out] = func_item['dir'].split('/')
        bit_idx_left_bound  = func_item['func'].find('[')
        bit_idx_right_bound = func_item['func'].find(']')

        if bit_idx_left_bound == -1:
            if func_item['rep_times'] != 1:
                fun_ie = ('%s_f%s_ie'%(func_item['func'], func_item['rep_order']))
                fun_i  = ('%s_f%s_i' %(func_item['func'], func_item['rep_order']))
                fun_oe = ('%s_f%s_oe'%(func_item['func'], func_item['rep_order']))
                fun_o  = ('%s_f%s_o' %(func_item['func'], func_item['rep_order']))
            else:
                fun_ie = func_item['func'] + '_ie'
                fun_i  = func_item['func'] + '_i'
                fun_oe = func_item['func'] + '_oe'
                fun_o  = func_item['func'] + '_o'
        else:
            if func_item['rep_times'] != 1:
                fun_ie = ('%s_f%s_ie%s'%(func_item['func'][0:bit_idx_left_bound], func_item['rep_order'], func_item['func'][bit_idx_left_bound:]))
                fun_i  = ('%s_f%s_i%s' %(func_item['func'][0:bit_idx_left_bound], func_item['rep_order'], func_item['func'][bit_idx_left_bound:]))
                fun_oe = ('%s_f%s_oe%s'%(func_item['func'][0:bit_idx_left_bound], func_item['rep_order'], func_item['func'][bit_idx_left_bound:]))
                fun_o  = ('%s_f%s_o%s' %(func_item['func'][0:bit_idx_left_bound], func_item['rep_order'], func_item['func'][bit_idx_left_bound:]))
            else:
                fun_ie = func_item['func'][0:bit_idx_left_bound] + '_ie' + func_item['func'][bit_idx_left_bound:]
                fun_i  = func_item['func'][0:bit_idx_left_bound] + '_i'  + func_item['func'][bit_idx_left_bound:]
                fun_oe = func_item['func'][0:bit_idx_left_bound] + '_oe' + func_item['func'][bit_idx_left_bound:]
                fun_o  = func_item['func'][0:bit_idx_left_bound] + '_o'  + func_item['func'][bit_idx_left_bound:]

        if io_in == 'i':
            fun_ie = '1\'b1'
        elif io_in == 'x':
            fun_i  = '/*floating*/'
            fun_ie = '1\'b0'
        if io_out == 'o':
            fun_oe = '1\'b1'
        elif io_out == 'x':
            fun_o  = '1\'b0'
            fun_oe = '1\'b0'

        if valid_chk(func_item['default_i']):
            default_i = func_item['default_i']
        else:
            default_i = '1\'b0'

    return fun_ie, fun_i, fun_oe, fun_o, default_i

def inst_io_mux1_cell(io_name, io_element):
    fun_sel_reg = io_element['func_mux'][0]['cfg_reg'] + '[' + io_element['func_mux'][0]['bits'] + ']'

    func_item = io_element['func_mux'][0]
    fun_a_ie, fun_a_i, fun_a_oe, fun_a_o, default_a_i = gen_func_con(func_item)

    if io_element.get('debug') != None:
        dbg_item = {}
        dbg_item['func']      = io_element['debug']
        dbg_item['dir']       = 'c/c'
        dbg_item['default_i'] = '1\'b0'
        dbg_item['rep_times'] = 1
        dbg_item['rep_order'] = 0
        dbg_ie, dbg_i, dbg_oe, dbg_o, default_dbg_i = gen_func_con(dbg_item)
        dbg_en = dbg_oe.replace('oe', 'en')
    else:
        dbg_ie        = '1\'b0'
        dbg_i         = '/*floating*/'
        dbg_oe        = '1\'b0'
        dbg_o         = '1\'b0'
        dbg_en        = '1\'b0'
        default_dbg_i = '1\'b0'

    if io_element.get('testmode1') != None:
        if io_element['testmode1'].find('_i') != -1:
            test_a_i  = io_element['testmode1']
            test_a_ie = '1\'b1'
        else:
            test_a_i  = '/*floating*/'
            test_a_ie = '1\'b0'
        if io_element['testmode1'].find('_o') != -1:
            test_a_o  = io_element['testmode1']
            test_a_oe = '1\'b1'
        else:
            test_a_o  = '1\'b0'
            test_a_oe = '1\'b0'
        default_test_a_i = '1\'b0'
    else:
        test_a_ie        = '1\'b0'
        test_a_i         = '/*floating*/'
        test_a_oe        = '1\'b0'
        test_a_o         = '1\'b0'
        default_test_a_i = '1\'b0'

    if io_element.get('testmode2') != None:
        test_b_i = '/*floating*/'
        test_b_o = '1\'b0'
        if io_element['testmode2'].find('_i') != -1:
            test_b_ie = '1\'b1'
        else:
            test_b_ie = '1\'b0'
        if io_element['testmode2'].find('_o') != -1:
            test_b_oe = '1\'b1'
        else:
            test_b_oe = '1\'b0'
        default_test_b_i = '1\'b0'
    else:
        test_b_ie        = '1\'b0'
        test_b_i         = '/*floating*/'
        test_b_oe        = '1\'b0'
        test_b_o         = '1\'b0'
        default_test_b_i = '1\'b0'

    str = 'io_mux1_cell io_' + io_name.lower() + '(\n'
    str = str + ('    .%-18s(%-20s),\n'%('testmode', 'testmode'))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_en', dbg_en))
    str = str + ('    // function matrix\n')
    str = str + ('    .%-18s(%-20s),\n'%('fun_a_i'    , fun_a_i    ))
    str = str + ('    .%-18s(%-20s),\n'%('fun_a_ie'   , fun_a_ie   ))
    str = str + ('    .%-18s(%-20s),\n'%('fun_a_o'    , fun_a_o    ))
    str = str + ('    .%-18s(%-20s),\n'%('fun_a_oe'   , fun_a_oe   ))
    str = str + ('    .%-18s(%-20s),\n'%('default_a_i', default_a_i))
    str = str + ('    // debug\n')
    str = str + ('    .%-18s(%-20s),\n'%('dbg_i'        , dbg_i        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_ie'       , dbg_ie       ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_o'        , dbg_o        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_oe'       , dbg_oe       ))
    str = str + ('    .%-18s(%-20s),\n'%('default_dbg_i', default_dbg_i))
    str = str + ('    // testmode\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_i'        , test_a_i        , 'test_b_i'        , test_b_i        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_ie'       , test_a_ie       , 'test_b_ie'       , test_b_ie       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_o'        , test_a_o        , 'test_b_o'        , test_b_o        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_oe'       , test_a_oe       , 'test_b_oe'       , test_b_oe       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_test_a_i', default_test_a_i, 'default_test_b_i', default_test_b_i))
    str = str + ('    // cell interface\n')
    str = str + ('    .%-18s(%-20s),\n'%('cell_i' , 'p_' + io_name.lower() + '_i '))
    str = str + ('    .%-18s(%-20s),\n'%('cell_ie', 'p_' + io_name.lower() + '_ie'))
    str = str + ('    .%-18s(%-20s),\n'%('cell_o' , 'p_' + io_name.lower() + '_o '))
    str = str + ('    .%-18s(%-20s) \n'%('cell_oe', 'p_' + io_name.lower() + '_oe'))
    str = str + ('    );\n')

    return str

def inst_io_mux2_cell(io_name, io_element):
    fun_sel_reg = io_element['func_mux'][0]['cfg_reg'] + '[' + io_element['func_mux'][0]['bits'] + ']'

    for func_item in io_element['func_mux']:
        if int(func_item['iomux_cfg'], 2) == 0:
            fun_a_ie, fun_a_i, fun_a_oe, fun_a_o, default_a_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 1:
            fun_b_ie, fun_b_i, fun_b_oe, fun_b_o, default_b_i = gen_func_con(func_item)

    if io_element.get('debug') != None:
        dbg_item = {}
        dbg_item['func']      = io_element['debug']
        dbg_item['dir']       = 'c/c'
        dbg_item['default_i'] = '1\'b0'
        dbg_item['rep_times'] = 1
        dbg_item['rep_order'] = 0
        dbg_ie, dbg_i, dbg_oe, dbg_o, default_dbg_i = gen_func_con(dbg_item)
        dbg_en = dbg_oe.replace('oe', 'en')
    else:
        dbg_ie        = '1\'b0'
        dbg_i         = '/*floating*/'
        dbg_oe        = '1\'b0'
        dbg_o         = '1\'b0'
        dbg_en        = '1\'b0'
        default_dbg_i = '1\'b0'

    if io_element.get('testmode1') != None:
        if io_element['testmode1'].find('_i') != -1:
            test_a_i  = io_element['testmode1']
            test_a_ie = '1\'b1'
        else:
            test_a_i  = '/*floating*/'
            test_a_ie = '1\'b0'
        if io_element['testmode1'].find('_o') != -1:
            test_a_o  = io_element['testmode1']
            test_a_oe = '1\'b1'
        else:
            test_a_o  = '1\'b0'
            test_a_oe = '1\'b0'
        default_test_a_i = '1\'b0'
    else:
        test_a_ie        = '1\'b0'
        test_a_i         = '/*floating*/'
        test_a_oe        = '1\'b0'
        test_a_o         = '1\'b0'
        default_test_a_i = '1\'b0'

    if io_element.get('testmode2') != None:
        test_b_i = '/*floating*/'
        test_b_o = '1\'b0'
        if io_element['testmode2'].find('_i') != -1:
            test_b_ie = '1\'b1'
        else:
            test_b_ie = '1\'b0'
        if io_element['testmode2'].find('_o') != -1:
            test_b_oe = '1\'b1'
        else:
            test_b_oe = '1\'b0'
        default_test_b_i = '1\'b0'
    else:
        test_b_ie        = '1\'b0'
        test_b_i         = '/*floating*/'
        test_b_oe        = '1\'b0'
        test_b_o         = '1\'b0'
        default_test_b_i = '1\'b0'

    str = 'io_mux2_cell io_' + io_name.lower() + '(\n'
    str = str + ('    .%-18s(%-20s),\n'%('testmode', 'testmode'))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_en', dbg_en))
    str = str + ('    .%-18s(%-20s),\n'%('fun_sel', fun_sel_reg))
    str = str + ('    // function matrix\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_i'    , fun_a_i    , 'fun_b_i'    , fun_b_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_ie'   , fun_a_ie   , 'fun_b_ie'   , fun_b_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_o'    , fun_a_o    , 'fun_b_o'    , fun_b_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_oe'   , fun_a_oe   , 'fun_b_oe'   , fun_b_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_a_i', default_a_i, 'default_b_i', default_b_i))
    str = str + ('    // debug\n')
    str = str + ('    .%-18s(%-20s),\n'%('dbg_i'        , dbg_i        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_ie'       , dbg_ie       ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_o'        , dbg_o        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_oe'       , dbg_oe       ))
    str = str + ('    .%-18s(%-20s),\n'%('default_dbg_i', default_dbg_i))
    str = str + ('    // testmode\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_i'        , test_a_i        , 'test_b_i'        , test_b_i        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_ie'       , test_a_ie       , 'test_b_ie'       , test_b_ie       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_o'        , test_a_o        , 'test_b_o'        , test_b_o        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_oe'       , test_a_oe       , 'test_b_oe'       , test_b_oe       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_test_a_i', default_test_a_i, 'default_test_b_i', default_test_b_i))
    str = str + ('    // cell interface\n')
    str = str + ('    .%-18s(%-20s),\n'%('cell_i' , 'p_' + io_name.lower() + '_i '))
    str = str + ('    .%-18s(%-20s),\n'%('cell_ie', 'p_' + io_name.lower() + '_ie'))
    str = str + ('    .%-18s(%-20s),\n'%('cell_o' , 'p_' + io_name.lower() + '_o '))
    str = str + ('    .%-18s(%-20s) \n'%('cell_oe', 'p_' + io_name.lower() + '_oe'))
    str = str + ('    );\n')

    return str

def inst_io_mux4_cell(io_name, io_element):
    fun_sel_reg = io_element['func_mux'][0]['cfg_reg'] + '[' + io_element['func_mux'][0]['bits'] + ']'

    for func_item in io_element['func_mux']:
        if int(func_item['iomux_cfg'], 2) == 0:
            fun_a_ie, fun_a_i, fun_a_oe, fun_a_o, default_a_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 1:
            fun_b_ie, fun_b_i, fun_b_oe, fun_b_o, default_b_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 2:
            fun_c_ie, fun_c_i, fun_c_oe, fun_c_o, default_c_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 3:
            fun_d_ie, fun_d_i, fun_d_oe, fun_d_o, default_d_i = gen_func_con(func_item)

    if io_element.get('debug') != None:
        dbg_item = {}
        dbg_item['func']      = io_element['debug']
        dbg_item['dir']       = 'c/c'
        dbg_item['default_i'] = '1\'b0'
        dbg_item['rep_times'] = 1
        dbg_item['rep_order'] = 0
        dbg_ie, dbg_i, dbg_oe, dbg_o, default_dbg_i = gen_func_con(dbg_item)
        dbg_en = dbg_oe.replace('oe', 'en')
    else:
        dbg_ie        = '1\'b0'
        dbg_i         = '/*floating*/'
        dbg_oe        = '1\'b0'
        dbg_o         = '1\'b0'
        dbg_en        = '1\'b0'
        default_dbg_i = '1\'b0'

    if io_element.get('testmode1') != None:
        if io_element['testmode1'].find('_i') != -1:
            test_a_i  = io_element['testmode1']
            test_a_ie = '1\'b1'
        else:
            test_a_i  = '/*floating*/'
            test_a_ie = '1\'b0'
        if io_element['testmode1'].find('_o') != -1:
            test_a_o  = io_element['testmode1']
            test_a_oe = '1\'b1'
        else:
            test_a_o  = '1\'b0'
            test_a_oe = '1\'b0'
        default_test_a_i = '1\'b0'
    else:
        test_a_ie        = '1\'b0'
        test_a_i         = '/*floating*/'
        test_a_oe        = '1\'b0'
        test_a_o         = '1\'b0'
        default_test_a_i = '1\'b0'

    if io_element.get('testmode2') != None:
        test_b_i = '/*floating*/'
        test_b_o = '1\'b0'
        if io_element['testmode2'].find('_i') != -1:
            test_b_ie = '1\'b1'
        else:
            test_b_ie = '1\'b0'
        if io_element['testmode2'].find('_o') != -1:
            test_b_oe = '1\'b1'
        else:
            test_b_oe = '1\'b0'
        default_test_b_i = '1\'b0'
    else:
        test_b_ie        = '1\'b0'
        test_b_i         = '/*floating*/'
        test_b_oe        = '1\'b0'
        test_b_o         = '1\'b0'
        default_test_b_i = '1\'b0'

    str = 'io_mux4_cell io_' + io_name.lower() + '(\n'
    str = str + ('    .%-18s(%-20s),\n'%('testmode', 'testmode'))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_en', dbg_en))
    str = str + ('    .%-18s(%-20s),\n'%('fun_sel', fun_sel_reg))
    str = str + ('    // function matrix\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_i'    , fun_a_i    , 'fun_b_i'    , fun_b_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_ie'   , fun_a_ie   , 'fun_b_ie'   , fun_b_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_o'    , fun_a_o    , 'fun_b_o'    , fun_b_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_oe'   , fun_a_oe   , 'fun_b_oe'   , fun_b_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_a_i', default_a_i, 'default_b_i', default_b_i))
    str = str + ('    //--------\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_i'    , fun_c_i    , 'fun_d_i'    , fun_d_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_ie'   , fun_c_ie   , 'fun_d_ie'   , fun_d_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_o'    , fun_c_o    , 'fun_d_o'    , fun_d_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_oe'   , fun_c_oe   , 'fun_d_oe'   , fun_d_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_c_i', default_c_i, 'default_d_i', default_d_i))
    str = str + ('    // debug\n')
    str = str + ('    .%-18s(%-20s),\n'%('dbg_i'        , dbg_i        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_ie'       , dbg_ie       ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_o'        , dbg_o        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_oe'       , dbg_oe       ))
    str = str + ('    .%-18s(%-20s),\n'%('default_dbg_i', default_dbg_i))
    str = str + ('    // testmode\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_i'        , test_a_i        , 'test_b_i'        , test_b_i        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_ie'       , test_a_ie       , 'test_b_ie'       , test_b_ie       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_o'        , test_a_o        , 'test_b_o'        , test_b_o        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_oe'       , test_a_oe       , 'test_b_oe'       , test_b_oe       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_test_a_i', default_test_a_i, 'default_test_b_i', default_test_b_i))
    str = str + ('    // cell interface\n')
    str = str + ('    .%-18s(%-20s),\n'%('cell_i' , 'p_' + io_name.lower() + '_i '))
    str = str + ('    .%-18s(%-20s),\n'%('cell_ie', 'p_' + io_name.lower() + '_ie'))
    str = str + ('    .%-18s(%-20s),\n'%('cell_o' , 'p_' + io_name.lower() + '_o '))
    str = str + ('    .%-18s(%-20s) \n'%('cell_oe', 'p_' + io_name.lower() + '_oe'))
    str = str + ('    );\n')

    return str

def inst_io_mux8_cell(io_name, io_element):
    fun_sel_reg = io_element['func_mux'][0]['cfg_reg'] + '[' + io_element['func_mux'][0]['bits'] + ']'

    for func_item in io_element['func_mux']:
        if int(func_item['iomux_cfg'], 2) == 0:
            fun_a_ie, fun_a_i, fun_a_oe, fun_a_o, default_a_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 1:
            fun_b_ie, fun_b_i, fun_b_oe, fun_b_o, default_b_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 2:
            fun_c_ie, fun_c_i, fun_c_oe, fun_c_o, default_c_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 3:
            fun_d_ie, fun_d_i, fun_d_oe, fun_d_o, default_d_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 4:
            fun_e_ie, fun_e_i, fun_e_oe, fun_e_o, default_e_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 5:
            fun_f_ie, fun_f_i, fun_f_oe, fun_f_o, default_f_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 6:
            fun_g_ie, fun_g_i, fun_g_oe, fun_g_o, default_g_i = gen_func_con(func_item)
        elif int(func_item['iomux_cfg'], 2) == 7:
            fun_h_ie, fun_h_i, fun_h_oe, fun_h_o, default_h_i = gen_func_con(func_item)

    if io_element.get('debug') != None:
        dbg_item = {}
        dbg_item['func']      = io_element['debug']
        dbg_item['dir']       = 'c/c'
        dbg_item['default_i'] = '1\'b0'
        dbg_item['rep_times'] = 1
        dbg_item['rep_order'] = 0
        dbg_ie, dbg_i, dbg_oe, dbg_o, default_dbg_i = gen_func_con(dbg_item)
        dbg_en = dbg_oe.replace('oe', 'en')
    else:
        dbg_ie        = '1\'b0'
        dbg_i         = '/*floating*/'
        dbg_oe        = '1\'b0'
        dbg_o         = '1\'b0'
        dbg_en        = '1\'b0'
        default_dbg_i = '1\'b0'

    if io_element.get('testmode1') != None:
        if io_element['testmode1'].find('_i') != -1:
            test_a_i  = io_element['testmode1']
            test_a_ie = '1\'b1'
        else:
            test_a_i  = '/*floating*/'
            test_a_ie = '1\'b0'
        if io_element['testmode1'].find('_o') != -1:
            test_a_o  = io_element['testmode1']
            test_a_oe = '1\'b1'
        else:
            test_a_o  = '1\'b0'
            test_a_oe = '1\'b0'
        default_test_a_i = '1\'b0'
    else:
        test_a_ie        = '1\'b0'
        test_a_i         = '/*floating*/'
        test_a_oe        = '1\'b0'
        test_a_o         = '1\'b0'
        default_test_a_i = '1\'b0'

    if io_element.get('testmode2') != None:
        test_b_i = '/*floating*/'
        test_b_o = '1\'b0'
        if io_element['testmode2'].find('_i') != -1:
            test_b_ie = '1\'b1'
        else:
            test_b_ie = '1\'b0'
        if io_element['testmode2'].find('_o') != -1:
            test_b_oe = '1\'b1'
        else:
            test_b_oe = '1\'b0'
        default_test_b_i = '1\'b0'
    else:
        test_b_ie        = '1\'b0'
        test_b_i         = '/*floating*/'
        test_b_oe        = '1\'b0'
        test_b_o         = '1\'b0'
        default_test_b_i = '1\'b0'

    str = 'io_mux8_cell io_' + io_name.lower() + '(\n'
    str = str + ('    .%-18s(%-20s),\n'%('testmode', 'testmode'))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_en', dbg_en))
    str = str + ('    .%-18s(%-20s),\n'%('fun_sel', fun_sel_reg))
    str = str + ('    // function matrix\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_i'    , fun_a_i    , 'fun_b_i'    , fun_b_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_ie'   , fun_a_ie   , 'fun_b_ie'   , fun_b_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_o'    , fun_a_o    , 'fun_b_o'    , fun_b_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_a_oe'   , fun_a_oe   , 'fun_b_oe'   , fun_b_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_a_i', default_a_i, 'default_b_i', default_b_i))
    str = str + ('    //--------\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_i'    , fun_c_i    , 'fun_d_i'    , fun_d_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_ie'   , fun_c_ie   , 'fun_d_ie'   , fun_d_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_o'    , fun_c_o    , 'fun_d_o'    , fun_d_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_c_oe'   , fun_c_oe   , 'fun_d_oe'   , fun_d_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_c_i', default_c_i, 'default_d_i', default_d_i))
    str = str + ('    //--------\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_e_i'    , fun_e_i    , 'fun_f_i'    , fun_f_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_e_ie'   , fun_e_ie   , 'fun_f_ie'   , fun_f_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_e_o'    , fun_e_o    , 'fun_f_o'    , fun_f_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_e_oe'   , fun_e_oe   , 'fun_f_oe'   , fun_f_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_e_i', default_e_i, 'default_f_i', default_f_i))
    str = str + ('    //--------\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_g_i'    , fun_g_i    , 'fun_h_i'    , fun_h_i    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_g_ie'   , fun_g_ie   , 'fun_h_ie'   , fun_h_ie   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_g_o'    , fun_g_o    , 'fun_h_o'    , fun_h_o    ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('fun_g_oe'   , fun_g_oe   , 'fun_h_oe'   , fun_h_oe   ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_g_i', default_g_i, 'default_h_i', default_h_i))
    str = str + ('    // debug\n')
    str = str + ('    .%-18s(%-20s),\n'%('dbg_i'        , dbg_i        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_ie'       , dbg_ie       ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_o'        , dbg_o        ))
    str = str + ('    .%-18s(%-20s),\n'%('dbg_oe'       , dbg_oe       ))
    str = str + ('    .%-18s(%-20s),\n'%('default_dbg_i', default_dbg_i))
    str = str + ('    // testmode\n')
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_i'        , test_a_i        , 'test_b_i'        , test_b_i        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_ie'       , test_a_ie       , 'test_b_ie'       , test_b_ie       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_o'        , test_a_o        , 'test_b_o'        , test_b_o        ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('test_a_oe'       , test_a_oe       , 'test_b_oe'       , test_b_oe       ))
    str = str + ('    .%-18s(%-20s),    .%-18s(%-20s),\n'%('default_test_a_i', default_test_a_i, 'default_test_b_i', default_test_b_i))
    str = str + ('    // cell interface\n')
    str = str + ('    .%-18s(%-20s),\n'%('cell_i' , 'p_' + io_name.lower() + '_i '))
    str = str + ('    .%-18s(%-20s),\n'%('cell_ie', 'p_' + io_name.lower() + '_ie'))
    str = str + ('    .%-18s(%-20s),\n'%('cell_o' , 'p_' + io_name.lower() + '_o '))
    str = str + ('    .%-18s(%-20s) \n'%('cell_oe', 'p_' + io_name.lower() + '_oe'))
    str = str + ('    );\n')

    return str

with open('./io_matrix.csv', 'r') as f:
    # read title_line
    title_line = f.readline()
    keys = title_line.strip().lower().split(',')
    print('title line')
    print(title_line)

    # read lines
    lines = f.readlines()
    io_matrix = {}
    for line in lines:
        element = attr_match(title_line.lower(), line.lower())
        print('matrix element')
        print(element)
        element['func_mux'] = []                        # add func_mux to element
        io_matrix[element['name']] = element            # add element to io_matrix
        io_matrix[element['name']].pop('name')          # remove 'name' in element since it exists in the key of io_matrix

with open('./io_mux_cfg.csv', 'r') as f:
    # read lines
    lines = f.readlines()
    def_line = ''
    for line in lines:
        keys = line.strip().lower().split(',')
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
            element = attr_match(title_line.lower(), line.lower())
            element['cfg_reg'] = reg_name
            prev_element = element
            def_line = line
        elif keys[0] == '' and keys[1] != '':
            line = prev_element['bits'] + line
            element = attr_match(title_line.lower(), line.lower())
            element['cfg_reg'] = reg_name
            prev_element = element
            def_line = line
        else:
            element = attr_match(title_line.lower(), line.lower(), def_line.lower())
            element['cfg_reg'] = reg_name
            prev_element = element
        print('mux element')
        print(element)
        if valid_chk(element['io_name']):
            io_name = element['io_name']
            element.pop('io_name')
            io_matrix[io_name]['func_mux'].append(element)

print('\n')
print('------------------------------')
print('io_matrix:')
print('------------------------------')
for key in io_matrix:
    print(key,':')
    print(io_matrix[key])
    print('\n')

with open('./io_mux.v', 'w') as f:
    # pre-check
    testmode_set = set([])
    iomux_cfg_set = set([])
    multi_bit_sig_list = {}
    func_rep_list = {}
    dbg_bit_width = 1
    for io_name in sorted(io_matrix):
        # check if func_mux is consistent with function list
        if not func_chk(io_name, io_matrix[io_name]):
            print('*********************************************')
            print('function list check fail!')
            print('*********************************************')
            exit()

        # add to cfg_reg set
        iomux_cfg_set.add(io_matrix[io_name]['func_mux'][0]['cfg_reg'])

        for func_item in io_matrix[io_name]['func_mux']:
            bit_idx_left_bound  = func_item['func'].find('[')
            bit_idx_right_bound = func_item['func'].find(']')

            # find multi bit signals
            if bit_idx_left_bound != -1:
                func_name = func_item['func'][0:bit_idx_left_bound]
                func_bit  = int(func_item['func'][bit_idx_left_bound+1:bit_idx_right_bound])
                if multi_bit_sig_list.get(func_name) != None:
                    multi_bit_sig_list[func_name]['max_bit'] = max(multi_bit_sig_list[func_name]['max_bit'], func_bit)
                    if multi_bit_sig_list[func_name]['dir'] != func_item['dir']:
                        print('*********************************************')
                        print('Warning!')
                        print('function direction is not consistent')
                        print('function: ', func_name)
                        print('direction: ', multi_bit_sig_list[func_name]['dir'])
                        print('direction: ', func_item['dir'])
                        print('*********************************************')
                else:
                    multi_bit_sig_list[func_name] = {}
                    multi_bit_sig_list[func_name]['max_bit'] = func_bit
                    multi_bit_sig_list[func_name]['dir'] = func_item['dir']

            # find replicated function
            if func_rep_list.get(func_item['func']) != None:
                rep_func = func_rep_list[func_item['func']]
                if rep_func['dir'] != func_item['dir'] or rep_func['default_i'] != func_item['default_i']:
                    print('*********************************************')
                    print('Warning!')
                    print('replicate function is not consistent')
                    print('function: ', func_item['func'])
                    print('direction: ', rep_func['dir'])
                    print('direction: ', func_item['dir'])
                    print('default_i: ', rep_func['default_i'])
                    print('default_i: ', func_item['default_i'])
                    print('*********************************************')
                if rep_func['dir'].find('x/') == -1:    # means input is enable
                    func_rep_list[func_item['func']]['rep_times'] = rep_func['rep_times'] + 1
            elif valid_chk(func_item['func']):
                func_rep_list[func_item['func']] = {}
                func_rep_list[func_item['func']]['rep_times'] = 1
                func_rep_list[func_item['func']]['rep_order'] = 0
                func_rep_list[func_item['func']]['dir']       = func_item['dir']
                func_rep_list[func_item['func']]['default_i'] = func_item['default_i']

        if io_matrix[io_name].get('debug') != None and valid_chk(io_matrix[io_name]['debug']):
            dbg_item = io_matrix[io_name]['debug']
            bit_idx_left_bound  = dbg_item.find('[')
            bit_idx_right_bound = dbg_item.find(']')

            # find multi bit signals
            if bit_idx_left_bound != -1:
                dbg_bit = int(dbg_item[bit_idx_left_bound+1:bit_idx_right_bound])
                dbg_bit_width = max(dbg_bit, dbg_bit_width)

        for io_element in sorted(io_matrix[io_name]):
            # add to testmode set
            if io_element[0:8] == 'testmode':
                testmode_set.add(io_element)

    # add replicated attr to func_mux
    for io_name in sorted(io_matrix):
        for func_item in io_matrix[io_name]['func_mux']:
            if valid_chk(func_item['func']):
                rep_func = func_rep_list[func_item['func']]
                func_item['rep_times'] = rep_func['rep_times']
                func_item['rep_order'] = rep_func['rep_order']
                func_rep_list[func_item['func']]['rep_order'] = rep_func['rep_order'] + 1
            else:
                func_item['rep_times'] = 1
                func_item['rep_order'] = 0

    print('\n')
    print('------------------------------')
    print('testmode:')
    print(testmode_set)
    print('------------------------------')
    print('------------------------------')
    print('iomux_cfg_reg:')
    print(iomux_cfg_set)
    print('------------------------------')
    print('------------------------------')
    print('multi bit signal list:')
    print(multi_bit_sig_list)
    print('------------------------------')
    print('------------------------------')
    print('debug signal max_bit:')
    print(dbg_bit_width)
    print('------------------------------')
    print('------------------------------')
    print('function replicate list:')
    print(func_rep_list)
    print('------------------------------')

    #------------------------------------------------
    # formatted RTL output
    #------------------------------------------------

    f.write('module io_mux(\n')

    # global control
    f.write('    // global control\n')
    f.write('    output          %-20s, // <o>  1b,\n'%('clk_ate'))
    for testmode in sorted(testmode_set):
        f.write('    input           %-20s, // <i>  1b,\n'%(testmode))
    for iomux_cfg in sorted(iomux_cfg_set):
        f.write('    input   [31:0]  %-20s, // <i>  1b,\n'%(iomux_cfg))
    f.write('\n')

    # io_matrix signals
    f.write('    // io_matrix signals\n')

    for multi_bit_sig in sorted(multi_bit_sig_list):
        [io_in, io_out] = multi_bit_sig_list[multi_bit_sig]['dir'].split('/')
        func_o  = multi_bit_sig + '_o'
        func_oe = multi_bit_sig + '_oe'
        func_i  = multi_bit_sig + '_i'
        func_ie = multi_bit_sig + '_ie'
        max_bit = multi_bit_sig_list[multi_bit_sig]['max_bit']
        in_declare  = 'input   [' + str(max_bit) + ':0]'
        out_declare = 'output  [' + str(max_bit) + ':0]'
        if io_in == 'c':
            f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare, func_ie, max_bit + 1))
        if io_in != 'x':
            f.write('    %-16s%-20s, // <o> %2sb,\n'%(out_declare, func_i, max_bit + 1))
        if io_out == 'c':
            f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare, func_oe, max_bit + 1))
        if io_out != 'x':
            f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare, func_o, max_bit + 1))

    for io_name in sorted(io_matrix):
        func_mux = io_matrix[io_name]['func_mux']
        for func in func_mux:
            if not valid_chk(func['func']) or func['rep_order'] != 0:
                continue

            [io_in, io_out] = func['dir'].split('/')
            bit_idx_left_bound = func['func'].find('[')
            if bit_idx_left_bound != -1:
                continue

            func_o  = func['func'] + '_o'
            func_oe = func['func'] + '_oe'
            func_i  = func['func'] + '_i'
            func_ie = func['func'] + '_ie'

            in_declare  = 'input'
            out_declare = 'output'
            if io_in == 'c':
                f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare, func_ie, 1))
            if io_in != 'x':
                f.write('    %-16s%-20s, // <o> %2sb,\n'%(out_declare, func_i, 1))
            if io_out == 'c':
                f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare, func_oe, 1))
            if io_out != 'x':
                f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare, func_o, 1))
    f.write('\n')

    # debug signals
    f.write('    // debug signals\n')

    in_declare  = 'input   [' + str(dbg_bit_width) + ':0]'
    out_declare = 'output  [' + str(dbg_bit_width) + ':0]'
    f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare , 'debug_en', dbg_bit_width + 1))
    f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare , 'debug_ie', dbg_bit_width + 1))
    f.write('    %-16s%-20s, // <o> %2sb,\n'%(out_declare, 'debug_i' , dbg_bit_width + 1))
    f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare , 'debug_oe', dbg_bit_width + 1))
    f.write('    %-16s%-20s, // <i> %2sb,\n'%(in_declare , 'debug_o' , dbg_bit_width + 1))
    f.write('\n')

    # test signals
    f.write('    // test signals\n')
    for io_name in sorted(io_matrix):
        for io_element in sorted(io_matrix[io_name]):
            if io_element == 'testmode1' and valid_chk(io_matrix[io_name][io_element]):
                if io_matrix[io_name][io_element].find('_i') != -1:
                    f.write('    %-16s%-20s, // <i> %2sb,\n'%('input', io_matrix[io_name][io_element], 1))
                elif io_matrix[io_name][io_element].find('_o') != -1:
                    f.write('    %-16s%-20s, // <o> %2sb,\n'%('output', io_matrix[io_name][io_element], 1))
                else:
                    print('*********************************************')
                    print(io_name, ':')
                    print('signal name invalid in %s!'%(io_element))
                    print('signal name must end with \'_i\' or \'_o\'')
                    print('-> ', io_matrix[io_name][io_element])
                    print('*********************************************')
    f.write('\n')

    # io signals
    f.write('    // io signals\n')
    io_total_num = len(io_matrix)
    for io_cnt, io_name in enumerate(sorted(io_matrix)):
        f.write('    %-16s%-20s, // <i> %2sb,\n'%('input' , 'p_' + io_name.lower() + '_ie', 1))
        f.write('    %-16s%-20s, // <o> %2sb,\n'%('output', 'p_' + io_name.lower() + '_i' , 1))
        f.write('    %-16s%-20s, // <i> %2sb,\n'%('output', 'p_' + io_name.lower() + '_oe', 1))
        if io_cnt == io_total_num - 1:
            f.write('    %-16s%-20s  // <i> %2sb,\n'%('output', 'p_' + io_name.lower() + '_o' , 1))
        else:
            f.write('    %-16s%-20s, // <i> %2sb,\n'%('output', 'p_' + io_name.lower() + '_o' , 1))

    f.write('    );\n')
    f.write('\n')

    # wire definition
    f.write('    // wire definition\n')
    for rep_func in sorted(func_rep_list):
        rep_times = func_rep_list[rep_func]['rep_times']
        if rep_times > 1:
            for rep_order in range(rep_times):
                wire_name = ('%s_f%s_i'%(rep_func, rep_order))
                f.write('%-8s%-20s;\n'%('wire', wire_name))
    f.write('\n')

    # io_mux_cell instances
    for io_name in sorted(io_matrix):
        func_total_num = len(io_matrix[io_name]['func_mux'])
        if func_total_num == 1:
            str = inst_io_mux1_cell(io_name, io_matrix[io_name])
        elif func_total_num == 2:
            str = inst_io_mux2_cell(io_name, io_matrix[io_name])
        elif func_total_num == 4:
            str = inst_io_mux4_cell(io_name, io_matrix[io_name])
        elif func_total_num == 8:
            str = inst_io_mux8_cell(io_name, io_matrix[io_name])

        f.write(str + '\n')

    str = ''
    for rep_func in sorted(func_rep_list):
        rep_times = func_rep_list[rep_func]['rep_times']
        if rep_times > 1:
            str = str + ('assign %s_i ='%(rep_func))
            if func_rep_list[rep_func]['default_i'][-1] == '0':
                operator = '|'
            elif func_rep_list[rep_func]['default_i'][-1] == '1':
                operator = '&'
            for rep_order in range(rep_times):
                if rep_order == rep_times - 1:
                    str = ('%s %s_f%s_i;\n'%(str, rep_func, rep_order))
                else:
                    str = ('%s %s_f%s_i %s'%(str, rep_func, rep_order, operator))
    str = str + '\n'
    f.write(str)

    f.write('endmodule\n')
