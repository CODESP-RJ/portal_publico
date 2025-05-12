from .base_validator import BaseValidator

class ItensNotaFiscalValidator(BaseValidator):
    def validar_cod_mat_serv(self):
        for idx, row in self.df.iterrows():
            codigo = row['COD_MAT_SERV']
            if not self._consultar_api_codigo_valido(codigo):
                self._registrar_erro(idx, f"Código {codigo} inválido ou não encontrado na API")

    def _consultar_api_codigo_valido(self, codigo):
        # Implemente a consulta à API aqui
        return True

    def validar_especifico(self):
        self.validar_cod_mat_serv()
