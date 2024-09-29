# Run streamlit app using conda
conda create --name streamlit_env python=3.6.12
conda activate streamli_env
pip install -r requirements.txt
streamlit ecommerce_dashboard.py
