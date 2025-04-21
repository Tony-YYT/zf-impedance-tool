import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Z(f) 電源阻抗估算工具")

st.markdown("""
這個工具可以讓你依據不同的電容器參數（容值、ESL、ESR）模擬整體電源阻抗 Z(f)，
幫助你找到特定頻段的雜訊壓制方法。
""")

# 頻率設定
frequencies = np.logspace(4, 9, num=1000)  # 10 kHz 到 1 GHz
omega = 2 * np.pi * frequencies

# 可設定的電容種類數
num_cap_types = st.slider("選擇不同電容種類數量", 1, 10, 3)

capacitors = []
st.subheader("電容參數設定")

# 安全數值轉換函數
def safe_eval(expr, default):
    try:
        value = eval(expr, {"__builtins__": {}}, {})
        return float(value)
    except:
        return default

for i in range(num_cap_types):
    with st.expander(f"電容種類 {i+1}", expanded=(i < 3)):
        # 常用電容值下拉 + 自訂輸入
        preset_options = {
            "自訂": "",
            "0.1 μF (100nF)": "1e-7",
            "1 μF": "1e-6",
            "10 μF": "1e-5",
            "22 μF": "22e-6",
            "47 μF": "47e-6",
            "100 μF": "100e-6"
        }
        preset_label = st.selectbox(f"選擇常用容值 C{i+1}", list(preset_options.keys()), key=f"presetC{i}")
        C_default = preset_options[preset_label] or "1e-6"
        C_input = st.text_input(f"容值 C{i+1} (F)", value=C_default, key=f"C{i}_text")
        C = safe_eval(C_input, 1e-6)

        # ESL 輸入 (nH)
        L_input = st.text_input(f"ESL L{i+1} (nH)", value="0.8", key=f"L{i}_text")
        L = safe_eval(L_input, 0.8) * 1e-9

        # ESR 輸入 (mΩ)
        R_input = st.text_input(f"ESR R{i+1} (mΩ)", value="10", key=f"R{i}_text")
        R = safe_eval(R_input, 10) * 1e-3

        qty = st.number_input(f"數量 C{i+1}", min_value=1, value=1, step=1, key=f"Q{i}")

        for _ in range(qty):
            capacitors.append({"C": C, "L": L, "R": R})

# 比較模式切換
compare_mode = st.checkbox("啟用比較模式 (保留目前頻譜作為比較)")
if compare_mode:
    st.info("啟用比較後，下方會同時顯示目前與上一版本的 Z(f) 曲線對照。")
    if "Z_previous" not in st.session_state:
        st.session_state.Z_previous = None

# 計算 Z_total
Z_total = np.zeros_like(frequencies, dtype=complex)
for cap in capacitors:
    C, L, R = cap["C"], cap["L"], cap["R"]
    Z = R + 1j * omega * L + 1 / (1j * omega * C)
    Y = 1 / Z
    Z_total += Y
Z_total = 1 / Z_total
Z_mag_mohm = np.abs(Z_total) * 1e3  # 單位轉為 mΩ

# 繪圖
fig, ax = plt.subplots(figsize=(10, 5))
ax.semilogx(frequencies / 1e6, Z_mag_mohm, label="目前 Z(f) (mΩ)", color='blue')

if compare_mode and st.session_state.Z_previous is not None:
    ax.semilogx(frequencies / 1e6, st.session_state.Z_previous, label="前次 Z(f) (mΩ)", color='red', linestyle='--')
    ax.legend()

ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Impedance (mΩ)")
ax.set_title("電容並聯堆疊後的電源阻抗 Z(f)")
ax.grid(True, which="both", ls="--", lw=0.5)

st.pyplot(fig)

# 儲存上一次的頻譜以供比較
if compare_mode:
    st.session_state.Z_previous = Z_mag_mohm

st.markdown("---")
st.caption("Created by ChatGPT – 可即時互動的 Z(f) 頻譜估算工具")
