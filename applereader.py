"""
    Class supporting the creation of a simple API endpoint
"""
import os, json
from itertools import permutations
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from dotenv import load_dotenv

class AppleReader():
    def __init__(self):
        self.lstReturnedItems = list()
        d = dict()

        project_folder = os.path.expanduser('/users/brad/code/applereaderapi')  # ON SERVER: ~/applereaderapi
        load_dotenv(os.path.join(project_folder, '.env'))
        d = json.loads('{"type": "service_account","project_id": "applereadergsoc","client_email": "applereaderapi@applereadergsoc.iam.gserviceaccount.com","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/applereaderapi%40applereadergsoc.iam.gserviceaccount.com"}')

        # Secret stuff here ...
        d["client_id"] = os.getenv("CLIENTID")
        d["private_key_id"] = os.getenv("PRIVATEKEYID")
        s = os.getenv("PRIVATEKEY")
        s = s.replace('\\n', '\n')
        d["private_key"] = s

        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/firebase.database"
        ]
        try:
            credentials = service_account.Credentials.from_service_account_info(d, scopes=scopes)
        except:
            print("something went wrong with firebase credentials")
        else:
            self.authed_session = AuthorizedSession(credentials)

        del d

        return

    def __del__(self):
        del self.authed_session
        del self.lstReturnedItems

        return

    def __getFirebaseUsernames(self):
        """
            input: none
            output: returns a list of the current usernames within the database
        """
        lstReturnThis = list()

        url = "https://applereadergsoc-default-rtdb.firebaseio.com/users.json"
        response = self.authed_session.get(url)
        self.firebaseConfig = json.loads(response.text)
        print(self.firebaseConfig)
        for values in self.firebaseConfig.values():
            lstReturnThis.append(values["username"])

        return lstReturnThis

    def getFirebaseKeys(self, child, username):
        """
            input: child (e.g. library, user), username as strings
            output: list of the database items beneath child filtered for that username
        """
        self.lstReturnedItems = list()   # you need to refresh this
        if child and username:
            url = 'https://applereadergsoc-default-rtdb.firebaseio.com/{}.json?orderBy="username"&equalTo="{}"'.format(child, username)

            response = self.authed_session.get(url)
            self.firebaseConfig = json.loads(response.text)
            for keys in self.firebaseConfig.keys():
                self.lstReturnedItems.append(keys)

        return json.dumps(self.lstReturnedItems)


    def getUserName(self, items):
        """
            input: comma delimited list of strings (can be numeric)
            output: dictionary with single element key "items" with whose value is a list of all the
            permutations of the input items
        """
        # print("GET items coming in: {}".format(items))
        d = dict()
        self.lstReturnedItems = list()
        d["items"] = self.lstReturnedItems

        if items:

            lstCurrentUsers = self.__getFirebaseUsernames()
            print(lstCurrentUsers)

            lstItemsIn = items.split(",")
            if len(lstItemsIn) > 0:
                end = len(lstItemsIn) + 1
                for cnt in range(2, end):
                    lstHolder = list()
                    perm = permutations(lstItemsIn, cnt)
                    lstHolder.extend(list(perm))
                    for item in lstHolder:
                        lstUserName = list()
                        for subitem in item:
                            lstUserName.append(subitem)
                        self.lstReturnedItems.append(''.join(lstUserName))

            # d["items"] = self.lstReturnedItems
            # filter out usernames that are already within the database ..
            d["items"] = [x for x in self.lstReturnedItems if x not in lstCurrentUsers]

        return d

if __name__ == '__main__':
    """
        Some testing going on here ...
    """
    obj = AppleReader()
    print("RETURNING items: {}".format(obj.getUserName("one,two,three,four")))
