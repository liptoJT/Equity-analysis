import streamlit as st
import yfinance as yf

st.title("Equity Analysis Program")
st.write("Här kan du analysera aktier direkt i webbläsaren!")

# En textruta där användaren kan skriva en aktiesymbol (t.ex. AAPL eller ERIC-B.ST)
ticker = st.text_input("Ange aktiesymbol (t.ex. AAPL):", "AAPL")

if ticker:
    st.write(f"Hämtar data för {ticker}...")
    
    # Hämta aktiedata via yfinance (samma logik som du säkert har i din kod)
    aktie = yf.Ticker(ticker)
    hist = aktie.history(period="1mo")
    
    # Visa data i en tabell på skbsan
    st.subheader("Historisk prisdata")
    st.dataframe(hist)
    
    # Rita en snygg graf direkt
    st.subheader("Prisutveckling")
    st.line_chart(hist['Close'])