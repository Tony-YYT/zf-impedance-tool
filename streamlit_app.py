
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
num_caps = st.slider("選擇電容數量", 1, 10, 5)

capacitors = []
st.subheader("電容參數設定")

for i in range(num_caps):
    with st.expander(f"電容 {i+1}", expanded=(i < 3)):
        C = st.number_input(f"電容 {i+1} 容值 (F)", value=1e-6, format="%.1e", key=f"C{i}")
        L = st.number_input(f"電容 {i+1} ESL (H)", value=0.8e-9, format="%.1e", key=f"L{i}")
        R = st.number_input(f"電容 {i+1} ESR (Ω)", value=0.01, format="%.2e", key=f"R{i}")
        capacitors.append({"C": C, "L": L, "R": R})

# 計算總阻抗
Z_total = np.zeros_like(frequencies, dtype=complex)
for cap in capacitors:
    C, L, R = cap["C"], cap["L"], cap["R"]
    Z = R + 1j * omega * L + 1 / (1j * omega * C)
    Y = 1 / Z
    Z_total += Y

Z_total = 1 / Z_total
Z_mag_db = 20 * np.log10(np.abs(Z_total))

# 繪圖
fig, ax = plt.subplots(figsize=(10, 5))
ax.semilogx(frequencies / 1e6, Z_mag_db, label="Z(f) Total", color='blue')
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Impedance (dBΩ)")
ax.set_title("電容並聯堆疊後的電源阻抗 Z(f)")
ax.grid(True, which="both", ls="--", lw=0.5)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.legend()
st.pyplot(fig)

st.markdown("---")
st.caption("Created by ChatGPT – 可即時互動的 Z(f) 頻譜估算工具")
