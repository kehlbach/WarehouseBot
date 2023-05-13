from requests import Session

from app.data import constants


class Database:
    def __init__(self, url: str, login: str, password: str):
        self.URL = url
        self.session = Session()
        self.session.auth = (login, password)
        self.DEPARTMENTS = 'departments'
        self.ROLES = 'roles'
        self.ROLE_PERMISSIONS = 'role_permissions'
        self.PROFILES = 'profiles'
        self.CATEGORIES = 'categories'
        self.PRODUCTS = 'products'
        self.RECEIPTS = 'receipts'
        self.RECEIPT_PRODUCTS = 'receipt_products'
        self.INVENTORY = 'inventory'
        self.SUBJECTS = 'subjects'
        self.ACTIONS = 'actions'
        self.SUBJECT = {
            constants.DEPARTMENTS: self.DEPARTMENTS,
            constants.ROLES: self.ROLES,
            constants.PROFILES: self.PROFILES,
            constants.CATEGORIES: self.CATEGORIES,
            constants.PRODUCTS: self.PRODUCTS,
            constants.RECEIPTS: self.RECEIPTS,
            constants.INVENTORY: self.INVENTORY
        }
        self._permissions = {}

    def get(self, subject: str, id: int = '') -> dict | list[dict]:
        """
        Get all entities by subject: 
        >>> db.get(db.PROFILES)

        Get entity by id: 
        >>> db.get(db.PROFILES,data['id'])
        """
        url = f'{self.URL}/{subject}'
        if id or subject in ['actions', 'subjects']:
            url += f'/{id}'
            response = self.session.get(url)
            if response.status_code == 404:
                return []
            return response.json()
        else:
            result = []
            next = True
            while next:
                response = self.session.get(url).json()
                if 'results' in response.keys():
                    result = result + response['results']
                else:
                    result = response
                    next = False
                next = bool(response['next'])
                url = response['next']
            return result

    def add(self, _subject, **data) -> dict:
        """usage examples:
        >>> data = {'name':..}; db.add(subject=db.PROFILES, **data)
        >>> db.add(subject=db.PROFILES,name='..',..)"""
        response = self.session.post(f'{self.URL}/{_subject}/', data=data)
        response = response.json()
        return response

    def edit_put(self, subject, object, **data) -> dict:
        """For operations with ManyToMany, as patch cannot set None for them"""
        # response = self.session.put(f'{self.URL}/{table}/{id}/', data=data)
        for key, value in data.items():
            object[key] = value
        response = self.session.put(
            f'{self.URL}/{subject}/{object["id"]}/', data=object)
        response = response.json()
        return response

    def edit_patch(self, subject, id, **data) -> dict:
        """For anything except ManyToMany.

        Examples:
        >>> db.edit_patch(db.PROFILES, id, name = "abc"..)

        or
        >>> data = {name: "abc"..}

        >>> db.edit_patch(db.PROFILES, id, **data)
        """
        response = self.session.patch(
            f'{self.URL}/{subject}/{id}/', data=data)
        response = response.json()
        return response

    def delete(self, subject, id):
        response = self.session.delete(f'{self.URL}/{subject}/{id}/')
        response = response
        return response

    def filter(self, _subject, **conditions) -> list[dict] | dict:
        """usage:
        >>> db.filter('profiles',phone_number='+77479309084')"""
        url = f'{self.URL}/{_subject}/?'
        for field, value in conditions.items():
            value = str(value).replace('+', r'%2B')
            url += f'{field}={value}&'
        response = self.session.get(url)
        if 'Select a valid choice' in str(response.json()):
            return []
        result = response.json()['results']
        if len(result) == 1:
            return response.json()['results'][0]
        else:
            return response.json()['results']

    def get_page(self, subject, page='1'):
        url = f'{self.URL}/{subject}/?page={page}'
        response = self.session.get(url).json()
        return response

    def next_page(self, response):
        next = response['next']
        response = self.session.get(next).json()
        return response

    def prev_page(self, response):
        previous = response['previous']
        response = self.session.get(previous).json()
        return response
