import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text


engine = create_engine('postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c')

create_table_query = """
                    CREATE TABLE IF NOT EXISTS stock_index (
                        trading_date DATE,
                        stock_code VARCHAR(20),
                        reference_price NUMERIC,
                        opening_price NUMERIC,
                        closing_price NUMERIC,
                        highest_price NUMERIC,
                        lowest_price NUMERIC,
                        average_price NUMERIC,
                        price_change NUMERIC,
                        price_change_percentage NUMERIC,
                        matched_orders_volume BIGINT,
                        matched_orders_value BIGINT,
                        total_trading_volume BIGINT,
                        total_trading_value BIGINT,
                        market_capitalization DECIMAL(20, 2),
                        PRIMARY KEY (trading_date, stock_code)
                    );
    """
with engine.connect() as connection:
    connection.execute(text(create_table_query))