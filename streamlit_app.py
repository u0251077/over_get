import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period='5d')['Close'].iloc[-1]

def get_exchange_rate(base_currency, target_currency):
    ticker = f'{base_currency}{target_currency}=X'
    return yf.Ticker(ticker).history(period='5d')['Close'].iloc[-1]

def calculate_performance(current_price, reference_price):
    return (current_price - reference_price) / reference_price * 100

def calculate_holding_period(purchase_date):
    return (datetime.now().date() - purchase_date).days

def get_stock_data(stocks):
    usd_twd_rate = get_exchange_rate('USD', 'TWD')
    vwra_price = get_stock_price('VWRA.L')
    
    data = []
    for stock, (count, ref_price, vwra_ref, purchase_date) in stocks.items():
        current_price = get_stock_price(stock) * usd_twd_rate * count
        stock_perf = calculate_performance(current_price, ref_price)
        vwra_perf = calculate_performance(vwra_price, vwra_ref)
        relative_perf = stock_perf - vwra_perf
        holding_period = calculate_holding_period(purchase_date)
        data.append({
            'Stock': stock,
            'Current Value (TWD)': current_price,
            'Reference Value (TWD)': ref_price,
            'Performance (%)': stock_perf,
            'VWRA Performance (%)': vwra_perf,
            'Relative Performance (%)': relative_perf,
            'Purchase Date': purchase_date,
            'Holding Period (days)': holding_period
        })
    return pd.DataFrame(data)

def create_performance_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Stock'], y=df['Performance (%)'], name='Stock Performance'))
    fig.add_trace(go.Bar(x=df['Stock'], y=df['VWRA Performance (%)'], name='VWRA Performance'))
    fig.update_layout(title='Stock vs VWRA Performance', barmode='group', yaxis_title='Performance (%)')
    return fig

def main():
    st.title('Over_get')

    stocks = {
        'NVDA': (9.0, 29666.0, 128.3, datetime(2024, 8, 8).date()),
        'ARM': (52.0, 202458.0, 129.62, datetime(2024, 5, 28).date()),
        'AVUV': (50.0, 144332.0, 131.38, datetime(2024, 6, 27).date()),
        'MTCH': (20.0, 22164.0, 106.32, datetime(2023, 10, 30).date())
    }

    df = get_stock_data(stocks)

    st.subheader('Over_get')
    st.dataframe(df.style.format({
        'Current Value (TWD)': '{:,.2f}',
        'Reference Value (TWD)': '{:,.2f}',
        'Performance (%)': '{:+.2f}%',
        'VWRA Performance (%)': '{:+.2f}%',
        'Relative Performance (%)': '{:+.2f}%',
        'Purchase Date': '{:%Y-%m-%d}',
        'Holding Period (days)': '{:,d}'
    }).background_gradient(subset=['Relative Performance (%)'], cmap='RdYlGn'))

    st.subheader('性能比較圖表')
    st.plotly_chart(create_performance_chart(df))

    st.subheader('詳細數據')
    for _, row in df.iterrows():
        with st.expander(f"{row['Stock']} 詳情"):
            col1, col2, col3 = st.columns(3)
            col1.metric("當前價值", f"${row['Current Value (TWD)']:,.2f}", f"{row['Performance (%)']:+.2f}%")
            col2.metric("相對VWRA表現", f"{row['Relative Performance (%)']:+.2f}%")
            col3.metric("持有期間", f"{row['Holding Period (days']} 天")
            st.write(f"參考價值: ${row['Reference Value (TWD)']:,.2f}")
            st.write(f"購入日期: {row['Purchase Date']:%Y-%m-%d}")

if __name__ == "__main__":
    main()
