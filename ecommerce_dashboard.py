import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime

# Fungsi untuk memuat data
@st.cache(allow_output_mutation=True)
def load_data():
    orders = pd.read_csv('orders_dataset.csv')
    customers = pd.read_csv('customers_dataset.csv')
    order_items = pd.read_csv('order_items_dataset.csv')
    products = pd.read_csv('products_dataset.csv')
    sellers = pd.read_csv('sellers_dataset.csv')
    order_reviews = pd.read_csv('order_reviews_dataset.csv')


    # Data cleaning and merging
    orders['order_approved_at'].fillna(orders['order_purchase_timestamp'], inplace=True)
    products['product_category_name'].fillna('unknown', inplace=True)

    # Convert date columns to datetime
    date_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
                    'order_delivered_customer_date', 'order_estimated_delivery_date']
    for column in date_columns:
        orders[column] = pd.to_datetime(orders[column])


    # Merge datasets
    orders_customers = pd.merge(orders, customers, on='customer_id')
    orders_items_products = pd.merge(order_items, products, on='product_id')
    full_data = pd.merge(orders_customers, orders_items_products, on='order_id')
    full_data = pd.merge(full_data, order_reviews, on='order_id')

    # Add day of week and hour columns
    full_data['order_day'] = full_data['order_purchase_timestamp'].dt.day_name()
    full_data['order_hour'] = full_data['order_purchase_timestamp'].dt.hour

    # Add order_month column
    full_data['order_month'] = full_data['order_purchase_timestamp'].dt.to_period('M')

    # Calculate delivery time
    full_data['delivery_time'] = (full_data['order_delivered_customer_date'] - full_data['order_purchase_timestamp']).dt.days

    return full_data

# Memuat data
data = load_data()

# Pastikan 'order_purchase_timestamp' dalam format datetime dan tambahkan 'order_month'
data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
data['order_month'] = data['order_purchase_timestamp'].dt.to_period('M')

# Sidebar untuk filter
st.sidebar.header('Filter Data')
selected_category = st.sidebar.selectbox('Pilih Kategori Produk', data['product_category_name'].unique())
selected_city = st.sidebar.selectbox('Pilih Kota', data['customer_city'].unique())

# Filter data berdasarkan pilihan pengguna
filtered_data = data[(data['product_category_name'] == selected_category) & (data['customer_city'] == selected_city)]

# Menampilkan logo di dashboard
st.image('logo.2.jpg', width=150)

# Judul aplikasi
st.title('Dashboard Analisis Data E-Commerce')

# Tampilkan data setelah filter
st.write(f"Menampilkan data untuk kategori produk: {selected_category} dan kota: {selected_city}")
st.dataframe(filtered_data)

# Visualisasi pesanan berdasarkan hari dalam seminggu
st.header('Distribusi Pesanan Berdasarkan Hari')
plt.figure(figsize=(12, 6))
sns.countplot(data=filtered_data, x='order_day', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.title('Pesanan Berdasarkan Hari dalam Seminggu')
st.pyplot(plt)

# Visualisasi pesanan berdasarkan jam dalam sehari
st.header('Distribusi Pesanan Berdasarkan Jam')
plt.figure(figsize=(12, 6))
sns.countplot(data=filtered_data, x='order_hour')
plt.title('Pesanan Berdasarkan Jam dalam Sehari')
st.pyplot(plt)

# Top 10 kategori produk berdasarkan penjualan
st.header('Top 10 Kategori Produk Berdasarkan Penjualan')
top_categories = data.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(12, 6))
sns.barplot(x=top_categories.index, y=top_categories.values)
plt.title('Top 10 Kategori Produk Berdasarkan Penjualan')
plt.xticks(rotation=45, ha='right')
st.pyplot(plt)

# Korelasi antara harga dan skor ulasan
st.header('Korelasi Harga dan Skor Ulasan')
plt.figure(figsize=(10, 6))
sns.scatterplot(data=filtered_data, x='price', y='review_score')
plt.title('Korelasi Harga vs Skor Ulasan')
st.pyplot(plt)

# Data RFM Analysis
rfm_data = {
    'customer_unique_id': ['0000366f3b9a7992bf8c76cfdf3221e2', '0000b849f77a49e4a4ce2b2a4ca5be3f',
                           '0000f46a3911fa3c0805444483337064', '0000f6ccb0745a6a4b88665a16c9f078',
                           '0004aac84e0df4da2b147fca70cf8255'],
    'Recency': [115, 118, 541, 325, 292],
    'Frequency': [1, 1, 1, 1, 1],
    'Monetary': [129.90, 18.90, 69.00, 25.99, 180.00]
}

# Membuat DataFrame dari data RFM
rfm_df = pd.DataFrame(rfm_data)

# Menampilkan judul dan metrik RFM
st.title('Best Customer Based on RFM Parameters')

col1, col2, col3 = st.columns(3)

# Menampilkan rata-rata Recency, Frequency, dan Monetary
col1.metric("Average Recency (days)", f"{rfm_df['Recency'].mean():.1f}")
col2.metric("Average Frequency", f"{rfm_df['Frequency'].mean():.2f}")
col3.metric("Average Monetary", f"AUD{rfm_df['Monetary'].mean():,.2f}")

# Menampilkan bar chart horizontal untuk Recency
st.subheader('Recency by Customer')
fig, ax = plt.subplots()
ax.barh(rfm_df['customer_unique_id'], rfm_df['Recency'], color='lightblue')
ax.set_xlabel('Recency (days)')
ax.set_ylabel('customer_unique_id')
ax.set_title('Recency by Customer')
st.pyplot(fig)

# Menampilkan bar chart horizontal untuk Frequency
st.subheader('Frequency by Customer')
fig, ax = plt.subplots()
ax.barh(rfm_df['customer_unique_id'], rfm_df['Frequency'], color='lightgreen')
ax.set_xlabel('Frequency')
ax.set_ylabel('customer_unique_id')
ax.set_title('Frequency by Customer')
st.pyplot(fig)

# Menampilkan bar chart horizontal untuk Monetary
st.subheader('Monetary by Customer')
fig, ax = plt.subplots()
ax.barh(rfm_df['customer_unique_id'], rfm_df['Monetary'], color='lightcoral')
ax.set_xlabel('Monetary (AUD)')
ax.set_ylabel('customer_unique_id')
ax.set_title('Monetary by Customer')
st.pyplot(fig)

# Tren Penjualan Bulanan dari 5 Kategori Produk Teratas
st.header('Tren Penjualan Bulanan dari 5 Kategori Produk Teratas')

# Top 5 categories by sales
top_5_categories = data.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head().index

# Sales trend for top 5 categories per month
category_sales = data[data['product_category_name'].isin(top_5_categories)].groupby(['order_month', 'product_category_name'])['price'].sum().unstack()

# Visualisasi tren penjualan bulanan
fig, ax = plt.subplots(figsize=(12, 6))
category_sales.plot(kind='line', marker='o', ax=ax)
ax.set_title('Monthly Sales Trend for Top 5 Product Categories')
ax.set_xlabel('Month')
ax.set_ylabel('Total Sales')
ax.legend(title='Product Category', bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(fig)

# Footer
st.markdown("Copyright © 2024")
