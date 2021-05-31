import mysql.connector
from mysql.connector import Error
import pandas as pd


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def in_table(connection, table_name, id):
    try:
        #SELECT DISTINCT 1 FROM User WHERE idUser=\"id test\"
        return execute_query(connection, "SELECT DISTINCT 1 FROM User WHERE idUser=" + str(id) + ";")
    except Error as err:
        print(f"Error: '{err}'")
        return None
    # return execute_query(connection, "SELECT DISTINCT 1 FROM " + table_name + " WHERE id_user=" + str(id))


def add_user(connection, id_user):
    try:
        execute_query(connection, "INSERT INTO User (idUser, language) VALUES(" + str(id_user) + ", en)")
        print(str(id_user) + "add with success")
    except Error as err:
        print(f"Error: '{err}'")


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


if __name__ == '__main__':
    # connection = create_server_connection("localhost", "root", "Margaux0!")
    connection = create_db_connection("localhost", "root", "Margaux0!", "cineBot")

    # execute_query(connection, "CREATE DATABASE cineBot")
    execute_query(connection, "CREATE TABLE User(idUser varchar(30), language varchar(30))")
    print(connection)
