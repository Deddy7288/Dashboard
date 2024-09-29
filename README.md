## Run streamlit app using conda

```bash
# Membuat environment conda baru dengan Python 3.6.12
conda create --name streamlit_env python=3.6.12

# Mengaktifkan environment conda
conda activate streamlit_env

# Install dependencies dari file requirements.txt
pip install -r requirements.txt

# Menjalankan aplikasi Streamlit
streamlit run ecommerce_dashboard.py
