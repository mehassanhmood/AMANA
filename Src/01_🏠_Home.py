# Import neccessary libraries
import streamlit as st
import user as usr
import globalvar as gbl
import sys

try:
    st.set_page_config(page_title="Talent Search", page_icon="🧊", 
                       layout="centered", initial_sidebar_state="auto", menu_items=None)
except:
    pass

# hide_menu_style = """
#         <style>
#         #MainMenu {visibility: hidden; }
#         footer {visibility: hidden;}
#         </style>
#         """

# Remove the stremlit main and footer
hide_menu_style = """
        <style>
        #MainMenu {visibility: visible; }   
        footer {visibility: hidden;}       
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)  # Set the stremlit menu style

# Initialize all state variables
if not "initialized" in st.session_state:
    st.session_state.FirstTime = True      # Set state variables for login
    st.session_state.Register = False      # Set state variables for login
    st.session_state.loggedIn = False      # Set state variables for register
    st.session_state.Freelancer = False    # Set state variables for register
    st.session_state.chgd = False          # Set state variables for reset password
    st.session_state.User = ""             # Set state variables for logged in user id
    st.session_state.area_exp = ""         # Set state variables for area of expertise
    st.session_state.service_uri = ""      # Set state variables for service URI
    st.session_state.token_json = ""       # Set state variables for IPFS image
    st.session_state.token_id = ""         # Purchasing token id 
    st.session_state.selFreelancer = ""    # Selected freelancer's name
    st.session_state.initialized = True    # Set state variables to run this routine


# Create containers to be used within this app
# headerSection = st.container()
mainSection = st.container()
searchSection = st.container()
loginSection = st.container()
logoutSection = st.container()
pwdResetSection = st.container()
regSection = st.container()
sideBarSection = st.sidebar

class Freelancer_page:
    def __init__(self):
        self.freelancer_account = st.text_input("Enter Freelancer's Account Address: ", value="0x62348232954BC5399c217fBeDF8F11662c1D6873")
        self.area_exp = st.text_input("Enter the Area of expertise: ")
        self.level_exp = st.text_input("Enter the level of expertise: ")
        rate = st.number_input("Enter the Service Rate in USDT: ")
        init_token = st.number_input("Enter total number of taken needed: ")
        self.duration = st.text_input("Enter the time of completion in days: ")
        self.jobdesc = st.text_area("Job Describtion: ")
        self.rate = int(rate)
        self.init_token = int(init_token)

        # Upload a document
        self.file = st.file_uploader("Upload a document", type=None)



# ----------------------------------------------------------------
# About page
# ----------------------------------------------------------------
def about_page():
    st.markdown("<h1 style='text-align: center; color: lightblue;'>Welcomwe to AMANA</h1>", unsafe_allow_html=True)
    st.markdown("### A Web3 Freelance MarketPlace powered by BlockChain.")
    st.markdown("##### Post your skills, find a gig, get paid in crypto!")


# ---------------------------------------------------------------
# This is the main page that is displaied after successful login
# ---------------------------------------------------------------
def main_page(): 
    with mainSection:
        st.markdown("<h1 style='text-align: center; color: lightblue;'>Welcomwe to AMANA</h1>", unsafe_allow_html=True)
        st.markdown("### A Web3 Freelance MarketPlace powered by BlockChain.")
        st.markdown("##### Post your skills, find a gig, get paid in crypto!")
        

        if st.session_state.Freelancer:    # If the user is a Freelancer
            st.markdown("<p style='text-align: left; color: red;'>Available Skills</p>", unsafe_allow_html=True)
            placeholder = st.empty()
            placeholder2 = st.empty()
            num = 0

            with placeholder2:
                display_skils()

            st.markdown("""<p style='text-align: left; color: blue;'>To Register, 
                           choose register Sevice on left menu</p>""", unsafe_allow_html=True)
            
        # If the user is a client, process request neccessary for the client
        else:
            st.markdown("---")
            menu = usr.get_talents()              # Display available talents 
            st.selectbox("Available skills", menu, key="Sel")
            if st.session_state.Sel != "Select":  # Process the selected talent
                st.session_state.area_exp = st.session_state.Sel
                talent_user_sel()                 # Process the selection


def display_skils():
    skills = usr.get_talents_for_user(st.session_state.User)
    s = ''
    for i in skills:
        s += "- " + i + "\n"
    st.markdown(s)
    


# ---------------------------------------------------------------
# Display all talents to the user
# ---------------------------------------------------------------
def talent_user_sel():
    #if st.session_state.Sel != "Select":
        with searchSection:
            menu = usr.get_talents_users(st.session_state.Sel)      # Radio button values
            st.radio(label = 'Selection', options = menu, key="radio", horizontal=True)
            st.session_state.selFreelancer = st.session_state.radio
            ii = menu.index(st.session_state.radio)                 # Get the selected valu's index
            user_ID = gbl.talentUserEmail[ii]                       # Retrieve the email id based on index
            usr.get_talents_hash(user_ID, st.session_state.Sel)     # Rtv talent's hash
            st.session_state.token_id = gbl.talentUserHash[0][2]    # Store toekn id on session state
            st.write(f"Purchasing token id is {st.session_state.token_id}")
            srv = f"[Service image](https://{gbl.talentUserHash[0][1]})"
            token = f"[Detail](https://{gbl.talentUserHash[0][0]})"
            st.write(srv)
            st.write(token)
            # st.write("Use 'Purchase Service on the top sidebar' to purchase this service")
            st.markdown("""<p style='text-align: left; color: blue;'>To Register, 
                           Purchase Service on the top sidebar' to purchase this service</p>""", unsafe_allow_html=True)

        searchSection.empty()

# ---------------------------------------------------------------
# Logout page. Display the 'logout' button
# --------------------------------------------------------------- 
def logout_page():
    loginSection.empty()
    with sideBarSection:
        st.button("Log out", key="logout", on_click=loggedOut_clicked)

# ---------------------------------------------------------------
# If the 'Logout' button is pressed, this function is called
# Function is called to logoff the user
# ---------------------------------------------------------------                
def loggedOut_clicked():
    st.session_state.loggedIn = False 
    st.session_state.Freelancer = False
    st.session_state.User = ""

# ---------------------------------------------------------------
# Login main page
# --------------------------------------------------------------- 
def login_page():
    with loginSection:
        if st.session_state.loggedIn == False:
            userName = st.text_input("Enter Email Address")
            password = st.text_input("Enter password", type="password")
            st.button("Login", on_click=loggedIn_clicked, args=(userName, password))

# ---------------------------------------------------------------
# If the 'Login' button is pressed, this function is called to login
# --------------------------------------------------------------- 
def loggedIn_clicked(userName, password):
    userName = userName.upper()
    if usr.login(userName, password):
        st.session_state.loggedIn = True
        if len(gbl.userData) != 0:
            _, name, _, usrID, _, gbl.Freelancer = gbl.userData
            st.session_state.Freelancer = gbl.Freelancer
            st.session_state.User = usrID
            gbl.Title = (f"#### Welcome to Talent Search - {name}")
    else:
        st.session_state.loggedIn = False
        st.error("Invalid user name or password")

# ---------------------------------------------------------------
# Display change password page
# --------------------------------------------------------------- 
def chg_pwd_page():
    with pwdResetSection:
        userName1 = st.text_input("Enter User id")
        password1 = st.text_input("Enter New password", type="password")
        st.button("Change Password", on_click=Change_Password_clicked, args=(userName1, password1))

# ---------------------------------------------------------------
# Process reset password request when the "Change Password" is pressed
# --------------------------------------------------------------- 
def Change_Password_clicked(user_Name,pwd):
    changed = usr.chg_pwd(user_Name, pwd)
    # print(changed, file=sys.stderr)
    if not changed:
        st.error("Invalid user")
    else:
        st.session_state.chgd = True


# ---------------------------------------------------------------
# Register main page - Process registration of a user
# # --------------------------------------------------------------- 
def register_page():
    menu = ["Freelancer", "Client"]                    # Set user type selection box
    choice = st.sidebar.radio(label = 'User Type', options = menu, key="radio", horizontal=True)
    
    with regSection:
        area_expert = ""
        if st.session_state.loggedIn == False:
            user_ID = st.text_input("Email Address")                  # Get user id
            password = st.text_input("Password", type="password")     # Get password
            first_name = st.text_input("First Name")                  # Get First Name
            last_name = st.text_input("Last Name")                    # Get Last Name

            if choice == "Freelancer":                                # Processing for Freelancer selection
                userType = True
                area_expert = st.text_input("Area of Experties")
            else:                                                     # Processing for Client selection
                userType = False

            if st.button("Register"):
                # Make sure all fields are entered 
                if ((choice != "Freelancer" and                       # Condition for Client
                     (first_name == "" or last_name == "" or user_ID == "" or password == "" )) or
                    (choice == "Freelancer" and                       # Condition for Freelancer
                     (first_name == "" or last_name == "" or user_ID == "" or password == "" or area_expert == ""))
                   ):
                    st.error("You must fill all fields!")

                else:
                    user_ID = user_ID.upper()
                    act_dta = [first_name, last_name, user_ID, password, userType]     # Create the query paramenter
                    bio_dta = [user_ID, area_expert]                                   # Create the query paramenter
                    err = usr.create_user(act_dta, bio_dta)                            # Write to table Users

                    if err == "":
                        st.session_state.Register = True
                        st.sidebar.success("Registration is successfull")              # Display successful msg
                    else:
                        st.exception(f"Account is not acreated! {err}")                # Display any errors


# ---------------------------------------------------------------
# This is the main function called by Stremlit
# --------------------------------------------------------------- 
def main():
    with sideBarSection:                            # Display all the widgets in the sidebars
        name = ""
        menu = ["About", "Login", "Reset Password", "Register"]  # Set selectbox value
        choice = st.sidebar.selectbox("Menu", menu, index=1)     # Display the dropdown menu

    if choice == "About":                           # Process About page
        about_page()

    elif choice == "Login":                         # Process Login 
        if not st.session_state.loggedIn:           # If not logged in 
            login_page()                            # Display login page
        else:                                       # If logged in 
            main_page()                             # Display main page
            logout_page()                           # and log out page
    
    elif choice == "Reset Password":                # Process reset password
        chg_pwd_page()                              # Display reset password page
        if st.session_state.chgd:
            st.success('Password reset is successfull')

    elif choice == "Register":                      # Process Register if register is selected
        if st.session_state.loggedIn:               # Process Register if the user is not logged in
            st.markdown("""
                <h4 style='text-align: left; color: red;'
                >You must be logged off to register!</h4>""", unsafe_allow_html=True)
            logout_page()
        else:                                       # Process Registration
            register_page()                         # Display Registration page



if __name__ == '__main__':
    main()     # Function to process

