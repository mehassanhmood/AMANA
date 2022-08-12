from os import curdir
import sqlite3
import globalvar as gbl
import streamlit as st
import hashlib
import sys

# -----------------------------------------------------------------
# Rotuine to process login 
# -----------------------------------------------------------------
def login(userName, password) -> bool:
    conn = db_connection()
    cur = conn.cursor()
    user_logged_in = get_user(cur, userName, hashes_pwd(password))
    # print(user_result, file=sys.stderr)
    if user_logged_in:
        bio_result = get_bio(cur, userName)
    # gbl.conn.close()
    return user_logged_in

# -----------------------------------------------------------------
# retrieve all user details from table - Users
# based on entered userID and password
# -----------------------------------------------------------------
def get_user(cur, user_id, pwd) -> bool:
    gbl.userData = ()
    qry = '''SELECT * from Users WHERE UserID = ? AND Password = ?'''
    cur.execute(qry, (user_id,pwd))
    user_data = cur.fetchone()
    #print(user_data, file=sys.stderr)

    if user_data is None:
        return False
    elif len(user_data) > 0:
        gbl.userData = user_data
        return True
    else:
        return False

# -----------------------------------------------------------------
# Retrieve all BioData details from table - BioData
# -----------------------------------------------------------------
def get_bio(cur, user_id) -> bool:
    gbl.bioData = ()
    qry = '''SELECT * from BioData WHERE UserID = ?'''
    cur.execute(qry, (user_id,))
    bio_data = cur.fetchone()
    if bio_data is None:
        return False
    elif len(bio_data) > 0:
        gbl.bioData = bio_data
        return True
    else:
        return False


# -----------------------------------------------------------------
# Change user password
# -----------------------------------------------------------------
def chg_pwd(user_id, pwd) -> bool:
    conn = db_connection()
    cur = conn.cursor()
    qry = '''Update Users set Password = ? WHERE UserID = ? '''
    qry1 = '''Select UserID From Users WHERE UserID = ? '''
    # print(qry, file=sys.stderr)
    # print(qry1, file=sys.stderr)
    usr = cur.execute(qry1, (user_id,)).fetchone()
    if usr is None:
        return False
    else:
        # print(usr, file=sys.stderr)
        cur.execute(qry, (hashes_pwd(pwd), user_id))
        conn.commit()
        return True

# -----------------------------------------------------------------
# Get all talents from table - BioData
# -----------------------------------------------------------------
def get_talents() -> str:
    gbl.talentData = []
    conn = db_connection()
    cur = conn.cursor()
    qry = '''SELECT DISTINCT AreaExpertise from BioData'''
    cur.execute(qry)
    talent_data = cur.fetchall()
    if talent_data is not None:
        if len(talent_data) > 0:
            gbl.talentData.append("Select")
            for i in range(len(talent_data)):
                t = ''.join(talent_data[i])
                gbl.talentData.append(t)
    return gbl.talentData

# -----------------------------------------------------------------
# Retrieve talents based on selected skills from table - BioData
# -----------------------------------------------------------------
def get_talents_users(skill) -> str:
    gbl.talentUser = []
    gbl.talentUserEmail = []
    conn = db_connection()
    cur = conn.cursor()
    qry = ('''SELECT UserID, FirstName, LastName from Users
              Where UserID IN (select UserID from biodata where areaexpertise = "?")''')
    qry = qry.replace("?", skill)
    cur.execute(qry)
    talent_user = cur.fetchall()
    if talent_user is not None:
        if len(talent_user) > 0:
            for i in range(len(talent_user)):
                t = ''.join(talent_user[i][1] + " " + talent_user[i][2])
                tt = ''.join(talent_user[i][0])
                gbl.talentUser.append(t)
                gbl.talentUserEmail.append(tt)
    return gbl.talentUser


# -----------------------------------------------------------------
# Retrieve talent's HASH from table BioData based on UserID and Skills selected
# -----------------------------------------------------------------
def get_talents_hash(mailID, skill) -> str:
    gbl.talentUserHash = []
    conn = db_connection()
    cur = conn.cursor()
    qry = ('''SELECT ServiceURI, Image, TokenID from BioData Where UserID = "1" and AreaExpertise = "2" ''')
    qry = qry.replace("1", mailID)
    qry = qry.replace("2", skill)
    cur.execute(qry)
    talent_user_hash = cur.fetchall()
    gbl.talentUserHash = talent_user_hash
    return gbl.talentUserHash[0]

# -----------------------------------------------------------------
# Retrieve available skills for the selected user
# -----------------------------------------------------------------
def get_talents_for_user(mailID) -> str:
    gbl.talenForUser = []
    conn = db_connection()
    cur = conn.cursor()
    qry = ('''SELECT AreaExpertise from BioData Where UserID = "?" ''')
    qry = qry.replace("?", mailID)
    # print(qry)

    cur.execute(qry)
    talent_for_user = cur.fetchall()
    if talent_for_user is not None:
        if len(talent_for_user) > 0:
            for i in range(len(talent_for_user)):
                t = ''.join(talent_for_user[i])
                gbl.talenForUser.append(t)
        # print(gbl.talenForUser)
    return gbl.talenForUser

# -----------------------------------------------------------------
# Get the tokenID from last record and increment by 1
# Return the tokenID
# -----------------------------------------------------------------
def get_tokenID():
    conn = db_connection()
    cur = conn.cursor()
    tokenid = 0
    token_id = cur.execute("SELECT tokenID FROM BioData ORDER BY rowid DESC LIMIT 1").fetchone()
    tokenid, *_ = token_id
    try:
        tokenid +=  1
    except:
        tokenid = 0
    return tokenid

# -----------------------------------------------------------------
# Check if user entered area of expertise exist in the database
# -----------------------------------------------------------------
def check_area_experty(area_exp):
    conn = db_connection()
    cur = conn.cursor()
    qry = '''SELECT AreaExpertise FROM BioData Where UserID = "1" and AreaExpertise = "2" '''
    qry = qry.replace("1", st.session_state.User)
    qry = qry.replace("2", area_exp)
    # print(qry, file=sys.stderr)
    areExp = cur.execute(qry).fetchone()
    # print(areExp, file=sys.stderr)
    if areExp is None:
        return False
    else:
        return True

# -----------------------------------------------------------------
# Insert new service record
# -----------------------------------------------------------------
def RegisterService(userID, areaExp, ServiceURI, TokenJason) -> str:
    DBerror = ""
    conn = db_connection()
    cur = conn.cursor()
    qry = '''INSERT INTO BioData (UserID, AreaExpertise, ServiceURI, Image) VALUES(?,?,?,?)'''
    # print(qry)
    
    try:
        with conn:                              # Commit is called automatically when no exceptions
            cur.execute(qry,                    # Create the user account
            (userID, areaExp, ServiceURI, TokenJason))   
    except sqlite3.Error as er:                 # On exception rollback is called automatically
        print(f"Error---> {er}")
        DBerror = er
    conn.close                                  # Close the connection
    return DBerror


# -----------------------------------------------------------------
# Create Freelancer records 
# -----------------------------------------------------------------
def create_user(accountData, bioData) -> str:
    conn = db_connection()
    cur = conn.cursor()
    DBerror = ""
    qry1 = '''INSERT INTO Users (FirstName, LastName, UserID, Password, Freelancer) VALUES(?,?,?,?,?)'''
    qry2 = '''INSERT INTO BioData (UserID, AreaExpertise) VALUES(?,?)'''
    qry3 = '''DELETE From freelancers Where UserID = ?'''

    try:
        with conn:                              # Commit is called automatically when no exceptions
            cur.execute(qry1, accountData)      # Create the user account
            cur.execute(qry2, bioData)          # Create biodata
    except sqlite3.Error as er:                 # On exception rollback is called automatically
        print(f"Error---> {er}", file=sys.stderr)
        DBerror = er
    conn.close                                  # Close the connection
    return DBerror


# -----------------------------------------------------------------
# Connect to SQlite3 database
# -----------------------------------------------------------------
def db_connection():
    conn=None
    try:
        conn = sqlite3.connect('data.db')
    except sqlite3.Error as e:
        print(f'Unable to connect - {e}', file=sys.stderr)
        return False

    return conn

# ---------------------------------------------------------------------------
# Hash the password
# ---------------------------------------------------------------------------
def hashes_pwd(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

