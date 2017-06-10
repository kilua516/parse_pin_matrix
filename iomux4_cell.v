module io_mux4_cell(
    input   [1:0]   testmode          , // <i>  2b, 
    input           dbg_en            , // <i>  1b, 
    input   [1:0]   fun_sel           , // <i>  2b, 
    // function
    output          fun_a_i           , // <o>  1b,
    input           fun_a_ie          , // <i>  1b,
    input           fun_a_o           , // <i>  1b,
    input           fun_a_oe          , // <i>  1b,
    input           default_a_i       , // <i>  1b,
    output          fun_b_i           , // <o>  1b, 
    input           fun_b_ie          , // <i>  1b, 
    input           fun_b_o           , // <i>  1b, 
    input           fun_b_oe          , // <i>  1b, 
    input           default_b_i       , // <i>  1b, 
    output          fun_c_i           , // <o>  1b, 
    input           fun_c_ie          , // <i>  1b, 
    input           fun_c_o           , // <i>  1b, 
    input           fun_c_oe          , // <i>  1b, 
    input           default_c_i       , // <i>  1b, 
    output          fun_d_i           , // <o>  1b, 
    input           fun_d_ie          , // <i>  1b, 
    input           fun_d_o           , // <i>  1b, 
    input           fun_d_oe          , // <i>  1b, 
    input           default_d_i       , // <i>  1b, 
    // debug
    output          dbg_i             , // <o>  1b, 
    input           dbg_ie            , // <i>  1b, 
    input           dbg_o             , // <i>  1b, 
    input           dbg_oe            , // <i>  1b, 
    input           default_dbg_i     , // <i>  1b, 
    // test
    output          test_a_i          , // <o>  1b, 
    input           test_a_ie         , // <i>  1b, 
    input           test_a_o          , // <i>  1b, 
    input           test_a_oe         , // <i>  1b, 
    input           default_test_a_i  , // <i>  1b, 
    output          test_b_i          , // <o>  1b, 
    input           test_b_ie         , // <i>  1b, 
    input           test_b_o          , // <i>  1b, 
    input           test_b_oe         , // <i>  1b, 
    input           default_test_b_i  , // <i>  1b, 
    // io interface
    input           cell_i            , // <i>  1b,
    output          cell_ie           , // <o>  1b,
    output          cell_o            , // <o>  1b,
    output          cell_oe             // <o>  1b,
    );

always @(*) begin
    if (|testmode) begin
        case (testmode)
            2'b01  : cell_o = test_a_o;
            2'b10  : cell_o = test_b_o;
            default: cell_o = 1'b0;
        endcase
    end
    else if (dbg_en) begin
        cell_o = dbg_o;
    end
    else begin
        case (fun_sel[1:0])
            2'b00 : cell_o = fun_a_o;
            2'b01 : cell_o = fun_b_o;
            2'b10 : cell_o = fun_c_o;
            2'b11 : cell_o = fun_d_o;
        endcase
    end
end

always (*) begin
    if (|testmode) begin
        case (testmode)
            2'b01  : cell_oe = test_a_oe;
            2'b10  : cell_oe = test_b_oe;
            default: cell_oe = 1'b0;
        endcase
    end
    else if (dbg_en) begin
        cell_oe = dbg_oe;
    end
    else begin
        case (fun_sel[1:0])
            2'b00 : cell_oe = fun_a_oe;
            2'b01 : cell_oe = fun_b_oe;
            2'b10 : cell_oe = fun_c_oe;
            2'b11 : cell_oe = fun_d_oe;
        endcase
    end
end

always @(*) begin
    if (|testmode) begin
        case (testmode)
            2'b01  : cell_ie = test_a_ie;
            2'b10  : cell_ie = test_b_ie;
            default: cell_ie = 1'b0;
        endcase
    end
    else if (dbg_en) begin
        cell_ie = dbg_ie;
    end
    else begin
        case (fun_sel[1:0])
            2'b00 : cell_ie = fun_a_ie;
            2'b01 : cell_ie = fun_b_ie;
            2'b10 : cell_ie = fun_c_ie;
            2'b11 : cell_ie = fun_d_ie;
        endcase
    end
end

assign fun_a_i = ((testmode = 2'b00) & ~dbg_en & (fun_sel == 2'b00) & fun_a_ie) ? cell_i : default_a_i;
assign fun_b_i = ((testmode = 2'b00) & ~dbg_en & (fun_sel == 2'b01) & fun_b_ie) ? cell_i : default_b_i;
assign fun_c_i = ((testmode = 2'b00) & ~dbg_en & (fun_sel == 2'b10) & fun_c_ie) ? cell_i : default_c_i;
assign fun_d_i = ((testmode = 2'b00) & ~dbg_en & (fun_sel == 2'b11) & fun_d_ie) ? cell_i : default_d_i;
assign dbg_i   = ((testmode = 2'b00) & dbg_en & dbg_ie) ? cell_i : default_dbg_i;
assign test_a_i = (testmode[0] & test_a_ie) ? cell_i : default_test_a_i;
assign test_b_i = (testmode[1] & test_b_ie) ? cell_i : default_test_b_i;

endmodule
