import yfinance as yafi
import streamlit as st

"""Importerar API-bibliotek yfinance som yafi."""

class Aktieanalys:
    """ Skapar klassen aktienanalys som ska ska hantera 
    huvuddelen av importering samt analys av aktiedata"""

    def __init__(self):
        """ Hanterar solididtetsfilerna från soliditestfilen.
        Sparar informationen i formatet; ticker, soliditet, i ordboken solinfo."""
        self.aktier = {}
        self.marknadsinformation = None

    def ladda_sp500_soliditet(self, soliditetsfil):
        """ Hanterar solididtetsfilerna från soliditestfilen.
        Sparar informationen i formatet; ticker, soliditet, i ordboken solinfo."""
        try:
            with open(soliditetsfil, "r") as fil:
                solinfo = {}
                for rad in fil:
                    ticker, soliditet = rad.strip().split(",")
                    solinfo[ticker] = float(soliditet)
                return solinfo
        except Exception as undantag:
            # Ändrat print till att synas i terminalen ifall filen saknas
            print(f"Kunde inte läsa soliditetsdata från {soliditetsfil}: {undantag}")
            return {}

    def importering_av_aktieinformation(self, ticker, period):
        """Hämtar all aktuell information från yfinance för den angivna perioden.
        resulterar i en dataframe.""Anropar soldiditets funktionen för att hämta ordboken med soliditeten.
        Hämtar stängningskurser från dataframe för den angivna perioden. 
        Sparar all info om aktien i en ordbok, sätter tickern som nyckel till information om den specifika aktien.
        Skapar ett ticker objekt för sp 500 indexet som benämns som "^GSPC" i yfinance.
        History(period=period) hämtar stängningkurserna för den angivna perioden.
        Index info finns fortsätter programmet och beräknar procentuell förändring 
        och gör resultatet till en lista och spara listan till en klass variabel self.marknasinformation."""
        try:
            aktie_information = yafi.Ticker(ticker)
            aktiens_kurshistoria = aktie_information.history(period=period)
            if aktiens_kurshistoria.empty:
                print(f"Kurshistoriken för {ticker} kunde inte laddas.")
                return

            info = aktie_information.info
            namn_på_aktiens_företag = info.get("longName", "Okänt företag")
            pe_Värde = info.get("trailingPE", "N/A")
            ps_Värde = info.get("priceToSalesTrailing12Months", "N/A")

            soliditet_data = self.ladda_sp500_soliditet("sp500_soliditet.txt")
            soliditet = soliditet_data.get(ticker, "N/A")

            priser = aktiens_kurshistoria["Close"].tolist()

            self.aktier[ticker] = {
                "namn_på_aktiens_företag": namn_på_aktiens_företag,
                "pe": pe_Värde,
                "ps": ps_Värde,
                "soliditet": soliditet,
                "priser": priser,
                "beta": None,
            }

            print(f"{namn_på_aktiens_företag} har lagts till i programmet för att analyseras.")
        except Exception as undantag:
            print(f"Kunde inte ladda data för {ticker}: {undantag}")

    def importering_av_marknadsinformation(self, period):
        """Hämtar S&P 500-marknadsinformation för den angivna perioden."""
        try:
            index_information = yafi.Ticker("^GSPC").history(period=period)
            if index_information.empty:
                print("Kunde inte importera S&P 500-indexet.")
            else:
                self.marknadsinformation = index_information["Close"].pct_change().tolist()
                print("S&P 500-marknadsinformationen har importerats framgångsrikt.")
        except Exception as undantag:
            print(f"Kunde inte ladda S&P 500-data: {undantag}")

    def fundamental_långtidsanalys(self, ticker):
        """Hämtar aktiedatan från ordboken self.aktier mha ticker som nicker.
            Metoden .get(ticker) returnrar värdena för den fundamentala analysen."""
        aktie = self.aktier.get(ticker)
        if aktie:
            return (
                f"\nDen fundamentala analysen för {aktie['namn_på_aktiens_företag']}:\n"
                f"Soliditet: {aktie['soliditet']}%\n"
                f"P/E-tal: {aktie['pe']}\n"
                f"P/S-tal: {aktie['ps']}\n"
            )
        else:
            return f"Aktien {ticker} finns inte i systemet."

    def teknisk_korttidsanalys(self, ticker):
        """Skapar en instans av Yafi ticket för den angivna tickern, 
            för att hämta mer detaljerad information från yfinance.
            betavärdet kontrolleras av isinstance ifall det är ett giltigt int tal eller float tal,
            ifall det stämmer sparas det värdet i orboken aktie med nyckeln "aktie".
            Listan med stängningskurserna hämtas från "aktie", med nyckeln priser.
            Kursurvecklingen beräknas i procent 
            ((sista dagen i perioden)-(första dagen i perioden))/(första dagen i period)).
            Lägsta occh högsta kurvärdet för perioden hämtas."""
        aktie = self.aktier.get(ticker)
        if aktie:
            try:
                aktie_information = yafi.Ticker(ticker)
                aktiens_betavärde = aktie_information.info.get("beta", None)

                if isinstance(aktiens_betavärde, (int, float)):
                    aktie["beta"] = aktiens_betavärde
                else:
                    return "Beta-värdet är inte tillgängligt."

            except Exception as undantag:
                print(f"Fel vid hämtning av data för {ticker}: {undantag}")
                return "Fel vid hämtning av teknisk data."

            priser = aktie["priser"]
            if priser and len(priser) > 1:
                utveckling = ((priser[-1] - priser[0]) / priser[0]) * 100
                return (
                    f"Kursutveckling: {utveckling:.2f}%\n"
                    f"Högsta kursvärde: {max(priser)}\n"
                    f"Lägsta kursvärde: {min(priser)}")
            else:
                return "För lite data för teknisk analys."
        else:
            return f"Aktien {ticker} finns inte i systemet."

    def ordnar_aktierna_beroende_på_beta(self):
        """List comprehension för att skapa en lista med tuples i formatet (ticker, beta-värde).
            self.aktier.items() returnerar alla aktier i form av (ticker, information) där information är en dictionary med data om aktien.
            if information["beta"] is not None filtrerar bort de aktier som inte har ett beta-värde (de med None som beta).
            Listan med betavärde sorteras, key=lambda säger att ska ske på bröja på det andra betavärdet.
            Reverse treu gör att värdena ordnas från störst till minst """
        betavärden = [(ticker, info["beta"]) for ticker, info in self.aktier.items() if info["beta"] is not None]
        betavärden.sort(key=lambda x: x[1], reverse=True)

        if betavärden:
            result = "\nAktier sorterade efter beta-värde:\n"
            for i, (ticker, beta) in enumerate(betavärden, 1):
                result += f"{i}. {ticker}: {beta:.2f}\n"
            return result
        else:
            return "Inga beta-värden tillgängliga."


# ==========================================
# ERSÄTTER TKINTER MED STREAMLIT-GRÄNSSNITT
# ==========================================

st.title("Liptos Aktieanalys Program")

# Ladda in logiken och "kom ihåg" den mellan knapptryck
if 'analys' not in st.session_state:
    st.session_state.analys = Aktieanalys()

st.subheader("1. Lägg till aktier")
col1, col2 = st.columns(2)

with col1:
    inmatad_ticker = st.text_input("Ange ticker/förkortning (t.ex. AAPL):").upper()
with col2:
    inmatad_period = st.text_input("Ange period (ex. 1mo, 1y, max):", "1mo")

if st.button("Tillägg av aktier"):
    if inmatad_ticker and inmatad_period:
        with st.spinner(f"Hämtar data för {inmatad_ticker}..."):
            st.session_state.analys.importering_av_aktieinformation(inmatad_ticker, inmatad_period)
            st.session_state.analys.importering_av_marknadsinformation(inmatad_period)
        
        if inmatad_ticker in st.session_state.analys.aktier:
            st.success(f"Aktien {inmatad_ticker} har lagts till i programmet!")
        else:
            st.error("Kunde inte hämta data. Kontrollera att tickern är korrekt.")
    else:
        st.warning("Vänligen fyll i både ticker och period.")

st.divider()

st.subheader("2. Analysera aktier")
analys_ticker = st.text_input("Ange ticker för analys (måste vara tillagd ovan):").upper()

col3, col4, col5 = st.columns(3)

if col3.button("Fundamental analys"):
    if analys_ticker:
        svar = st.session_state.analys.fundamental_långtidsanalys(analys_ticker)
        st.text(svar)
    else:
        st.warning("Ange en ticker först.")

if col4.button("Teknisk analys"):
    if analys_ticker:
        with st.spinner("Beräknar..."):
            svar = st.session_state.analys.teknisk_korttidsanalys(analys_ticker)
        st.text(svar)
    else:
        st.warning("Ange en ticker först.")

if col5.button("Ordna aktier efter beta"):
    with st.spinner("Sorterar..."):
        svar = st.session_state.analys.ordnar_aktierna_beroende_på_beta()
    st.text(svar)

st.divider()
st.write("Sparade aktier i minnet:", list(st.session_state.analys.aktier.keys()))