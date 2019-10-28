import tableauserverclient

SECRET_KEY = "secret key"

TABLEAU_AUTH = tableauserverclient.TableauAuth('userWithAccessToServer', 'passwordOfUser')

USERS_LIST = ["user1", "user2", "user3", "user4"] #Users who have the access to the dashboard
PASSWORD_LOGIN = "usersPassword"