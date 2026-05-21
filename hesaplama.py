class Hesaplayici:
    @staticmethod
    def malzeme_maliyeti_hesapla(miktar: float, birim_fiyat: float) -> float:
        return miktar * birim_fiyat

    @staticmethod
    def makine_maliyeti_hesapla(makine_suresi: float, makine_saat_ucreti: float) -> float:
        # makine_suresi saat cinsinden varsayılıyor
        return makine_suresi * makine_saat_ucreti

    @staticmethod
    def hurda_degeri_hesapla(miktar: float, fire_orani: float, hurda_birim_fiyati: float) -> float:
        fire_miktari = miktar * (fire_orani / 100)
        return fire_miktari * hurda_birim_fiyati

    @staticmethod
    def teklif_hesapla(malzeme_maliyeti: float, makine_maliyeti: float, ek_gider: float, kar_tipi: str, kar_degeri: float, manuel_indirim: float) -> dict:
        net_maliyet = malzeme_maliyeti + makine_maliyeti + ek_gider
        
        kar_tutari = 0
        if kar_tipi == "Yüzdesel":
            kar_tutari = net_maliyet * (kar_degeri / 100)
        elif kar_tipi == "Sabit":
            kar_tutari = kar_degeri
            
        teklif_tutari = net_maliyet + kar_tutari
        son_tutar = teklif_tutari - manuel_indirim
        
        return {
            "net_maliyet": net_maliyet,
            "kar_tutari": kar_tutari,
            "teklif_tutari": teklif_tutari,
            "son_tutar": son_tutar
        }
