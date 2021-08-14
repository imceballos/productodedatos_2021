"""OneClick Interface"""

class OneClick():

    def get_user_reference(self, data: []) -> str:
        pass

    def get_detail_reference(self, data: []) -> []:
        pass

    def retrieve_stored_details(self, user_reference: str) -> []:
        pass

    def update_stored_details(self, user_reference: str) -> bool:
        pass

    def delete_stored_details(self, user_reference: str, recurring_detail_reference: str) -> bool:
        pass