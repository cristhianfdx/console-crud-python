# -*- coding=utf-8 -*-

'''
@author: Cristhian Alexander Forero
'''

import sqlite3
import os
import re

db_name = 'students.db'

def print_menu():
    print('''
        OPERACIONES BÁSICAS CON SQLITE

        1. Crear Base de Datos.
        2. Crear tabla.
        3. Insertar datos en la tabla.
        4. Consultar todos los registros de la tabla.
        5. Eliminar tabla.
        6. Actualizar registro de la tabla.
        7. Buscar un registro.
        8. Eliminar un registro.
        9. Restaurar tabla eliminada.
        10. Salir.
    ''')


def create_database():
    if is_database_exists():
        print('{} ya existe! :/'.format(db_name))
    else:
        connection = sqlite3.connect(db_name)
        connection.close()
        print('{} se creó correctamente •ᴗ•'.format(db_name))


def create_table():
    query = '''
        CREATE TABLE estudiante (
            doc INT UNIQUE,
            nombre VARCHAR(40),
            fecha DATE,
            genero VARCHAR(1)
        )
        '''
    if are_valid_rules(create_table=True):
        execute_query(query)
        print('''La tabla ha sido creada •ᴗ• con la siguiente estructura:
            {}'''.format(query))


def insert_data_table():
    save_table_data()


def get_all_data():
    if not are_valid_rules(): return

    query = 'SELECT * FROM estudiante'
    result = execute_query(query).fetchall()

    if result:
        print('\nRegistros:')
        print('--------------------------------------')
        for row in result:
            print(row)
        print('--------------------------------------')
    else:
        print('La tabla no tiene registros :(')


def drop_table():
    if not are_valid_rules(): return
    question = get_input_question('eliminar la tabla')

    if is_run_again(question):
        print('La tabla no fue eliminada :)')
        return

    save_table_backup()
    result = execute_query(query='DROP TABLE estudiante')

    if result is not None:
        print('La tabla ha sido eliminada :(')
        print('Se ha guardado una copia de la tabla estudiante :)')


def update_one():
    save_table_data(is_editable=True)


def find_one():
    while True:
        if not are_valid_rules(): break
        option = get_find_option()

        if option == '1':
            document_number = int(input('\nIngrese el número de documento: '))
            result = get_by_field_and_parameter('doc', parameter=document_number)
            if result: print('Resultado: {}'.format(result))
        elif option == '2':
            name = get_insert_name()
            result = get_by_field_and_parameter('nombre', parameter=name)
            if result: print('Resultado: {}'.format(result))
        elif option == '3':
            date = get_valid_date()
            result = get_by_field_and_parameter('fecha', parameter=date)
            if result: print('Resultado: {}'.format(result))
        elif option == '4': return
        else: print('Opción incorrecta.')

        question = get_input_question('buscar otro registro')
        if is_run_again(question): break


def delete_one():
    if not are_valid_rules(): return
    print('Buscar usuario por número de documento.\n')
    document_number = int(input('\nIngrese el número de documento: '))
    student = get_by_field_and_parameter(field='doc', parameter=document_number)
    if student is None: return
    print('Usuario encontrado:\n', student, '\n')
    question = get_input_question('eliminar el registro')
    if not is_run_again(question):
        execute_query(query='DELETE FROM estudiante WHERE doc=?', parameters=(student[0],))
        print('Se ha eliminado el registro :(')
    else:
        print('No se ha eliminado el registro :)')


def restore_table():
    question = get_input_question('generar el backup')
    if is_run_again(question):
        print('No se ha restaurado la tabla :( \n')
        return
    if is_table_exists(is_main=False):
        execute_query(query='DROP TABLE IF EXISTS estudiante')
        execute_query(query='CREATE TABLE estudiante AS SELECT * FROM backup')
        print('Se ha restaurado la tabla estudiante :) \n')
        execute_query('DROP TABLE IF EXISTS backup')
        print('La tabla de respaldo ha sido eliminada :/ \n')
    else:
        print('No existe copia de respaldo :( \n')


def save_table_data(is_editable=False):
    while True:
        data = None
        query = ''

        if not are_valid_rules(): break

        if is_editable:
            data = get_valid_save_data(is_editable=True)
            query = '''
                UPDATE estudiante
                SET doc=?, nombre=?, fecha=?, genero=?
                WHERE doc=?
            '''
        else:
            data = get_valid_save_data()
            query = 'INSERT INTO estudiante VALUES (?,?,?,?)'

        if data is None: break
        result = execute_query(query=query, parameters=data)
        if result is not None: print('\nRegistro guardado correctamente •ᴗ•')

        action = 'guardar' if not is_editable else 'actualizar'
        question = get_input_question('{} más registros'.format(action))
        if is_run_again(question): break


def save_table_backup():
    execute_query('DROP TABLE IF EXISTS backup')
    execute_query('CREATE TABLE backup AS SELECT * FROM estudiante')


def get_selected_option(option):
    options = {
        '1' : 'create_database',
        '2' : 'create_table',
        '3' : 'insert_data_table',
        '4' : 'get_all_data',
        '5' : 'drop_table',
        '6' : 'update_one',
        '7' : 'find_one',
        '8' : 'delete_one',
        '9' : 'restore_table'
    }
    return options.get(option)

def get_valid_save_data(is_editable=False):
    student = None
    data = ()

    if is_editable:
        print('Se encuentra en el modo de edición de datos.\n')
        print('Buscar usuario por número de documento.\n')
        document_number = int(input('Ingrese el número de documento: '))
        student = get_by_field_and_parameter(field='doc', parameter=document_number)
        if student is None: return
        print('Usuario encontrado:\n', student, '\n')
        question = get_input_question('actualizar el nombre')
        name = get_insert_name() if not is_run_again(question) else student[1]
        question = get_input_question('actualizar la fecha')
        date = get_valid_date() if not is_run_again(question) else student[2]
        question = get_input_question('actualizar el género')
        gender = get_valid_gender() if not is_run_again(question) else student[3]
        data = (document_number, name, date, gender,) + (document_number,)
    else:
        print('Por favor ingrese los datos.\n')
        document_number = get_valid_document_number()
        name = get_insert_name()
        date = get_valid_date()
        gender = get_valid_gender()
        data = (document_number, name, date, gender,)
    return data


def function_execute():
    while True:
        option = input('Ingrese la opción deseada: ')
        func_name = get_selected_option(option)
        if func_name is not None:
            globals()[func_name]()
        else:
            if option == '10':
                print('(ʘ‿ʘ)╯ Bye....')
                break
            print('Opción incorrecta.')

        input_value = get_input_question('ejecutar otra operación')
        if is_run_again(input_value):
            print('Bye....')
            break
        print_menu()


def execute_query(query, parameters=()):
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        result = cursor.execute(query, parameters)
        connection.commit()
    return result


def are_valid_rules(create_table=False):
    is_valid = True
    if not is_database_exists():
        print('La base de datos no existe :(')
        return
    if not is_table_exists() and not create_table:
        print('La tabla estudiante no existe : (')
        return
    if create_table and is_table_exists():
        print('La tabla estudiante ya existe : (')
        return
    return is_valid


def is_database_exists():
    return os.path.isfile(db_name)


def is_table_exists(is_main=True):
    if not is_database_exists():
        print('La base de datos no existe :(')
        return
    table_name = 'estudiante' if is_main else 'backup'
    return execute_query('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?''',
        parameters=(table_name,)).fetchone()[0] == 1


def get_valid_document_number():
    input_document_number_message = 'Ingrese el número de documento: '
    document_number = int(input(input_document_number_message))
    query = 'SELECT * FROM estudiante WHERE doc=?'.format(document_number)
    student = execute_query(query, (document_number,)).fetchone()

    while student is not None:
        print('Ya existe un usuario con ese número de documento.')
        document_number = int(input(input_document_number_message))
        student = get_by_field_and_parameter(field='doc', parameter=document_number)
    return document_number


def get_by_field_and_parameter(field, parameter):
    if are_valid_rules():
        query = ''
        result = None

        if field == 'nombre':
            query = "SELECT * FROM estudiante WHERE {} LIKE ?".format(field)
            result = execute_query(query, ('%'+parameter+'%',))
        else:
            query = 'SELECT * FROM estudiante WHERE {} =?'.format(field)
            result = execute_query(query, (parameter,))
        data = result.fetchone()
        if data is None:
            print('No se encuentra el usuario por el parámetro {} :('.format(parameter))
        else:
            return data


def get_input_question(message):
    return input('\n¿Desea {}? s/n: '.format(message))


def is_run_again(option=''):
    return option.lower() != 's'


def get_insert_name():
    return input('Ingrese el nombre: ').upper()


def get_valid_date():
    input_date_message = 'Ingrese la fecha  (DD/MM/AAAA): '
    date_regex = r'^\d{1,2}\/\d{1,2}\/\d{4}$'

    date = input(input_date_message)
    while not re.match(date_regex, date):
        print('Formato de fecha inválido.')
        date = input(input_date_message)

    return date


def get_valid_gender():
    input_gender_message = 'Ingrese género (m/f/otro): '

    gender = input(input_gender_message)
    while is_valid_gender(gender):
        print('Formato de género inválido.')
        gender = input(input_gender_message)

    return gender.upper()


def is_valid_gender(gender):
    return not gender == 'm' and not gender == 'f' and not gender == 'otro'

def get_find_option():
    return input('''
        BÚSQUEDA DE REGISTROS
        1. Buscar por número de documento.
        2. Buscar por nombre
        3. Buscar por fecha.
        4. Cancelar

        Ingrese la opción deseada: ''')

def run():
    print_menu()
    function_execute()


if __name__ == '__main__':
    run()
