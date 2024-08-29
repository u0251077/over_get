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

@st.cache_data(ttl=3600)  # 缓存数据1小时
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
    fig.update_layout(
        title='Stock vs VWRA Performance',
        barmode='group',
        yaxis_title='Performance (%)',
        hovermode='x unified'
    )
    return fig

def calculate_portfolio_performance(df):
    total_current_value = df['Current Value (TWD)'].sum()
    total_reference_value = df['Reference Value (TWD)'].sum()
    portfolio_performance = (total_current_value - total_reference_value) / total_reference_value * 100
    
    # 計算VWRA的加權平均表現
    vwra_weighted_performance = (df['VWRA Performance (%)'] * df['Reference Value (TWD)']).sum() / total_reference_value
    
    excess_return = portfolio_performance - vwra_weighted_performance
    
    return portfolio_performance, vwra_weighted_performance, excess_return


@st.cache_data(ttl=3600)  # 缓存数据1小时
def get_stock_data(stocks):
    usd_twd_rate = get_exchange_rate('USD', 'TWD')
    vwra_price = get_stock_price('VWRA.L')
    
    data = []
    total_investment = 0
    total_current_value = 0
    total_vwra_value = 0
    
    for stock, (count, ref_price, vwra_ref, purchase_date) in stocks.items():
        current_price = get_stock_price(stock) * usd_twd_rate * count
        stock_perf = calculate_performance(current_price, ref_price)
        vwra_perf = calculate_performance(vwra_price, vwra_ref)
        relative_perf = stock_perf - vwra_perf
        holding_period = calculate_holding_period(purchase_date)
        
        total_investment += ref_price
        total_current_value += current_price
        total_vwra_value += (ref_price / vwra_ref) * vwra_price
        
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
    
    portfolio_perf = (total_current_value - total_investment) / total_investment * 100
    vwra_total_perf = (total_vwra_value - total_investment) / total_investment * 100
    excess_return = portfolio_perf - vwra_total_perf
    
    return pd.DataFrame(data), portfolio_perf, vwra_total_perf, excess_return

def create_performance_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Stock'], y=df['Performance (%)'], name='股票表现'))
    fig.add_trace(go.Bar(x=df['Stock'], y=df['VWRA Performance (%)'], name='VWRA表现'))
    fig.update_layout(
        title='股票 vs VWRA 表现',
        barmode='group',
        yaxis_title='表现 (%)',
        hovermode='x unified'
    )
    return fig

def create_holding_period_chart(df):
    fig = go.Figure(go.Bar(x=df['Stock'], y=df['Holding Period (days)'], name='持有期间'))
    fig.update_layout(
        title='持有期间',
        yaxis_title='天数',
        hovermode='x unified'
    )
    return fig

def main():
    st.set_page_config(page_title="Over_get", page_icon="📊", layout="wide")
    st.title('我的投資組合')

    stocks = {
        'NVDA': (9.0, 29666.0, 128.3, datetime(2024, 8, 8).date()),
        'ARM': (52.0, 202458.0, 129.62, datetime(2024, 5, 28).date()),
        'AVUV': (50.0, 144332.0, 131.38, datetime(2024, 6, 27).date()),
        'MTCH': (20.0, 22164.0, 106.32, datetime(2023, 10, 30).date())
    }

    with st.spinner('正在获取最新数据...'):
        df, portfolio_perf, vwra_total_perf, excess_return = get_stock_data(stocks)

    st.subheader('投資組合總覽')
    col1, col2, col3 = st.columns(3)
    col1.metric("投資組合總收益", f"{portfolio_perf:+.2f}%")
    col2.metric("VWRA大盤收益", f"{vwra_total_perf:+.2f}%")
    col3.metric("超額報酬", f"{excess_return:+.2f}%", 
                delta_color="normal" if excess_return >= 0 else "inverse")

    tab1, tab2, tab3 = st.tabs(["详细数据", "性能比较", "持有期间"])

    with tab1:
        st.dataframe(df.style.format({
            'Current Value (TWD)': '${:,.2f}',
            'Reference Value (TWD)': '${:,.2f}',
            'Performance (%)': '{:+.2f}%',
            'VWRA Performance (%)': '{:+.2f}%',
            'Relative Performance (%)': '{:+.2f}%',
            'Purchase Date': '{:%Y-%m-%d}',
            'Holding Period (days)': '{:,d}'
        }).background_gradient(subset=['Relative Performance (%)'], cmap='RdYlGn'))

    with tab2:
        st.plotly_chart(create_performance_chart(df), use_container_width=True)

    with tab3:
        st.plotly_chart(create_holding_period_chart(df), use_container_width=True)

    st.subheader('股票详情')
    for _, row in df.iterrows():
        with st.expander(f"{row['Stock']} 详情", expanded =True):
            col1, col2, col3 = st.columns(3)
            col1.metric("当前价值", f"${row['Current Value (TWD)']:,.2f}", f"{row['Performance (%)']:+.2f}%")
            col2.metric("相对VWRA表现", f"{row['Relative Performance (%)']:+.2f}%")
            col3.metric("持有期间", f"{row['Holding Period (days)']:,d} 天")
            st.write(f"参考价值: ${row['Reference Value (TWD)']:,.2f}")
            st.write(f"购入日期: {row['Purchase Date']:%Y-%m-%d}")

if __name__ == "__main__":
    main()

