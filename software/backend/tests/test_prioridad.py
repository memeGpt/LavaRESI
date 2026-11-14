
# Ejecución desde software/backend: python -m unittest discover -s tests -v
import unittest
from unittest.mock import patch
from app.servicios import prolog, turnos

def solicitud(id, estado='EN_ESPERA', disponible=1, iniciadas=0, total=1, maquina=1):
    return dict(id=id, maquina_id=maquina, estado=estado,
                disponible=disponible, tandas_iniciadas=iniciadas,
                tandas_totales=total)

def consulta(estado, solicitudes, accion='SIGUIENTE', sid=None, n=None, maquina=1):
    d=dict(accion=accion, maquina_id=maquina, estado_maquina=estado,
           solicitudes=solicitudes)
    if sid is not None: d['solicitud_id']=sid
    if n is not None: d['numero_tanda']=n
    return prolog._respaldo(d)

class Prioridad(unittest.TestCase):
    def test_ausente_se_salta(self):
        r=consulta('LIBRE',[solicitud(4,disponible=0),solicitud(5)])
        self.assertEqual(r.get('solicitud_id'),5)

    def test_retorno_antes_inicio_recupera_prioridad(self):
        r=consulta('LIBRE',[solicitud(4),solicitud(5,estado='AUTORIZADA')])
        self.assertEqual(r.get('solicitud_id'),4)

    def test_en_uso_no_se_interrumpe(self):
        r=consulta('EN_USO',[solicitud(4),solicitud(5,estado='EN_USO',iniciadas=1)])
        self.assertEqual(r.get('accion'),'MANTENER')
        self.assertEqual(r.get('solicitud_id'),5)

    def test_regreso_tras_retiro_final(self):
        r=consulta('LIBRE',[solicitud(4),solicitud(6)])
        self.assertEqual(r.get('solicitud_id'),4)

    def test_bloqueo_durante_retiro(self):
        r=consulta('PENDIENTE_RETIRO',[solicitud(4),solicitud(5,'EN_USO',iniciadas=1)])
        self.assertEqual(r.get('accion'),'MANTENER')

    def test_inicio_adelantado_rechazado_al_regresar_primero(self):
        r=consulta('LIBRE',[solicitud(4),solicitud(5,'AUTORIZADA')],accion='INICIAR',sid=5,n=1)
        self.assertFalse(r.get('permitido'))

    def test_inicio_primero_aceptado(self):
        r=consulta('LIBRE',[solicitud(4),solicitud(5,'AUTORIZADA')],accion='INICIAR',sid=4,n=1)
        self.assertTrue(r.get('permitido'))

    def test_maquinas_independientes(self):
        r=consulta('LIBRE',[solicitud(4,maquina=1),solicitud(9,maquina=2)],maquina=2)
        self.assertEqual(r.get('solicitud_id'),9)

    def test_dos_ausentes_pasa_tercero_disponible(self):
        # Justin y Grace ausentes; Jareth es el primero disponible.
        cola = [solicitud(4, disponible=0), solicitud(5, disponible=0), solicitud(6)]
        r = consulta('LIBRE', cola)
        self.assertEqual(r.get('solicitud_id'), 6)

    def test_grace_regresa_y_jareth_sigue_lavando(self):
        # Grace reaparece, pero Jareth ya empezó: nadie lo interrumpe.
        cola = [solicitud(4, disponible=0), solicitud(5, disponible=1),
                solicitud(6, estado='EN_USO', iniciadas=1)]
        r = consulta('EN_USO', cola)
        self.assertEqual((r.get('accion'), r.get('solicitud_id')), ('MANTENER', 6))

    def test_jareth_termina_justin_ausente_grace_disponible(self):
        # Tras el retiro final, Justin sigue ausente: pasa Grace.
        cola = [solicitud(4, disponible=0), solicitud(5, disponible=1)]
        r = consulta('LIBRE', cola)
        self.assertEqual(r.get('solicitud_id'), 5)

    def test_jareth_termina_justin_regreso_grace_disponible(self):
        # Justin regresó: conserva la prioridad anterior a Grace.
        cola = [solicitud(4, disponible=1), solicitud(5, disponible=1)]
        r = consulta('LIBRE', cola)
        self.assertEqual(r.get('solicitud_id'), 4)

    def test_todos_ausentes_maquina_espera(self):
        cola = [solicitud(4, disponible=0), solicitud(5, disponible=0)]
        r = consulta('LIBRE', cola)
        self.assertEqual(r.get('accion'), 'ESPERAR')

    def test_reasignacion_persiste_en_bd(self):
        class Resultado:
            def fetchone(self): return {'id':4,'estado':'EN_ESPERA','usuario_id':7}

        class Conn:
            def __init__(self): self.calls=[]

            def execute(self, sql, params):
                self.calls.append((sql,params))
                return Resultado()

        conn=Conn()
        with patch.object(turnos,'_consultar',return_value={'accion':'AUTORIZAR','solicitud_id':4}), \
             patch.object(turnos,'notificar') as notificar:
            turnos.asignar_siguiente(conn,1)

        self.assertTrue(any("estado = 'EN_ESPERA'" in sql and p==(1,4) for sql,p in conn.calls))
        self.assertTrue(any("estado = 'AUTORIZADA'" in sql and p==(4,) for sql,p in conn.calls))
        notificar.assert_called_once()

if __name__=='__main__': unittest.main()
