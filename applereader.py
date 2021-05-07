"""
    Class supporting the creation of a simple API endpoint
"""
import os, datetime, requests, json
from itertools import permutations
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from dotenv import load_dotenv

class AppleReader():
    def __init__(self):
        self.server_root = os.path.dirname(os.path.abspath(__file__))
        self.lstReturnedItems = list()
        d = dict()

        project_folder = os.path.expanduser(self.server_root)  # ON WEB SERVER: ~/applereaderapi
        load_dotenv(os.path.join(project_folder, '.env'))
        d = json.loads('{"type": "service_account","project_id": "applereadergsoc","client_email": "applereadergsoc@applereadergsoc.iam.gserviceaccount.com","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/applereadergsoc%40applereadergsoc.iam.gserviceaccount.com"}')

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
        del self.server_root

        return

    def __getUsernameProperty(self, username, property):
        """
            input: username and property (e.g. avatarImage) that you want from this user
            output: the property as a string
        """
        strAvatarURL = ""

        lstKeys = json.loads(self.getFirebaseKeys("users", username))  # should return only one key
        if lstKeys:
            url = "https://applereadergsoc-default-rtdb.firebaseio.com/users/{}.json".format(lstKeys[0])
            d = self.__getDictFromEndpoint(url, lstKeepTheseKeys=[property])
            if property in d:
                strAvatarURL = d[property]

        return strAvatarURL

    def __getDictFromEndpoint(self, urlEndPoint, lstKeepTheseKeys=[]):
        """
            input: key into Firebase that has a dictionary endpoint
            output: dictionary with the endpoint contents, or subset to the keys in lstKeepTheseKeys
        """
        d = dict()

        response = self.authed_session.get(urlEndPoint)
        d = json.loads(response.text)
        lstAllKeys = d.keys()
        lstRemoveTheseKeys = [x for x in lstAllKeys if x not in lstKeepTheseKeys]
        [d.pop(key) for key in lstRemoveTheseKeys]

        return(d)

    def __libraryActivelyReading(self, lstLibraryKeys):
        """
            input: lstLibraryKeys
            output: subset list of the lstLibraryKeys containing lastChapter > 0
        """
        lstReturnThis = list()
        lstToReview = json.loads(lstLibraryKeys)

        for key in lstToReview:
            url = "https://applereadergsoc-default-rtdb.firebaseio.com/library/{}.json".format(key)
            response = self.authed_session.get(url)
            self.firebaseConfig = json.loads(response.text)
            if "lastChapter" in self.firebaseConfig and self.firebaseConfig["lastChapter"] > 0:
                lstReturnThis.append(key)

        return lstReturnThis

    def __getFirebaseActivities(self):
        """
            input: none
            output: returns a list of the keys of the current activities within the database
        """
        lstReturnThis = list()

        url = "https://applereadergsoc-default-rtdb.firebaseio.com/activities.json"
        response = self.authed_session.get(url)
        self.firebaseConfig = json.loads(response.text)
        for keys in self.firebaseConfig.keys():
            lstReturnThis.append(keys)

        return lstReturnThis

    def __getFirebaseUsernames(self):
        """
            input: none
            output: returns a list of the current usernames within the database
        """
        lstReturnThis = list()

        url = "https://applereadergsoc-default-rtdb.firebaseio.com/users.json"
        response = self.authed_session.get(url)
        self.firebaseConfig = json.loads(response.text)
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
            # print(lstCurrentUsers)

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
            d["items"] = sorted([x for x in self.lstReturnedItems if x not in lstCurrentUsers])

        return d

    def getFirebaseActivities(self, username):
        """
            input: username of current user
            output: list of Activities keys
        """
        # return the books within the user's library that they were actively reading when added to the library
        lstLibrary = self.__libraryActivelyReading(self.getFirebaseKeys("library", username))
        lstActivities = self.__getFirebaseActivities()  # get all of the activity keys
        lstItemsToAdd = [x for x in lstLibrary if x not in lstActivities]  # keys to add to activities

        # print("lstLibrary: {}".format(lstLibrary))
        # print("lstActivities: {}".format(lstActivities))
        # print("lstItemsToAdd: {}".format(lstItemsToAdd))

        # now write the new library items as activity items before returning all activities
        for key in lstItemsToAdd:
            url = "https://applereadergsoc-default-rtdb.firebaseio.com/{}/{}.json".format("library", key)
            d = self.__getDictFromEndpoint(url, lstKeepTheseKeys=["author", "title", "coverImage", "lastChapter", "username"])
            if d:
                d["datetime"] = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
                d["emojiText"] = ""
                d["tagText"] = ""
                d["avatarImage"] = self.__getUsernameProperty(username, "avatarImage")
                url = "https://applereadergsoc-default-rtdb.firebaseio.com/{}/{}.json".format("activities", key)
                response = self.authed_session.put(url, json=d)
                # response.status_code should equal 200 or its an error on write !
                # didn't engineer a way of returning errors on list returns outside of an empty list

        return json.dumps(self.__getFirebaseActivities())  # refetch the keys after the update that occurred above

    def getBookDetail(self, typeparam, parameter):
        """
            input: type of parameter (intitle, inauthor, insubject, or isbn)
            parameter: title, author or subject with '+' delimiters (like "fuzzy+logic") or 13digit ISBN
            output: dictionary with element key "items" with attributes of the book detail we want.
            element key "error" returns either "ok" or an error message to display.  Items contains a list of books.
        """
        d = dict()
        d["error"] = "ok"
        self.lstReturnedItems = list()
        d["items"] = self.lstReturnedItems
        isbn13Code = ""
        nbrItemsToReturn = 10  # choosing to limit the amount of data returned

        if (typeparam and (typeparam == "intitle" or typeparam == "inauthor" or typeparam == "insubject" or typeparam == "isbn")):
            if (parameter and type(parameter) == str and len(parameter) > 4):
                nNbrReturned = 0
                response = requests.get("https://www.googleapis.com/books/v1/volumes?q={}:{}".format(typeparam, parameter))
                if response.status_code == 200:
                    objResponse = json.loads(response.text)
                    if objResponse["totalItems"] > 0:
                        lstBooks = objResponse["items"]
                        # would need a loop here of number of totalItems - think through returned structure - a list?
                        for items in lstBooks:
                            if nNbrReturned > nbrItemsToReturn:
                                break
                            else:
                                nNbrReturned += 1
                            itemBook = items["volumeInfo"]
                            bookDict = dict()
                            bookDict["coverImage"] = "https://img.icons8.com/cute-clipart/64/000000/nothing-found.png"
                            if "imageLinks" in itemBook.keys():
                                bookDict["coverImage"] = itemBook["imageLinks"]["thumbnail"]
                            bookDict["title"] = itemBook["title"]
                            bookDict["author"] = "none listed"
                            if "authors" in itemBook.keys():
                                bookDict["author"] = itemBook["authors"][0]
                            bookDict["readingLevel"] = -1
                            """
                                get the ISBN13 to use in the lexile API call
                            """
                            if "industryIdentifiers" in itemBook.keys():
                                lstIdentifiers = itemBook["industryIdentifiers"]
                                for item in lstIdentifiers:
                                    if item["type"] == "ISBN_13":
                                        isbn13Code = item["identifier"]

                            if (len(isbn13Code) > 10):
                                response = requests.get("http://GirlScouts_LexileAPI:Lexile_2021@fabapi.lexile.com/api/fab/v3/book/?format=json&ISBN13={}".format(isbn13Code))
                                if response.status_code == 200:
                                    objResponse = json.loads(response.text)
                                    if objResponse["meta"]["total_count"] > 0:
                                        lstBooks = objResponse["objects"]
                                        itemBook = lstBooks[0]
                                        if "lexile" in itemBook:
                                            bookDict["readingLevel"] = itemBook["lexile"]

                            self.lstReturnedItems.append(bookDict)
                    else:
                        d["error"] = "no books found with parameters {}, {}".format(typeparam, parameter)
                else:
                    d["error"] = "response error with parameters {}, {}".format(typeparam, parameter)
        return d

if __name__ == '__main__':
    """
        Some testing going on here ...
    """
    obj = AppleReader()
    # print("RETURNING items: {}".format(obj.getUserName("proud,yellow,worm,37")))
    # print("Returning items: {}".format(obj.getFirebaseActivities("proudyellowworm")))
    print("Returning items: {}".format(obj.getFirebaseActivities("sleepypurpleturtle")))

    # isbn code that is in both google and lexile: 9780451526342
    # isbn code only in google: 9780671738433
    # print("Returning items: {}".format(obj.getBookDetail("isbn", "9780451526342")))
