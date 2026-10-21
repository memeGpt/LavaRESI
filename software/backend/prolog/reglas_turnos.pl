% LavaRESI - Motor de reglas de turnos (SWI-Prolog)
% Modelo: 1 lavadora (id 1), 1 secadora (id 2).
% No modifica la base de datos ni valida PIN: eso corresponde al backend.
% Recibe un JSON por stdin y devuelve una decision JSON por stdout.
%
% Acciones: SIGUIENTE, INICIAR, RETIRAR.
% Estado de maquina: LIBRE, EN_USO, PENDIENTE_RETIRO, ENTRE_TANDAS.
% Estado de solicitud: EN_ESPERA, AUTORIZADA, EN_USO, FINALIZADA, CANCELADA.
%
% Orden estable: id de solicitud ascendente (representa orden de llegada).
% Al ausentarse alguien no pierde su id/puesto; se lo omite temporalmente.
% Una vez iniciado un turno, conserva la maquina hasta confirmar ultimo retiro.
% Lavadora y secadora se resuelven de forma independiente.

:- module(reglas_turnos, [resolver/2, main/0]).
:- use_module(library(http/json)).
:- use_module(library(lists)).

% ---- Validacion minima del contrato enviado por FastAPI ----
estado_maquina('LIBRE').
estado_maquina('EN_USO').
estado_maquina('PENDIENTE_RETIRO').
estado_maquina('ENTRE_TANDAS').
estado_solicitud('EN_ESPERA').
estado_solicitud('AUTORIZADA').
estado_solicitud('EN_USO').
estado_solicitud('FINALIZADA').
estado_solicitud('CANCELADA').

dato_valido(S) :-
    is_dict(S),
    get_dict(id, S, Id), integer(Id), Id > 0,
    get_dict(maquina_id, S, M), memberchk(M, [1, 2]),
    get_dict(estado, S, E), estado_solicitud(E),
    get_dict(disponible, S, D), memberchk(D, [0, 1]),
    get_dict(tandas_totales, S, T), integer(T), between(1, 3, T),
    get_dict(tandas_iniciadas, S, I), integer(I), between(0, T, I).

entrada_valida(D) :-
    is_dict(D),
    get_dict(accion, D, A), memberchk(A, ['SIGUIENTE', 'INICIAR', 'RETIRAR']),
    get_dict(maquina_id, D, M), memberchk(M, [1, 2]),
    get_dict(estado_maquina, D, E), estado_maquina(E),
    get_dict(solicitudes, D, Solicitudes), is_list(Solicitudes),
    maplist(dato_valido, Solicitudes).

% Conservamos el orden de solicitud: ausentarse no cambia su prioridad.
solicitudes_ordenadas(Lista, Ordenadas) :-
    findall(Id-S, (member(S, Lista), get_dict(id, S, Id)), Pares),
    keysort(Pares, Ordenados),
    findall(S, member(_-S, Ordenados), Ordenadas).

solicitud_maquina(M, S) :- get_dict(maquina_id, S, M).

ocupante(M, Lista, S) :-
    member(S, Lista), solicitud_maquina(M, S),
    get_dict(estado, S, 'EN_USO'), !.

reserva(M, Lista, S) :-
    solicitudes_ordenadas(Lista, Ordenadas),
    member(S, Ordenadas), solicitud_maquina(M, S),
    get_dict(estado, S, 'AUTORIZADA'), !.

elegible(M, Lista, S) :-
    solicitudes_ordenadas(Lista, Ordenadas),
    member(S, Ordenadas), solicitud_maquina(M, S),
    get_dict(estado, S, 'EN_ESPERA'),
    get_dict(disponible, S, 1),
    get_dict(tandas_iniciadas, S, 0), !.

% ---- Decision de siguiente turno ----
% Los estados EN_USO, PENDIENTE_RETIRO y ENTRE_TANDAS bloquean la maquina.
% AUTORIZADA es una reserva ya concedida: no se asigna a otro hasta revisarla.
% Respuesta con accion AUTORIZAR solo expresa la decision: Python debe persistirla.
siguiente(D, R) :-
    get_dict(maquina_id, D, M),
    get_dict(estado_maquina, D, Estado),
    get_dict(solicitudes, D, Lista),
    ( Estado \= 'LIBRE' ->
        ( ocupante(M, Lista, S) ->
            get_dict(id, S, Id),
            R = _{accion:'MANTENER', solicitud_id:Id, motivo:'MAQUINA_OCUPADA'}
        ; R = _{accion:'ESPERAR', motivo:'MAQUINA_OCUPADA_SIN_TURNO_VALIDO'}
        )
    ; ocupante(M, Lista, _) ->
        R = _{accion:'ESPERAR', motivo:'ESTADO_INCONSISTENTE_OCUPANTE'}
    ; reserva(M, Lista, Reservada) ->
        get_dict(id, Reservada, Id),
        ( get_dict(disponible, Reservada, 1) ->
            R = _{accion:'AUTORIZAR', solicitud_id:Id, motivo:'RESERVA_EXISTENTE'}
        ; R = _{accion:'ESPERAR', motivo:'REVISAR_RESERVA_NO_DISPONIBLE'}
        )
    ; elegible(M, Lista, S) ->
        get_dict(id, S, Id),
        R = _{accion:'AUTORIZAR', solicitud_id:Id, motivo:'PRIMER_DISPONIBLE'}
    ; R = _{accion:'ESPERAR', motivo:'SIN_SOLICITUDES_DISPONIBLES'}
    ).

% ---- Verificar si una tanda concreta puede empezar ----
% Tanda 1: maquina LIBRE, usuario primero elegible y aun sin tandas iniciadas.
% Tanda 2/3: maquina ENTRE_TANDAS, mismo ocupante, previa ropa retirada.
% El backend cambia a ENTRE_TANDAS solamente al confirmar retiro intermedio.
iniciar(D, R) :-
    get_dict(maquina_id, D, M),
    get_dict(estado_maquina, D, Estado),
    get_dict(solicitudes, D, Lista),
    ( get_dict(solicitud_id, D, Id), integer(Id), Id > 0,
      get_dict(numero_tanda, D, N), integer(N), between(1, 3, N),
      member(S, Lista), get_dict(id, S, Id), solicitud_maquina(M, S),
      get_dict(tandas_iniciadas, S, Previas),
      get_dict(tandas_totales, S, Total),
      N =:= Previas + 1, N =< Total,
      ( ( Estado == 'LIBRE', N =:= 1, Previas =:= 0,
          siguiente(D, Elegido), get_dict(accion, Elegido, 'AUTORIZAR'),
          get_dict(solicitud_id, Elegido, Id)
        )
      ; ( Estado == 'ENTRE_TANDAS',
          get_dict(estado, S, 'EN_USO'),
          ocupante(M, Lista, Titular), get_dict(id, Titular, Id)
        )
      )
    -> R = _{permitido:true, motivo:'INICIO_AUTORIZADO'}
    ;  R = _{permitido:false, motivo:'NO_ES_SU_TURNO_O_TANDA_INVALIDA'}
    ).

% ---- Confirmar retiro al terminar una tanda ----
% El backend verifica el PIN, la pertenencia de la solicitud, y que el
% ciclo haya finalizado. Prolog solo decide si se conserva o libera el turno.
retirar(D, R) :-
    get_dict(maquina_id, D, M),
    get_dict(estado_maquina, D, Estado),
    get_dict(solicitudes, D, Lista),
    ( Estado == 'PENDIENTE_RETIRO',
      get_dict(solicitud_id, D, Id), integer(Id),
      ocupante(M, Lista, S), get_dict(id, S, Id),
      get_dict(tandas_iniciadas, S, I), I > 0,
      get_dict(tandas_totales, S, T)
    -> ( I < T ->
            R = _{permitido:true, resultado:'CONTINUAR_TANDAS',
                  motivo:'CONSERVA_TURNO'}
       ;    R = _{permitido:true, resultado:'LIBERAR_MAQUINA',
                  motivo:'ULTIMA_TANDA_RETIRADA'}
       )
    ; R = _{permitido:false, motivo:'RETIRO_NO_AUTORIZADO'}
    ).

resolver(D, R) :-
    ( entrada_valida(D) ->
        get_dict(accion, D, Accion),
        ( Accion == 'SIGUIENTE' -> siguiente(D, R)
        ; Accion == 'INICIAR'   -> iniciar(D, R)
        ; Accion == 'RETIRAR'   -> retirar(D, R)
        )
    ; R = _{accion:'ERROR', motivo:'ENTRADA_INVALIDA'}
    ).

% Entrada/Salida JSON para integracion desde Python, sin ejecutar codigo
% suministrado por usuarios. Comando: swipl -q -s reglas_turnos.pl -g main -t halt
main :-
    catch(
        ( json_read_dict(current_input, Peticion, [value_string_as(atom)]),
          resolver(Peticion, Respuesta)
        ),
        _,
        Respuesta = _{accion:'ERROR', motivo:'JSON_O_DATOS_INVALIDOS'}
    ),
    json_write_dict(current_output, Respuesta, [width(0)]), nl.
