import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Z(f) 電源阻抗估算工具")

st.markdown("""
這個工具可以讓你依據不同的電容器參數（容值、ESL、ESR）模擬整體電源阻抗 Z(f)，
幫助你找到特定頻段的雜訊壓制方法。
""")

# 頻率區間設定
frequencies = np.logspace(4, 9, num=1000)  # 10 kHz 到 1 GHz
omega = 2 * np.pi * frequencies

# 建立可調參數表單
num_caps = st.slider("選擇不同容值的電容種類數量", 1, 10, 3)

capacitors = []
st.subheader("電容參數設定")

unit_options = {"uF": 1e-6, "nF": 1e-9, "pF": 1e-12}

for i in range(num_caps):
    with st.expander(f"電容 {i+1}", expanded=(i < 3)):
        cap_qty = st.number_input(f"電容 {i+1} 使用數量", min_value=1, max_value=100, value=1, step=1, key=f"qty{i}")
        cap_value = st.number_input(f"容值數字 (例如 1, 4.7, 100)", value=1.0, key=f"val{i}")
        cap_unit = st.selectbox(f"容值單位", options=list(unit_options.keys()), index=0, key=f"unit{i}")
        C = cap_value * unit_options[cap_unit]
        L = st.number_input(f"ESL (H)", value=0.8e-9, format="%.2e", key=f"L{i}")
        R = st.number_input(f"ESR (Ω)", value=0.01, format="%.2e", key=f"R{i}")
        for _ in range(cap_qty):
            capacitors.append({"C": C, "L": L, "R": R})

# 比較模式
st.markdown("---")
st.subheader("比較模式")
compare_mode = st.checkbox("啟用比較模式（儲存當前曲線以供對照）")

if 'previous_Z' not in st.session_state:
    st.session_state.previous_Z = None

# 計算總阻抗
Z_total = np.zeros_like(frequencies, dtype=complex)
for cap in capacitors:
    C, L, R = cap["C"], cap["L"], cap["R"]
    Z = R + 1j * omega * L + 1 / (1j * omega * C)
    Y = 1 / Z
    Z_total += Y

Z_total = 1 / Z_total
Z_mag_mohm = 1e3 * np.abs(Z_total)  # 轉換成 mΩ

# 繪圖
fig, ax = plt.subplots(figsize=(10, 5))
ax.semilogx(frequencies / 1e6, Z_mag_mohm, label="Z(f) 現在值", color='blue')

# 如果啟用比較模式，畫出前一次的線
if compare_mode:
    if st.session_state.previous_Z is not None:
        ax.semilogx(frequencies / 1e6, st.session_state.previous_Z, label="Z(f) 前一次", color='red', linestyle='--')
    st.session_state.previous_Z = Z_mag_mohm.copy()

ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Impedance (mΩ)")
ax.set_title("電容並聯堆疊後的電源阻抗 Z(f)")
ax.set_ylim(0, 50000)  # 設定最大值到 50 Ω（= 50,000 mΩ）
ax.grid(True, which="both", ls="--", lw=0.5)
ax.legend()
st.pyplot(fig)

st.markdown("---")
st.caption("Created by ChatGPT – 可即時互動的 Z(f) 頻譜估算工具")
