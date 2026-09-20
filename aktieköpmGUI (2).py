import yfinance as yafi
import tkinter as kint
from tkinter import simpledialog

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

class AktieanalysGUI:
    """kint.Text är en widget inom tkinter, den använda för att visa eller redigera tex. Texten uppfattas som rad.kolumn där 1.0 är start,
    och kint.END är slutet. Simpledialog.askstring("titel, fråga") öppnar en ruta som användaren kan interagera med (input funktion). 
    Exempelvis ("Input", "Ange ticker/förkortning för en aktie"). Texten i kint.Text kan manipuleras m.h.a funtkioner som delete(start, end) för att ta bort eller 
    insert(position, text) för att lägga till text."""
    def __init__(self, root):
        self.analys = Aktieanalys()
        self.root = root
        self.root.title("Liptos Aktieanalys Program")

        #pady= avstånd i antalet, vertikalt
        #kint.Button= funktion inom tkinter för att göra en knapp
        self.lägg_till_aktier_knapp = kint.Button(root, text="Tillägg av aktier", command=self.lägg_till_aktier)
        self.lägg_till_aktier_knapp.pack(pady=5)

        self.fundamental_analys_knapp = kint.Button(root, text="Fundamental analys", command=self.fundamental_analys)
        self.fundamental_analys_knapp.pack(pady=5)

        self.teknisk_analys_knapp = kint.Button(root, text="Teknisk analys", command=self.teknisk_analys)
        self.teknisk_analys_knapp.pack(pady=5)

        self.sortera_betavärde_knapp = kint.Button(root, text="Ordna aktier efter beta", command=self.sortering_betabaserat)
        self.sortera_betavärde_knapp.pack(pady=5)

        self.avslutningsknapp = kint.Button(root, text="Avsluta", command=root.quit)
        self.avslutningsknapp.pack(pady=5)

        # Text widget för att visa data
        self.text_svar = kint.Text(root, height=15, width=50)
        self.text_svar.pack(pady=10)

    def lägg_till_aktier(self):
        ticker = simpledialog.askstring("Input", "Ange ticker/förkortningen för en aktie:").upper()
        period = simpledialog.askstring("Input", "Ange period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, 10y, ytd, max.):")
        if ticker and period:
            self.analys.importering_av_aktieinformation(ticker, period)
            self.analys.importering_av_marknadsinformation(period)

    def fundamental_analys(self):
        ticker = simpledialog.askstring("Input", "Ange ticker/förkortningen för en aktie:").upper()
        if ticker:
            result = self.analys.fundamental_långtidsanalys(ticker)
            self.text_svar.delete(1.0, kint.END)
            self.text_svar.insert(kint.END, result)

    def teknisk_analys(self):
        ticker = simpledialog.askstring("Input", "Ange ticker/förkortningen för en aktie:").upper()
        if ticker:
            result = self.analys.teknisk_korttidsanalys(ticker)
            self.text_svar.delete(1.0, kint.END)
            self.text_svar.insert(kint.END, result)

    def sortering_betabaserat(self):
        result = self.analys.ordnar_aktierna_beroende_på_beta()
        self.text_svar.delete(1.0, kint.END)
        self.text_svar.insert(kint.END, result)


if __name__ == "__main__":
    root = kint.Tk()
    app = AktieanalysGUI(root)
    root.mainloop()